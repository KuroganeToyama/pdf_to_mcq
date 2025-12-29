"""Storage utilities for Supabase Storage"""
from io import BytesIO
from supabase import Client

from app.config import Settings


class StorageService:
    def __init__(self, supabase: Client, settings: Settings):
        self.supabase = supabase
        self.settings = settings
        self.bucket = settings.PDF_BUCKET
    
    def get_storage_path(self, user_id: str, pdf_id: str) -> str:
        """Get storage path for a PDF"""
        return f"{user_id}/{pdf_id}.pdf"
    
    async def upload_pdf(self, user_id: str, pdf_id: str, file_content: bytes) -> str:
        """Upload PDF to storage and return path"""
        path = self.get_storage_path(user_id, pdf_id)
        
        try:
            # Upload to Supabase Storage
            result = self.supabase.storage.from_(self.bucket).upload(
                path=path,
                file=file_content,
                file_options={"content-type": "application/pdf"}
            )
            print(f"Upload result: {result}")
        except Exception as e:
            print(f"Upload error: {e}")
            raise
        
        return path
    
    async def delete_pdf(self, user_id: str, pdf_id: str) -> None:
        """Delete PDF from storage"""
        path = self.get_storage_path(user_id, pdf_id)
        self.supabase.storage.from_(self.bucket).remove([path])
    
    async def get_pdf_url(self, user_id: str, pdf_id: str, expires_in: int = 3600) -> str:
        """Get signed URL for PDF"""
        path = self.get_storage_path(user_id, pdf_id)
        
        # Create signed URL
        response = self.supabase.storage.from_(self.bucket).create_signed_url(
            path=path,
            expires_in=expires_in
        )
        
        # Response can be either a dict or object with signedURL attribute
        if isinstance(response, dict):
            return response.get("signedURL") or response.get("signed_url")
        return response
    
    async def download_pdf(self, user_id: str, pdf_id: str) -> bytes:
        """Download PDF content"""
        path = self.get_storage_path(user_id, pdf_id)
        
        response = self.supabase.storage.from_(self.bucket).download(path)
        return response
