"""Quiz routes"""
import json
import base64
from urllib.parse import quote
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from supabase import Client

from app.config import get_settings, Settings
from app.deps import get_supabase_client, get_current_user_id
from app.quiz.service import QuizService
from app.mcq.service import MCQService

router = APIRouter(tags=["quiz"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/pdfs/{pdf_id}/quiz", response_class=HTMLResponse)
async def take_quiz(
    request: Request,
    pdf_id: str,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Display quiz page for a PDF using latest MCQ set"""
    mcq_service = MCQService(supabase, settings)
    quiz_service = QuizService(supabase, settings)
    
    # Get PDF
    pdf_response = supabase.table("pdfs").select("*").eq("id", pdf_id).eq("user_id", user_id).single().execute()
    pdf = pdf_response.data
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Get latest completed MCQ set
    latest_mcq_set = await mcq_service.get_latest_mcq_set(pdf_id, user_id)
    if not latest_mcq_set:
        raise HTTPException(
            status_code=404,
            detail="No MCQs available for this PDF. Please generate MCQs first."
        )
    
    # Get MCQs (without answers)
    mcqs = await quiz_service.get_mcqs_for_quiz(latest_mcq_set["id"])
    
    return templates.TemplateResponse("quiz_take.html", {
        "request": request,
        "pdf": pdf,
        "mcq_set": latest_mcq_set,
        "mcqs": mcqs
    })


@router.post("/api/quiz/submit")
async def submit_quiz(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Submit quiz answers and get results"""
    quiz_service = QuizService(supabase, settings)
    
    # Get form data
    form_data = await request.form()
    mcq_set_id = form_data.get("mcq_set_id")
    
    if not mcq_set_id:
        raise HTTPException(status_code=400, detail="MCQ set ID required")
    
    # Verify MCQ set belongs to user
    mcq_set_response = supabase.table("mcq_sets").select("*").eq("id", mcq_set_id).eq("user_id", user_id).single().execute()
    if not mcq_set_response.data:
        raise HTTPException(status_code=404, detail="MCQ set not found")
    
    # Extract answers from form
    answers = {}
    for key, value in form_data.items():
        if key.startswith("answer_"):
            mcq_id = key.replace("answer_", "")
            answers[mcq_id] = value
    
    # Check answers
    results = await quiz_service.check_answers(mcq_set_id, answers)
    
    # Encode results as base64 to pass via URL
    results_json = json.dumps(results)
    results_b64 = base64.b64encode(results_json.encode()).decode()
    
    # Redirect with encoded results in URL
    response = RedirectResponse(
        url=f"/quiz/results?mcq_set_id={mcq_set_id}&data={quote(results_b64)}",
        status_code=303
    )
    return response


@router.get("/quiz/results", response_class=HTMLResponse)
async def quiz_results(
    request: Request,
    mcq_set_id: str,
    data: str,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Display quiz results"""
    try:
        # Decode results from URL parameter
        results_json = base64.b64decode(data.encode()).decode()
        results = json.loads(results_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid results data")
    
    # Get MCQ set and PDF info
    mcq_set_response = supabase.table("mcq_sets").select("*, pdfs(*)").eq("id", mcq_set_id).single().execute()
    mcq_set = mcq_set_response.data
    
    return templates.TemplateResponse("quiz_result.html", {
        "request": request,
        "results": results,
        "mcq_set": mcq_set,
        "pdf": mcq_set.get("pdfs")
    })
