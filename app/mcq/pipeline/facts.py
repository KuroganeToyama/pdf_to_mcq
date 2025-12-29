"""Facts extraction from text chunks using OpenAI"""
import json
from typing import List, Dict
from openai import OpenAI

from app.mcq.pipeline.prompts import EXTRACT_FACTS_PROMPT
from app.mcq.pipeline.chunking import TextChunk


class Fact:
    """Represents an atomic fact extracted from text"""
    
    def __init__(self, fact_id: str, fact: str, source_pages: List[int], 
                 difficulty: str = "medium", chunk_id: str = None):
        self.fact_id = fact_id
        self.fact = fact
        self.source_pages = source_pages
        self.difficulty = difficulty
        self.chunk_id = chunk_id
    
    def to_dict(self) -> dict:
        return {
            "fact_id": self.fact_id,
            "fact": self.fact,
            "source_pages": self.source_pages,
            "difficulty": self.difficulty,
            "chunk_id": self.chunk_id
        }


async def extract_facts_from_chunk(
    chunk: TextChunk,
    openai_client: OpenAI,
    model: str
) -> List[Fact]:
    """
    Extract atomic facts from a text chunk using OpenAI.
    
    Args:
        chunk: TextChunk to extract facts from
        openai_client: OpenAI client instance
        model: OpenAI model to use
        
    Returns:
        List of Fact objects
    """
    prompt = EXTRACT_FACTS_PROMPT.format(text=chunk.text)
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educator extracting facts from educational content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        facts = []
        for fact_data in data.get("facts", []):
            fact = Fact(
                fact_id=fact_data.get("id", f"{chunk.chunk_id}_fact_{len(facts)}"),
                fact=fact_data.get("fact", ""),
                source_pages=fact_data.get("source_pages", chunk.page_numbers),
                difficulty=fact_data.get("difficulty", "medium"),
                chunk_id=chunk.chunk_id
            )
            facts.append(fact)
        
        return facts
        
    except Exception as e:
        raise Exception(f"Failed to extract facts: {str(e)}")


async def extract_facts_from_chunks(
    chunks: List[TextChunk],
    openai_client: OpenAI,
    model: str
) -> List[Fact]:
    """
    Extract facts from multiple chunks.
    
    Args:
        chunks: List of TextChunk objects
        openai_client: OpenAI client instance
        model: OpenAI model to use
        
    Returns:
        List of all extracted Facts
    """
    all_facts = []
    
    for chunk in chunks:
        facts = await extract_facts_from_chunk(chunk, openai_client, model)
        all_facts.extend(facts)
    
    return all_facts
