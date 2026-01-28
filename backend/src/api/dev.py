from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from backend.src.models.user import User
from backend.src.core.security import get_password_hash

router = APIRouter(prefix="/dev", tags=["dev"])

@router.post("/create-user")
def create_user(email: str, password: str, session: Session = Depends(get_session)):
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": str(user.id), "email": user.email}
