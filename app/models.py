from pydantic import BaseModel
from typing import List, Optional

class Argument(BaseModel):
    heading: str
    content: str

class Brief(BaseModel):
    brief_id: str
    brief_arguments: List[Argument]

class BriefPairRequest(BaseModel):
    moving_brief: Brief
    response_brief: Brief
    top_n: Optional[int] = 1

class LinkResult(BaseModel):
    moving_heading: str
    moving_content: str
    response_heading: str
    response_content: str
    score: float

class BriefPairResult(BaseModel):
    moving_brief_id: str
    response_brief_id: str
    top_links: List[LinkResult]
