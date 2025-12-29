"""Auth service for Supabase authentication"""
from supabase import Client


class AuthService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def sign_in_with_password(self, email: str, password: str) -> dict:
        """Sign in with email and password"""
        response = self.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    
    async def sign_out(self, access_token: str) -> None:
        """Sign out user"""
        # Note: With service role key, we can't really sign out
        # Session is managed server-side via cookies
        pass
