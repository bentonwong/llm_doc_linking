import openai
from typing import List
from .models import BriefPairRequest, BriefPairResult, LinkResult
from .utils import cosine_similarity
from .config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def embed_texts(texts: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
    response = openai.Embedding.create(input=texts, model=model)
    return [e["embedding"] for e in response["data"]]

def process_brief_pair(brief_data: BriefPairRequest) -> BriefPairResult:
    moving_args = brief_data.moving_brief.brief_arguments
    response_args = brief_data.response_brief.brief_arguments
    top_n = brief_data.top_n or 1

    moving_texts = [f"{arg.heading}: {arg.content}" for arg in moving_args]
    response_texts = [f"{arg.heading}: {arg.content}" for arg in response_args]

    moving_embeddings = embed_texts(moving_texts)
    response_embeddings = embed_texts(response_texts)

    top_links = []
    for m_arg, m_emb in zip(moving_args, moving_embeddings):
        scored_links = []
        for r_arg, r_emb in zip(response_args, response_embeddings):
            score = cosine_similarity(m_emb, r_emb)
            scored_links.append((r_arg.heading, r_arg.content, score))

        scored_links.sort(key=lambda x: x[2], reverse=True)
        for match in scored_links[:top_n]:
            top_links.append(LinkResult(
                moving_heading=m_arg.heading,
                moving_content=m_arg.content,
                response_heading=match[0],
                response_content=match[1],
                score=match[2]
            ))

    return BriefPairResult(
        moving_brief_id=brief_data.moving_brief.brief_id,
        response_brief_id=brief_data.response_brief.brief_id,
        top_links=top_links
    )
