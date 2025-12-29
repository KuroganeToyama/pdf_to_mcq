"""Persist MCQs to database"""
from datetime import datetime, timezone
from typing import List
from supabase import Client

from app.mcq.pipeline.generation import MCQ


async def persist_mcqs(
    mcqs: List[MCQ],
    mcq_set_id: str,
    supabase: Client
) -> int:
    """
    Persist MCQs to the database.
    
    Args:
        mcqs: List of MCQ objects
        mcq_set_id: ID of the MCQ set
        supabase: Supabase client
        
    Returns:
        Number of MCQs persisted
    """
    if not mcqs:
        return 0
    
    # Prepare MCQ data for insertion
    mcq_records = []
    for idx, mcq in enumerate(mcqs):
        record = {
            "mcq_set_id": mcq_set_id,
            "idx": idx,
            "question": mcq.question,
            "choice_a": mcq.choice_a,
            "choice_b": mcq.choice_b,
            "choice_c": mcq.choice_c,
            "choice_d": mcq.choice_d,
            "answer": mcq.answer,
            "explanation": mcq.explanation,
            "difficulty": mcq.difficulty,
            "bloom": mcq.bloom,
            "source_pages": mcq.source_pages,
            "chunk_id": mcq.chunk_id,
            "fact_id": mcq.fact_id,
            "flags": mcq.flags,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        mcq_records.append(record)
    
    # Insert all MCQs at once
    try:
        response = supabase.table("mcqs").insert(mcq_records).execute()
        return len(response.data)
    except Exception as e:
        raise Exception(f"Failed to persist MCQs: {str(e)}")


async def update_mcq_set_status(
    mcq_set_id: str,
    status: str,
    supabase: Client,
    error: str = None
) -> None:
    """
    Update MCQ set status.
    
    Args:
        mcq_set_id: ID of the MCQ set
        status: New status (queued, running, done, failed)
        supabase: Supabase client
        error: Error message if status is failed
    """
    update_data = {
        "status": status,
        "completed_at": datetime.now(timezone.utc).isoformat() if status in ["done", "failed"] else None
    }
    
    if error:
        update_data["error"] = error
    
    try:
        supabase.table("mcq_sets").update(update_data).eq("id", mcq_set_id).execute()
    except Exception as e:
        raise Exception(f"Failed to update MCQ set status: {str(e)}")
