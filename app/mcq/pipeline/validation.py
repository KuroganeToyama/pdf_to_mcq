"""MCQ validation and repair using OpenAI"""
import json
from typing import List
from openai import OpenAI

from app.mcq.pipeline.prompts import VALIDATE_MCQS_PROMPT
from app.mcq.pipeline.generation import MCQ


async def validate_and_repair_mcqs(
    mcqs: List[MCQ],
    openai_client: OpenAI,
    model: str
) -> List[MCQ]:
    """
    Validate and repair MCQs using OpenAI.
    
    Args:
        mcqs: List of MCQ objects to validate
        openai_client: OpenAI client instance
        model: OpenAI model to use
        
    Returns:
        List of validated/repaired MCQ objects
    """
    if not mcqs:
        return []
    
    # Convert MCQs to JSON for validation
    mcqs_data = [mcq.to_dict() for mcq in mcqs]
    mcqs_json = json.dumps({"mcqs": mcqs_data}, indent=2)
    
    prompt = VALIDATE_MCQS_PROMPT.format(mcqs=mcqs_json)
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educator validating and fixing multiple choice questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Convert back to MCQ objects
        validated_mcqs = []
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
                source_pages=mcq_data.get("source_pages", []),
                chunk_id=mcq_data.get("chunk_id"),
                flags=mcq_data.get("flags", [])
            )
            
            # Basic validation
            if _is_valid_mcq(mcq):
                validated_mcqs.append(mcq)
        
        return validated_mcqs
        
    except Exception as e:
        # If validation fails, return original MCQs that pass basic checks
        return [mcq for mcq in mcqs if _is_valid_mcq(mcq)]


def _is_valid_mcq(mcq: MCQ) -> bool:
    """Perform basic validation checks on an MCQ"""
    # Check all required fields are present
    if not all([
        mcq.question,
        mcq.choice_a,
        mcq.choice_b,
        mcq.choice_c,
        mcq.choice_d,
        mcq.answer,
        mcq.explanation
    ]):
        return False
    
    # Check answer is valid
    if mcq.answer not in ["A", "B", "C", "D"]:
        return False
    
    # Check choices are different
    choices = [mcq.choice_a, mcq.choice_b, mcq.choice_c, mcq.choice_d]
    if len(set(choices)) < 4:
        return False
    
    return True
