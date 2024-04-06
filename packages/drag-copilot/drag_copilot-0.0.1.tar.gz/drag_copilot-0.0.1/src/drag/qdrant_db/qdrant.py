import json
from typing import List
import uuid
from abc import abstractmethod

import chromadb
import pandas as pd
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..base.base import Drag

default_ef = embedding_functions.DefaultEmbeddingFunction()


class ChromaDB_VectorStore(Drag):
    def __init__(self, config=None):
        Drag.__init__(self, config=config)

        if config is not None:
            path = config.get("path", ".")
            self.embedding_function = config.get("embedding_function", default_ef)
        else:
            path = "."
            self.embedding_function = default_ef

        self.chroma_client = chromadb.PersistentClient(
            path=path, settings=Settings(anonymized_telemetry=False)
        )
        self.questions_collection = self.chroma_client.get_or_create_collection(
            name="questions", embedding_function=self.embedding_function
        )

    def generate_embedding(self, data: str, **kwargs) -> List[float]:
        embedding = self.embedding_function([data])
        if len(embedding) == 1:
            return embedding[0]
        return embedding

    def add_questions(self, question: str, output: str, **kwargs) -> str:
        question_output_json = json.dumps(
            {
                "question": question,
                "output": output,
            },
            ensure_ascii=False,
        )
        id = str(uuid.uuid4()) + "-question"
        self.questions_collection.add(
            documents=question_output_json,
            embeddings=self.generate_embedding(question_output_json),
            ids=id,
        )
        return id

    def get_training_data(self, **kwargs) -> pd.DataFrame:
        questions_data = self.questions_collection.get()

        df = pd.DataFrame()

        if questions_data is not None:
            # Extract the documents and ids
            documents = [json.loads(doc) for doc in questions_data["documents"]]
            ids = questions_data["ids"]

            # Create a DataFrame
            df_questions = pd.DataFrame(
                {
                    "id": ids,
                    "question": [doc["question"] for doc in documents],
                    "content": [doc["output"] for doc in documents],
                }
            )

            df_questions["training_data_type"] = "question"

            df = pd.concat([df, df_questions])

        return df

    @staticmethod
    def _extract_documents(query_results) -> list:
        """
        Static method to extract the documents from the results of a query.

        Args:
            query_results (pd.DataFrame): The dataframe to use.

        Returns:
            List[str] or None: The extracted documents, or an empty list or single document if an error occurred.
        """
        if query_results is None:
            return []

        if "documents" in query_results:
            documents = query_results["documents"]

            if len(documents) == 1 and isinstance(documents[0], list):
                try:
                    documents = [json.loads(doc) for doc in documents[0]]
                except Exception as e:
                    return documents[0]

            return documents

    def get_similar_questions(self, question: str, **kwargs) -> list:
        return ChromaDB_VectorStore._extract_documents(
            self.questions_collection.query(
                query_texts=[question],
            )
        )