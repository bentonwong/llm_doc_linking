import openai
from typing import List
from .models import BriefPairRequest, BriefPairResult, LinkResult
from .utils import cosine_similarity
from .config import OPENAI_API_KEY

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please check your environment variables.")

openai.api_key = OPENAI_API_KEY

def embed_text(text: str, model: str = "text-embedding-3-large") -> List[float]:
    try:
        response = openai.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"Embedding failed for input: {text[:60]}... \nError: {e}")

def process_brief_pair(brief_data: BriefPairRequest) -> BriefPairResult:
    moving_args = brief_data.moving_brief.brief_arguments
    response_args = brief_data.response_brief.brief_arguments
    top_n = brief_data.top_n or 1

    # Embed all moving arguments
    moving_data = []
    for arg in moving_args:
        full_text = f"{arg.heading}\n\n{arg.content}"
        full_text = full_text[:8000]
        embedding = embed_text(full_text)
        moving_data.append({
            "heading": arg.heading,
            "content": arg.content,
            "embedding": embedding
        })

    # Embed all response arguments
    response_data = []
    for arg in response_args:
        full_text = f"{arg.heading}\n\n{arg.content}"
        embedding = embed_text(full_text)
        response_data.append({
            "heading": arg.heading,
            "content": arg.content,
            "embedding": embedding
        })

    # Calculate similarity scores
    top_links = []
    for m in moving_data:
        scored_links = []
        for r in response_data:
            score = cosine_similarity(m["embedding"], r["embedding"])
            scored_links.append((r["heading"], r["content"], score))

        scored_links.sort(key=lambda x: x[2], reverse=True)
        for match in scored_links[:top_n]:
            top_links.append(LinkResult(
                moving_heading=m["heading"],
                moving_content=m["content"],
                response_heading=match[0],
                response_content=match[1],
                score=match[2]
            ))

    return BriefPairResult(
        moving_brief_id=brief_data.moving_brief.brief_id,
        response_brief_id=brief_data.response_brief.brief_id,
        top_links=top_links
    )
