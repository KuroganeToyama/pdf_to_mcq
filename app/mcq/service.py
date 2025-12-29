"""MCQ service for managing MCQ sets"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from supabase import Client

from app.config import Settings


class MCQService:
    def __init__(self, supabase: Client, settings: Settings):
        self.supabase = supabase
        self.settings = settings
    
    async def get_mcq_set(self, mcq_set_id: str, user_id: str) -> Optional[dict]:
        """Get MCQ set by ID"""
        response = self.supabase.table("mcq_sets").select("*").eq("id", mcq_set_id).eq("user_id", user_id).single().execute()
        return response.data
    
    async def get_latest_mcq_set(self, pdf_id: str, user_id: str) -> Optional[dict]:
        """Get the latest completed MCQ set for a PDF"""
        response = self.supabase.table("mcq_sets").select("*").eq("pdf_id", pdf_id).eq("user_id", user_id).eq("status", "done").order("created_at", desc=True).limit(1).execute()
        return response.data[0] if response.data else None
    
    async def check_active_generation(self, pdf_id: str, user_id: str) -> bool:
        """Check if there's an active generation for this PDF"""
        response = self.supabase.table("mcq_sets").select("id").eq("pdf_id", pdf_id).eq("user_id", user_id).in_("status", ["queued", "running"]).execute()
        return len(response.data) > 0
    
    async def create_mcq_set(self, pdf_id: str, user_id: str, requested_count: int, model: str) -> dict:
        """Create a new MCQ set record"""
        mcq_set_data = {
            "id": str(uuid4()),
            "pdf_id": pdf_id,
            "user_id": user_id,
            "model": model,
            "requested_count": requested_count,
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        response = self.supabase.table("mcq_sets").insert(mcq_set_data).execute()
        return response.data[0]
    
    async def get_mcqs(self, mcq_set_id: str) -> List[dict]:
        """Get all MCQs for a set"""
        response = self.supabase.table("mcqs").select("*").eq("mcq_set_id", mcq_set_id).order("idx").execute()
        return response.data
