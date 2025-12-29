"""Quiz service for managing quiz attempts"""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from supabase import Client

from app.config import Settings


class QuizService:
    def __init__(self, supabase: Client, settings: Settings):
        self.supabase = supabase
        self.settings = settings
    
    async def create_quiz_attempt(self, mcq_set_id: str, user_id: str) -> dict:
        """Create a new quiz attempt"""
        mcq_set_response = self.supabase.table("mcq_sets").select("*").eq("id", mcq_set_id).eq("user_id", user_id).single().execute()
        return mcq_set_response.data
    
    async def get_mcqs_for_quiz(self, mcq_set_id: str) -> List[dict]:
        """Get MCQs for a quiz (without answers)"""
        response = self.supabase.table("mcqs").select(
            "id, idx, question, choice_a, choice_b, choice_c, choice_d, difficulty"
        ).eq("mcq_set_id", mcq_set_id).order("idx").execute()
        return response.data
    
    async def check_answers(self, mcq_set_id: str, answers: dict) -> dict:
        """Check user answers against correct answers"""
        # Get all MCQs with answers
        mcqs_response = self.supabase.table("mcqs").select("*").eq("mcq_set_id", mcq_set_id).order("idx").execute()
        mcqs = mcqs_response.data
        
        results = []
        correct_count = 0
        
        for mcq in mcqs:
            mcq_id = mcq["id"]
            user_answer = answers.get(mcq_id, "").upper()
            correct_answer = mcq["answer"]
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_count += 1
            
            results.append({
                "mcq_id": mcq_id,
                "idx": mcq["idx"],
                "question": mcq["question"],
                "choice_a": mcq["choice_a"],
                "choice_b": mcq["choice_b"],
                "choice_c": mcq["choice_c"],
                "choice_d": mcq["choice_d"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": mcq["explanation"]
            })
        
        total_questions = len(mcqs)
        score_percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        return {
            "correct_count": correct_count,
            "total_questions": total_questions,
            "score_percentage": round(score_percentage, 2),
            "results": results
        }
