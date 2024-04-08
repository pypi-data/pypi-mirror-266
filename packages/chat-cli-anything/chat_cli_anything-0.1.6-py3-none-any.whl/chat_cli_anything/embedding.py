from langchain_core.embeddings import Embeddings
from logging import getLogger
from typing import List
import logging
import requests

logger = getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def build_embedding_model():
    import torch
    from langchain_community.embeddings import HuggingFaceBgeEmbeddings
    """"""
    logger.info('Loading embedding model')
    # model_name = "BAAI/bge-small-zh-v1.5"
    model_name = "infgrad/stella-base-zh-v3-1792d"

    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    model_kwargs = {"device": device}
    encode_kwargs = {"normalize_embeddings": True}

    embedding_model = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    logger.info('Loading complete.')
    return embedding_model


class LocalEmbeddings(Embeddings):
    def __init__(self, port: int) -> None:
        self.port = port
        super().__init__()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = requests.post(
            f'http://localhost:{self.port}/embed_documents',
            timeout=10 * len(texts) + 10,
            json=[{'text': text} for text in texts]
        )
        return [r['embedding'] for r in response.json()]

    def embed_query(self, text: str) -> List[float]:
        response = requests.post(
            f'http://localhost:{self.port}/embedding',
            timeout=10,
            json={'text': text}
        )
        return response.json()['embedding']
