"""Text chunking utilities"""
from typing import List, Dict, Tuple


class TextChunk:
    """Represents a chunk of text with metadata"""
    
    def __init__(self, text: str, page_numbers: List[int], chunk_id: str):
        self.text = text
        self.page_numbers = page_numbers
        self.chunk_id = chunk_id
    
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "page_numbers": self.page_numbers,
            "chunk_id": self.chunk_id
        }


def chunk_text(
    pages: Dict[int, str],
    target_words: int = 1000,
    overlap_words: int = 100
) -> List[TextChunk]:
    """
    Chunk text from multiple pages with overlap.
    
    Args:
        pages: Dictionary mapping page number to text
        target_words: Target number of words per chunk
        overlap_words: Number of words to overlap between chunks
        
    Returns:
        List of TextChunk objects
    """
    chunks = []
    chunk_id = 0
    
    # Combine all pages into a single text with page tracking
    combined_text = []
    word_to_page = []  # Track which page each word belongs to
    
    for page_num in sorted(pages.keys()):
        text = pages[page_num]
        words = text.split()
        combined_text.extend(words)
        word_to_page.extend([page_num] * len(words))
    
    # Create chunks
    start_idx = 0
    while start_idx < len(combined_text):
        # Get words for this chunk
        end_idx = min(start_idx + target_words, len(combined_text))
        chunk_words = combined_text[start_idx:end_idx]
        
        # Get unique page numbers for this chunk
        chunk_pages = sorted(set(word_to_page[start_idx:end_idx]))
        
        # Create chunk
        chunk_text = " ".join(chunk_words)
        chunk = TextChunk(
            text=chunk_text,
            page_numbers=chunk_pages,
            chunk_id=f"chunk_{chunk_id}"
        )
        chunks.append(chunk)
        
        chunk_id += 1
        
        # Move to next chunk with overlap
        start_idx = end_idx - overlap_words
        
        # Break if we've reached the end
        if end_idx >= len(combined_text):
            break
    
    return chunks
