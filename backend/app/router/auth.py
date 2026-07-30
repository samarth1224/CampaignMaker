"""Authentication routes for registered and guest users."""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import config
from app.models.usermodel import User, UserCreate
from app.utility.security import (
    DUMMY_HASH,
    create_access_token,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _build_token_response(user: User) -> JSONResponse:
    """Create the access-token response shared by every successful login."""
    access_token = create_access_token(
        data={
            "sub": str(user.public_id),
            "username": user.username,
            "is_guest": user.is_guest,
        },
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="none" if config.SECURE_COOKIES else "lax",
        secure=config.SECURE_COOKIES,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return response


def _invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/register")
async def register_user(user: UserCreate) -> JSONResponse:
    """Register a user and issue its access token."""
    if await User.find_one(User.username == user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        is_guest=False,
    )
    await new_user.insert()
    return _build_token_response(new_user)


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> JSONResponse:
    """Authenticate a registered user and issue an access token."""
    user = await User.find_one(User.username == form_data.username)
    stored_hash = user.hashed_password if user and user.hashed_password else DUMMY_HASH
    password_is_valid = verify_password(form_data.password, stored_hash)
    if not user or not user.hashed_password or not password_is_valid:
        raise _invalid_credentials()
    return _build_token_response(user)


@router.post("/guest")
async def login_as_guest() -> JSONResponse:
    """Create a guest user and issue its access token."""
    guest_id = uuid.uuid4()
    guest_user = User(
        public_id=guest_id,
        username=f"guest_{guest_id.hex[:12]}",
        is_guest=True,
        hashed_password=None,
    )
    await guest_user.insert()
    return _build_token_response(guest_user)


@router.post("/logout")
async def logout() -> JSONResponse:
    """Clear the access-token cookie."""
    response = JSONResponse(content={"message": "Successfully logged out"})
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="none" if config.SECURE_COOKIES else "lax",
        secure=config.SECURE_COOKIES,
        path="/",
    )
    return response
