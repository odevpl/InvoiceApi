from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

from api.services.token_service import create_access_token
from api.services.user_service import authenticate_user
from api.models.token import Token, RefreshTokenRequest, AccessTokenResponse
from api.services.user_service import get_user, db
from api.config.security import ALGORITHM
from api.config.settings import settings

router = APIRouter()


@router.post("/auth/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username})
    return Token(access_token=access_token)


@router.post("/auth/refresh", response_model=AccessTokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token,
                             settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = get_user(db, username=username)
    if user is None or user.disabled:
        raise HTTPException(status_code=401, detail="Invalid user")
    new_access_token = create_access_token(data={"sub": user.username})
    return AccessTokenResponse(access_token=new_access_token)
