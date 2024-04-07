from typing import Sequence
from chat_cli_anything.config import Config
import requests

def build_reranker():
    from FlagEmbedding import FlagReranker
    # Setting use_fp16 to True speeds up computation with a slight performance degradation
    reranker = FlagReranker('BAAI/bge-reranker-base', use_fp16=True) 
    return reranker

def rerank(
    query: str,
    docs: Sequence[str],
    topk: int = 4,
) -> Sequence[str]:
    """Rerank the documents using BGE-Reranker."""
    port = Config().get('local_server_port', Config.DEFAULT_PORT) 
    response = requests.post(
        f"http://localhost:{port}/rerank",
         json={"query": query, "documents": docs, "topk": topk}
    )
    return response.json()['documents']
