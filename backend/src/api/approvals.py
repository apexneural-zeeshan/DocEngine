import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.src.api.dependencies import get_current_user
from backend.src.db.session import get_session
from backend.src.models.approval_step import ApprovalStepStatus
from backend.src.models.document import DocumentStatus
from backend.src.models.user import User
from backend.src.services import approval_service

router = APIRouter(prefix="/documents/{document_id}/steps", tags=["approvals"])


class ApprovalDecisionRequest(BaseModel):
    approver_id: uuid.UUID


class ApprovalStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    approver_id: uuid.UUID
    step_order: int
    status: ApprovalStepStatus


class DocumentSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    status: DocumentStatus
    created_at: datetime


class ApprovalResponse(BaseModel):
    document: DocumentSummaryResponse
    step: ApprovalStepResponse


def _map_domain_error(error: Exception) -> HTTPException:
    if isinstance(error, approval_service.DocumentNotFoundError):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, approval_service.StepNotFoundError):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, approval_service.AuthorizationError):
        return HTTPException(status_code=403, detail=str(error))
    if isinstance(error, approval_service.ApproverMismatchError):
        return HTTPException(status_code=403, detail=str(error))
    if isinstance(error, approval_service.DocumentStateError):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, approval_service.InvalidStepTransitionError):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, approval_service.StepOutOfOrderError):
        return HTTPException(status_code=409, detail=str(error))
    return HTTPException(status_code=400, detail="Invalid approval request.")


@router.post("/{step_id}/approve", response_model=ApprovalResponse)
def approve_step(
    document_id: uuid.UUID,
    step_id: uuid.UUID,
    payload: ApprovalDecisionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApprovalResponse:
    try:
        result = approval_service.approve_step(
            session,
            document_id=document_id,
            step_id=step_id,
            approver_id=payload.approver_id,
        )
    except approval_service.ApprovalWorkflowError as error:
        raise _map_domain_error(error) from error
    return ApprovalResponse(document=result.document, step=result.step)


@router.post("/{step_id}/reject", response_model=ApprovalResponse)
def reject_step(
    document_id: uuid.UUID,
    step_id: uuid.UUID,
    payload: ApprovalDecisionRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApprovalResponse:
    try:
        result = approval_service.reject_step(
            session,
            document_id=document_id,
            step_id=step_id,
            approver_id=payload.approver_id,
        )
    except approval_service.ApprovalWorkflowError as error:
        raise _map_domain_error(error) from error
    return ApprovalResponse(document=result.document, step=result.step)
