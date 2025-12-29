"""Prompts for MCQ generation pipeline"""

EXTRACT_FACTS_PROMPT = """You are an expert educator analyzing educational content to extract atomic facts.

Extract atomic facts from the following text. Each fact should be:
- Self-contained and independently understandable
- Specific and concrete (not vague or general)
- Directly stated or strongly implied in the text
- Suitable for creating a quiz question

Text:
{text}

Return a JSON object with this structure:
{{
  "facts": [
    {{
      "id": "unique_id",
      "fact": "the atomic fact",
      "source_pages": [page numbers],
      "difficulty": "easy|medium|hard"
    }}
  ]
}}

Output only valid JSON, no other text."""

GENERATE_MCQS_PROMPT = """You are an expert educator creating multiple choice questions.

Create {count} multiple choice questions based on these facts:
{facts}

Requirements:
- Each question must have exactly 4 choices (A, B, C, D)
- Exactly ONE choice must be correct
- Wrong choices should be plausible but clearly incorrect
- Include a detailed explanation
- Difficulty should match the fact difficulty
- Apply Bloom's taxonomy appropriately

Return a JSON object with this structure:
{{
  "mcqs": [
    {{
      "question": "the question text",
      "choice_a": "first choice",
      "choice_b": "second choice",
      "choice_c": "third choice",
      "choice_d": "fourth choice",
      "answer": "A|B|C|D",
      "explanation": "detailed explanation why the answer is correct",
      "difficulty": "easy|medium|hard",
      "bloom": "remember|understand|apply|analyze|evaluate|create",
      "fact_id": "id of fact used",
      "source_pages": [page numbers]
    }}
  ]
}}

Output only valid JSON, no other text."""

VALIDATE_MCQS_PROMPT = """You are an expert educator validating multiple choice questions.

Review these MCQs and fix any issues:
{mcqs}

Check for:
- Ambiguous wording
- Multiple correct answers
- No correct answer
- Implausible distractors
- Unclear explanations
- Grammar/spelling errors

Return the corrected MCQs in the same JSON format. If an MCQ is unfixable, omit it.

Output only valid JSON, no other text."""
