"""FastAPI dependencies"""
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from supabase import create_client, Client

from app.config import get_settings, Settings


def get_supabase_client(settings: Settings = Depends(get_settings)) -> Client:
    """Get Supabase client with service role key"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def get_current_user_id(request: Request) -> str:
    """Get current authenticated user ID from session"""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user_id


def get_current_user_token(request: Request) -> str:
    """Get current user's access token from session"""
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return token


def get_optional_user_id(request: Request) -> Optional[str]:
    """Get current user ID if authenticated, None otherwise"""
    return request.session.get("user_id")
