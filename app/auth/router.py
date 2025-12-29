"""Auth routes"""
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from supabase import Client

from app.deps import get_supabase_client, get_optional_user_id
from app.auth.service import AuthService

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user_id: str | None = Depends(get_optional_user_id)
):
    """Display login page"""
    # If already logged in, redirect to PDFs
    if user_id:
        return RedirectResponse(url="/pdfs", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    supabase: Client = Depends(get_supabase_client)
):
    """Handle login form submission"""
    try:
        auth_service = AuthService(supabase)
        response = await auth_service.sign_in_with_password(email, password)
        
        # Store session
        request.session["user_id"] = response.user.id
        request.session["access_token"] = response.session.access_token
        request.session["email"] = response.user.email
        
        return RedirectResponse(url="/pdfs", status_code=302)
    
    except Exception as e:
        # Return to login with error
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid email or password"
            },
            status_code=400
        )


@router.post("/logout")
async def logout(request: Request):
    """Handle logout"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
