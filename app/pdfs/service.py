"""PDF service for managing PDFs"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from supabase import Client

from app.config import Settings


class PDFService:
    def __init__(self, supabase: Client, settings: Settings):
        self.supabase = supabase
        self.settings = settings
    
    async def list_pdfs(self, user_id: str) -> List[dict]:
        """List all PDFs for a user"""
        response = self.supabase.table("pdfs").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    
    async def get_pdf(self, pdf_id: str, user_id: str) -> Optional[dict]:
        """Get a single PDF by ID"""
        response = self.supabase.table("pdfs").select("*").eq("id", pdf_id).eq("user_id", user_id).single().execute()
        return response.data
    
    async def create_pdf(self, user_id: str, title: str, storage_path: str, pdf_id: str = None) -> dict:
        """Create a new PDF record"""
        pdf_data = {
            "id": pdf_id or str(uuid4()),
            "user_id": user_id,
            "title": title,
            "storage_path": storage_path,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        response = self.supabase.table("pdfs").insert(pdf_data).execute()
        return response.data[0]
    
    async def update_pdf_title(self, pdf_id: str, user_id: str, title: str) -> dict:
        """Update PDF title"""
        update_data = {
            "title": title,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        response = self.supabase.table("pdfs").update(update_data).eq("id", pdf_id).eq("user_id", user_id).execute()
        return response.data[0]
    
    async def delete_pdf(self, pdf_id: str, user_id: str) -> None:
        """Delete a PDF and its associated MCQ sets and MCQs (via cascade)"""
        # Hard delete the PDF - cascade deletes will handle mcq_sets and mcqs automatically
        self.supabase.table("pdfs").delete().eq("id", pdf_id).eq("user_id", user_id).execute()
