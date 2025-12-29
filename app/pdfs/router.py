"""PDF routes"""
from fastapi import APIRouter, Depends, Request, File, UploadFile, Form, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from supabase import Client

from app.config import get_settings, Settings
from app.deps import get_supabase_client, get_current_user_id
from app.pdfs.service import PDFService
from app.pdfs.storage import StorageService

router = APIRouter(tags=["pdfs"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/pdfs", response_class=HTMLResponse)
async def list_pdfs_page(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Display list of PDFs"""
    pdf_service = PDFService(supabase, settings)
    pdfs = await pdf_service.list_pdfs(user_id)
    
    return templates.TemplateResponse("pdf_list.html", {
        "request": request,
        "pdfs": pdfs
    })


@router.get("/pdfs/{pdf_id}", response_class=HTMLResponse)
async def view_pdf_page(
    request: Request,
    pdf_id: str,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Display PDF viewer page"""
    pdf_service = PDFService(supabase, settings)
    
    pdf = await pdf_service.get_pdf(pdf_id, user_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Use API endpoint to serve PDF
    pdf_url = f"/api/pdfs/{pdf_id}/file"
    
    # Get latest MCQ set if exists
    mcq_sets_response = supabase.table("mcq_sets").select("*").eq("pdf_id", pdf_id).eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
    latest_mcq_set = mcq_sets_response.data[0] if mcq_sets_response.data else None
    
    return templates.TemplateResponse("pdf_view.html", {
        "request": request,
        "pdf": pdf,
        "pdf_url": pdf_url,
        "latest_mcq_set": latest_mcq_set
    })


@router.post("/api/pdfs")
async def upload_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Upload a new PDF"""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {settings.MAX_UPLOAD_MB}MB limit"
        )
    
    # Create PDF record
    pdf_service = PDFService(supabase, settings)
    storage_service = StorageService(supabase, settings)
    
    from uuid import uuid4
    pdf_id = str(uuid4())
    
    # Upload to storage
    storage_path = await storage_service.upload_pdf(user_id, pdf_id, content)
    
    # Create database record
    pdf = await pdf_service.create_pdf(user_id, title, storage_path, pdf_id)
    
    return JSONResponse({"pdf": pdf})


@router.patch("/api/pdfs/{pdf_id}")
async def update_pdf(
    pdf_id: str,
    title: str = Form(...),
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Update PDF title"""
    pdf_service = PDFService(supabase, settings)
    
    try:
        pdf = await pdf_service.update_pdf_title(pdf_id, user_id, title)
        return JSONResponse({"pdf": pdf})
    except Exception as e:
        raise HTTPException(status_code=404, detail="PDF not found")


@router.delete("/api/pdfs/{pdf_id}")
async def delete_pdf(
    pdf_id: str,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Delete a PDF"""
    pdf_service = PDFService(supabase, settings)
    storage_service = StorageService(supabase, settings)
    
    # Verify PDF exists
    pdf = await pdf_service.get_pdf(pdf_id, user_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Delete from database (soft delete)
    await pdf_service.delete_pdf(pdf_id, user_id)
    
    # Delete from storage
    try:
        await storage_service.delete_pdf(user_id, pdf_id)
    except:
        pass  # Storage deletion is optional
    
    return JSONResponse({"success": True})


@router.get("/api/pdfs/{pdf_id}/file")
async def get_pdf_file(
    pdf_id: str,
    user_id: str = Depends(get_current_user_id),
    supabase: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """Serve PDF file"""
    pdf_service = PDFService(supabase, settings)
    storage_service = StorageService(supabase, settings)
    
    # Verify PDF exists and belongs to user
    pdf = await pdf_service.get_pdf(pdf_id, user_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Download PDF from storage
    try:
        pdf_content = await storage_service.download_pdf(user_id, pdf_id)
        return Response(content=pdf_content, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"PDF file not found in storage: {str(e)}")
