"""PDF text extraction using PyMuPDF"""
import fitz  # PyMuPDF
from typing import Dict, List


def extract_text_from_pdf(pdf_bytes: bytes) -> Dict[int, str]:
    """
    Extract text from PDF, organized by page number.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Dictionary mapping page number (1-indexed) to text content
    """
    pages = {}
    
    try:
        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Extract text from each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text()
            
            # Store with 1-indexed page numbers
            pages[page_num + 1] = text.strip()
        
        pdf_document.close()
        
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    return pages


def get_total_pages(pdf_bytes: bytes) -> int:
    """Get total number of pages in PDF"""
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        count = len(pdf_document)
        pdf_document.close()
        return count
    except Exception as e:
        raise Exception(f"Failed to read PDF: {str(e)}")
