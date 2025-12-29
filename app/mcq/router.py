"""MCQ routes"""
from fastapi import APIRouter, Depends, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from supabase import Client

from app.config import get_settings, Settings
from app.deps import get_supabase_client, get_current_user_id
from app.mcq.service import MCQService
from app.mcq.pipeline import run_mcq_generation_pipeline

router = APIRouter(prefix="/api", tags=["mcq"])


@router.post("/pdfs/{pdf_id}/mcq-sets")
async def create_mcq_set(
    pdf_id: str,
    background_tasks: BackgroundTasks,
    requested_count: int = Form(..., ge=1, le=500),
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Create a new MCQ generation set"""
    mcq_service = MCQService(supabase, settings)
    
    # Verify PDF exists and belongs to user
    pdf_response = supabase.table("pdfs").select("id").eq("id", pdf_id).eq("user_id", user_id).execute()
    if not pdf_response.data:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Check for active generation
    has_active = await mcq_service.check_active_generation(pdf_id, user_id)
    if has_active:
        raise HTTPException(
            status_code=400,
            detail="MCQ generation already in progress for this PDF"
        )
    
    # Validate requested count
    if requested_count > settings.MAX_MCQS:
        raise HTTPException(
            status_code=400,
            detail=f"Requested count exceeds maximum of {settings.MAX_MCQS}"
        )
    
    # Create MCQ set record
    mcq_set = await mcq_service.create_mcq_set(
        pdf_id=pdf_id,
        user_id=user_id,
        requested_count=requested_count,
        model=settings.OPENAI_MODEL
    )
    
    # Launch background task for generation
    background_tasks.add_task(
        run_mcq_generation_pipeline,
        mcq_set_id=mcq_set["id"],
        pdf_id=pdf_id,
        user_id=user_id,
        requested_count=requested_count,
        model=settings.OPENAI_MODEL,
        supabase=supabase,
        settings=settings
    )
    
    return JSONResponse({"mcq_set": mcq_set})


@router.get("/mcq-sets/{mcq_set_id}")
async def get_mcq_set(
    mcq_set_id: str,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Get MCQ set by ID"""
    mcq_service = MCQService(supabase, settings)
    
    mcq_set = await mcq_service.get_mcq_set(mcq_set_id, user_id)
    if not mcq_set:
        raise HTTPException(status_code=404, detail="MCQ set not found")
    
    return JSONResponse({"mcq_set": mcq_set})


@router.get("/mcq-sets/{mcq_set_id}/mcqs")
async def get_mcqs(
    mcq_set_id: str,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Get all MCQs for a set"""
    mcq_service = MCQService(supabase, settings)
    
    # Verify MCQ set belongs to user
    mcq_set = await mcq_service.get_mcq_set(mcq_set_id, user_id)
    if not mcq_set:
        raise HTTPException(status_code=404, detail="MCQ set not found")
    
    # Get MCQs
    mcqs = await mcq_service.get_mcqs(mcq_set_id)
    
    return JSONResponse({"mcqs": mcqs})
