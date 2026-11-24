
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from app.db.chunk_db import ChunkDB


class CodeRetriever:

    def __init__(self):
        self.chunk_db = ChunkDB()

    def retrieve(
        self,
        repository_id: int,
        query: str,
        top_k: int = 5
    ):
        """Retrieve relevant code chunks using TF-IDF similarity."""

        chunks = self.chunk_db.get_chunks_by_repository(
            repository_id
        )

        if not chunks or not query.strip() or top_k <= 0:
            return []

        # Combine symbol names and source code
        documents = [
            re.sub(
                r"_",
                " ",
                chunk["symbol_name"] + "\n" + chunk["content"]
            )
            for chunk in chunks
        ]

        # Convert code chunks into TF-IDF vectors
        vectorizer = TfidfVectorizer(lowercase=True)

        try:
            chunk_vectors = vectorizer.fit_transform(documents)
        except ValueError:
            return []

        # Convert the user's query into a TF-IDF vector
        query = query.replace("_", " ")
        query_vector = vectorizer.transform([query])

        # Calculate similarity between query and every chunk
        similarity_scores = cosine_similarity(
            query_vector,
            chunk_vectors
        ).flatten()

        results = []

        for index, score in enumerate(similarity_scores):

            if score > 0:
                chunk = chunks[index]

                results.append({
                    "symbol_name": chunk["symbol_name"],
                    "file_path": chunk["file_path"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "content": chunk["content"],
                    "score": float(score)
                })

        # Highest similarity first
        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]
