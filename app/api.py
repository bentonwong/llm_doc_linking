from fastapi import APIRouter
from .models import BriefPairRequest, BriefPairResult
from .logic import process_brief_pair

router = APIRouter()

@router.post("/analyze", response_model=BriefPairResult)
def analyze_briefs(brief_data: BriefPairRequest):
    return process_brief_pair(brief_data)
