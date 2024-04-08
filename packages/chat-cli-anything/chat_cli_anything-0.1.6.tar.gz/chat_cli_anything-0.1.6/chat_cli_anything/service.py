from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from chat_cli_anything.embedding import build_embedding_model
from chat_cli_anything.rerank import build_reranker
import click

SERVICE_NAME = 'EmbeddingAndRerank'


class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingResponse(BaseModel):
    embedding: List[float]

class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    topk: int = 4

class RerankerResponse(BaseModel):
    documents: List[str]


def create_app():
    app = FastAPI()
    embedding_model = build_embedding_model()
    reranker = build_reranker()
    db = None

    @app.post("/embedding", response_model=EmbeddingResponse)
    def get_embedding(request: EmbeddingRequest):
        r = embedding_model.embed_query(request.text)
        return {'embedding': r}

    @app.post("/embed_documents", response_model=List[EmbeddingResponse])
    def embed_documents(request: List[EmbeddingRequest]):
        res = embedding_model.embed_documents([x.text for x in request])
        return [{'embedding': r} for r in res]

    @app.post('/rerank', response_model=RerankerResponse)
    def rerank(request: RerankRequest):
        query = request.query
        documents = request.documents
        topk = request.topk
        model_inputs = [(query, doc) for doc in documents]
        scores = reranker.compute_score(model_inputs) 
        results = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
        return {'documents': [r[1] for r  in results[:topk]]}

    @app.get('/ping')
    def get_service_name():
        return {'service_name': SERVICE_NAME}

    return app


@click.command()
@click.argument('port', type=int)
def main(port: int):
    import uvicorn
    app = create_app()
    uvicorn.run(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()