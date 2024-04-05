from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import VectorParams, Distance


class VectorOps:
    def __init__(self):
        self.client = QdrantClient(":memory:")

    def make_collection(self, documents_with_embeddings, collection_name="letters"):
        documents = documents_with_embeddings['text']
        embeddings = documents_with_embeddings['embedding']

        points = [PointStruct(id=idx, vector=e, payload={'text': d})
                  for idx, (d, e) in enumerate(zip(documents, embeddings))]

        print(f"Creating collection {collection_name} with {len(points)} points of size {embeddings[0].shape[0]}")
        self.client.create_collection(collection_name=collection_name,
                                      vectors_config=VectorParams(size=embeddings[0].shape[0],
                                                                  distance=Distance.COSINE))

        self.client.upsert(collection_name, points)

    def find_similar(self, embedding, collection_name="letters", top_k=5, min_similarity=0.1):
        return self.client.search(collection_name=collection_name, query_vector=embedding,
                                  limit=top_k, score_threshold=min_similarity)
