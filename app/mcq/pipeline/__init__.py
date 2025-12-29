"""Main MCQ generation pipeline orchestrator"""
from openai import OpenAI
from supabase import Client

from app.config import Settings
from app.pdfs.storage import StorageService
from app.mcq.pipeline.pdf_extract import extract_text_from_pdf
from app.mcq.pipeline.chunking import chunk_text
from app.mcq.pipeline.facts import extract_facts_from_chunks
from app.mcq.pipeline.generation import generate_mcqs_from_facts
from app.mcq.pipeline.validation import validate_and_repair_mcqs
from app.mcq.pipeline.persistence import persist_mcqs, update_mcq_set_status


async def run_mcq_generation_pipeline(
    mcq_set_id: str,
    pdf_id: str,
    user_id: str,
    requested_count: int,
    model: str,
    supabase: Client,
    settings: Settings
):
    """
    Run the complete MCQ generation pipeline.
    
    Args:
        mcq_set_id: ID of the MCQ set
        pdf_id: ID of the PDF
        user_id: ID of the user
        requested_count: Number of MCQs to generate
        model: OpenAI model to use
        supabase: Supabase client
        settings: App settings
    """
    try:
        # Update status to running
        await update_mcq_set_status(mcq_set_id, "running", supabase)
        
        # Initialize services
        storage_service = StorageService(supabase, settings)
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Step 1: Download PDF from storage
        pdf_bytes = await storage_service.download_pdf(user_id, pdf_id)
        
        # Step 2: Extract text from PDF
        pages = extract_text_from_pdf(pdf_bytes)
        
        # Step 3: Chunk text
        chunks = chunk_text(pages, target_words=1000, overlap_words=100)
        
        # Step 4: Extract facts from chunks
        facts = await extract_facts_from_chunks(chunks, openai_client, model)
        
        # Need enough facts to generate MCQs
        if len(facts) < requested_count:
            raise Exception(f"Not enough facts extracted ({len(facts)}) to generate {requested_count} MCQs")
        
        # Step 5: Generate MCQs from facts
        mcqs = await generate_mcqs_from_facts(facts, requested_count, openai_client, model)
        
        # Step 6: Validate and repair MCQs
        validated_mcqs = await validate_and_repair_mcqs(mcqs, openai_client, model)
        
        # Check if we have enough valid MCQs
        if len(validated_mcqs) == 0:
            raise Exception("No valid MCQs generated after validation")
        
        # Step 7: Persist MCQs to database
        count = await persist_mcqs(validated_mcqs, mcq_set_id, supabase)
        
        # Step 8: Update MCQ set status to done
        await update_mcq_set_status(mcq_set_id, "done", supabase)
        
    except Exception as e:
        # Update status to failed with error message
        error_message = str(e)
        await update_mcq_set_status(mcq_set_id, "failed", supabase, error=error_message)
        raise
