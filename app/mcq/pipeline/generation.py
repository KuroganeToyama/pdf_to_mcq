"""MCQ generation using OpenAI"""
import json
from typing import List, Dict
from openai import OpenAI

from app.mcq.pipeline.prompts import GENERATE_MCQS_PROMPT
from app.mcq.pipeline.facts import Fact


class MCQ:
    """Represents a multiple choice question"""
    
    def __init__(
        self,
        question: str,
        choice_a: str,
        choice_b: str,
        choice_c: str,
        choice_d: str,
        answer: str,
        explanation: str,
        difficulty: str = "medium",
        bloom: str = "understand",
        fact_id: str = None,
        source_pages: List[int] = None,
        chunk_id: str = None,
        flags: List[str] = None
    ):
        self.question = question
        self.choice_a = choice_a
        self.choice_b = choice_b
        self.choice_c = choice_c
        self.choice_d = choice_d
        self.answer = answer.upper()
        self.explanation = explanation
        self.difficulty = difficulty
        self.bloom = bloom
        self.fact_id = fact_id
        self.source_pages = source_pages or []
        self.chunk_id = chunk_id
        self.flags = flags or []
    
    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choice_a": self.choice_a,
            "choice_b": self.choice_b,
            "choice_c": self.choice_c,
            "choice_d": self.choice_d,
            "answer": self.answer,
            "explanation": self.explanation,
            "difficulty": self.difficulty,
            "bloom": self.bloom,
            "fact_id": self.fact_id,
            "source_pages": self.source_pages,
            "chunk_id": self.chunk_id,
            "flags": self.flags
        }


async def generate_mcqs_from_facts(
    facts: List[Fact],
    count: int,
    openai_client: OpenAI,
    model: str
) -> List[MCQ]:
    """
    Generate MCQs from extracted facts.
    
    Args:
        facts: List of Fact objects
        count: Number of MCQs to generate
        openai_client: OpenAI client instance
        model: OpenAI model to use
        
    Returns:
        List of MCQ objects
    """
    # Select facts to use (prioritize diverse difficulties)
    selected_facts = _select_facts(facts, count)
    
    # Format facts for prompt
    facts_text = "\n\n".join([
        f"Fact ID: {f.fact_id}\n"
        f"Fact: {f.fact}\n"
        f"Pages: {f.source_pages}\n"
        f"Difficulty: {f.difficulty}"
        for f in selected_facts
    ])
    
    prompt = GENERATE_MCQS_PROMPT.format(count=count, facts=facts_text)
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educator creating high-quality multiple choice questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        mcqs = []
        for mcq_data in data.get("mcqs", []):
            mcq = MCQ(
                question=mcq_data.get("question", ""),
                choice_a=mcq_data.get("choice_a", ""),
                choice_b=mcq_data.get("choice_b", ""),
                choice_c=mcq_data.get("choice_c", ""),
                choice_d=mcq_data.get("choice_d", ""),
                answer=mcq_data.get("answer", "A"),
                explanation=mcq_data.get("explanation", ""),
                difficulty=mcq_data.get("difficulty", "medium"),
                bloom=mcq_data.get("bloom", "understand"),
                fact_id=mcq_data.get("fact_id"),
                source_pages=mcq_data.get("source_pages", [])
            )
            mcqs.append(mcq)
        
        return mcqs
        
    except Exception as e:
        raise Exception(f"Failed to generate MCQs: {str(e)}")


def _select_facts(facts: List[Fact], count: int) -> List[Fact]:
    """Select a diverse set of facts for MCQ generation"""
    # Group facts by difficulty
    by_difficulty = {"easy": [], "medium": [], "hard": []}
    for fact in facts:
        if fact.difficulty in by_difficulty:
            by_difficulty[fact.difficulty].append(fact)
    
    # Try to get a balanced mix
    selected = []
    target_per_level = count // 3
    
    for difficulty in ["easy", "medium", "hard"]:
        available = by_difficulty[difficulty]
        take = min(len(available), target_per_level)
        selected.extend(available[:take])
    
    # Fill remaining with any facts
    if len(selected) < count:
        remaining_facts = [f for f in facts if f not in selected]
        selected.extend(remaining_facts[:count - len(selected)])
    
    return selected[:count]
