from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.models.approval_step import ApprovalStep, ApprovalStepStatus
from backend.src.models.document import Document, DocumentStatus


class ApprovalWorkflowError(RuntimeError):
    """Base class for approval workflow rule violations."""


class DocumentNotFoundError(ApprovalWorkflowError):
    """Raised when a document cannot be found."""


class StepNotFoundError(ApprovalWorkflowError):
    """Raised when an approval step cannot be found."""


class AuthorizationError(ApprovalWorkflowError):
    """Raised when an approver is not allowed to act on a step."""


class ApproverMismatchError(AuthorizationError):
    """Raised when a step is acted on by a different approver."""


class InvalidStepTransitionError(ApprovalWorkflowError):
    """Raised when a step transition is not allowed."""


class StepOutOfOrderError(ApprovalWorkflowError):
    """Raised when attempting to act on a step out of order."""


class DocumentStateError(ApprovalWorkflowError):
    """Raised when the document status blocks the requested action."""


class Decision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


@dataclass(frozen=True)
class ApprovalResult:
    document: Document
    step: ApprovalStep


def decide_step(
    session: Session,
    *,
    document_id: uuid.UUID,
    step_id: uuid.UUID,
    approver_id: uuid.UUID,
    decision: Decision,
) -> ApprovalResult:
    document = _load_document(session, document_id)
    if document.status != DocumentStatus.PENDING:
        raise DocumentStateError(
            f"Document {document_id} is {document.status} and cannot be changed."
        )

    step = _load_step(session, step_id, document_id, approver_id)
    steps = _load_steps(session, document_id)
    _ensure_step_order(steps, step)
    _ensure_step_pending(step)

    if decision == Decision.APPROVE:
        step.status = ApprovalStepStatus.APPROVED
        if _all_steps_approved(steps, step):
            document.status = DocumentStatus.APPROVED
    elif decision == Decision.REJECT:
        step.status = ApprovalStepStatus.REJECTED
        document.status = DocumentStatus.REJECTED
    else:
        raise InvalidStepTransitionError(f"Unsupported decision: {decision}")

    return ApprovalResult(document=document, step=step)


def approve_step(
    session: Session,
    *,
    document_id: uuid.UUID,
    step_id: uuid.UUID,
    approver_id: uuid.UUID,
) -> ApprovalResult:
    return decide_step(
        session,
        document_id=document_id,
        step_id=step_id,
        approver_id=approver_id,
        decision=Decision.APPROVE,
    )


def reject_step(
    session: Session,
    *,
    document_id: uuid.UUID,
    step_id: uuid.UUID,
    approver_id: uuid.UUID,
) -> ApprovalResult:
    return decide_step(
        session,
        document_id=document_id,
        step_id=step_id,
        approver_id=approver_id,
        decision=Decision.REJECT,
    )


def _load_document(session: Session, document_id: uuid.UUID) -> Document:
    document = session.get(Document, document_id)
    if document is None:
        raise DocumentNotFoundError(f"Document {document_id} was not found.")
    return document


def _load_step(
    session: Session,
    step_id: uuid.UUID,
    document_id: uuid.UUID,
    approver_id: uuid.UUID,
) -> ApprovalStep:
    step = session.get(ApprovalStep, step_id)
    if step is None or step.document_id != document_id:
        raise StepNotFoundError(
            f"Step {step_id} does not belong to document {document_id}."
        )
    if step.approver_id != approver_id:
        raise ApproverMismatchError(
            f"Step {step_id} cannot be updated by approver {approver_id}."
        )
    return step


def _load_steps(session: Session, document_id: uuid.UUID) -> list[ApprovalStep]:
    statement = (
        select(ApprovalStep)
        .where(ApprovalStep.document_id == document_id)
        .order_by(ApprovalStep.step_order)
    )
    return list(session.scalars(statement))


def _ensure_step_pending(step: ApprovalStep) -> None:
    if step.status != ApprovalStepStatus.PENDING:
        raise InvalidStepTransitionError(
            f"Step {step.id} is already {step.status}."
        )


def _ensure_step_order(steps: list[ApprovalStep], target: ApprovalStep) -> None:
    for step in steps:
        if step.step_order >= target.step_order:
            continue
        if step.status == ApprovalStepStatus.REJECTED:
            raise DocumentStateError(
                f"Document already rejected at step {step.id}."
            )
        if step.status != ApprovalStepStatus.APPROVED:
            raise StepOutOfOrderError(
                f"Step {target.id} cannot be processed before step {step.id}."
            )

    pending_orders = [step.step_order for step in steps if step.status == ApprovalStepStatus.PENDING]
    if not pending_orders:
        raise InvalidStepTransitionError("No pending steps remain.")
    if target.step_order != min(pending_orders):
        raise StepOutOfOrderError(
            f"Step {target.id} is not the next pending approval."
        )


def _all_steps_approved(steps: list[ApprovalStep], target: ApprovalStep) -> bool:
    for step in steps:
        if step.id == target.id:
            continue
        if step.status != ApprovalStepStatus.APPROVED:
            return False
    return True
