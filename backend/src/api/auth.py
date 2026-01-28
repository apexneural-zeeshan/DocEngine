from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from backend.src.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


def _map_auth_error(error: Exception) -> HTTPException:
    if isinstance(error, auth_service.UserNotFoundError):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, auth_service.InvalidCredentialsError):
        return HTTPException(status_code=401, detail=str(error))
    if isinstance(error, auth_service.InactiveUserError):
        return HTTPException(status_code=403, detail=str(error))
    if isinstance(error, auth_service.AuthenticationInputError):
        return HTTPException(status_code=400, detail=str(error))
    return HTTPException(status_code=400, detail="Authentication failed.")


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    payload: LoginRequest,
    session: Session = Depends(get_session),
) -> TokenResponse:
    try:
        result = auth_service.authenticate_user(
            session,
            email=payload.email,
            password=payload.password,
        )
    except auth_service.AuthenticationError as error:
        raise _map_auth_error(error) from error
    return TokenResponse(access_token=result.access_token, token_type=result.token_type)
