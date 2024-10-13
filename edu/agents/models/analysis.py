from pydantic import BaseModel
from typing import List

class AnalysisOutput(BaseModel):
    understanding: str
    misconceptions: str
    reasoning: str
    strengths: List[str]
    areas_for_improvement: List[str]
    feedback: str
    follow_up_questions: List[str]