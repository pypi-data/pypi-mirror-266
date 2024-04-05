from typing import Any

import numpy as np
import openai
from numpy import ndarray, dtype

from .shared import load_openai_api_key


class OpenAIConnector:
    def __init__(self, api_key):
        self.client = openai.Client(api_key=api_key)

    def embed_documents(self, documents: list[str], embedding_model="text-embedding-3-small") -> list[
        ndarray[Any, dtype[Any]]]:
        embeddings = self.client.embeddings.create(input=documents, model=embedding_model)
        return [np.array(d.embedding) for d in embeddings.data]

    def chat(self, prompt: str, model: str = 'gpt-3.5-turbo', temperature: float = 0.0, max_tokens: int = 100) -> str:
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return completion.choices[0].message.content


if __name__ == "__main__":
    # Load API key
    api_key = load_openai_api_key("../openai_api_key.json")
    connector = OpenAIConnector(api_key)

    # Embed documents
    documents = ["Hello, world!", "How are you?"]
    embedding_model = "text-embedding-3-small"
    embeddings = connector.embed_documents(documents, embedding_model)
    print(embeddings, embeddings.shape)

    # Chat with GPT-3.5 Turbo
    prompt = "What is the meaning of life?"
    response = connector.chat(prompt)
    print(response)
