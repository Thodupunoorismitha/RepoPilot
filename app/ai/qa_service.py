from pathlib import Path
from app.db.symbol_db import SymbolDB
from app.db.relationship_db import RelationshipDB
from app.ai.gemini_client import GeminiClient
from app.retrieval.retriever import CodeRetriever


class CodeQAService:

    def __init__(self):
        self.retriever = CodeRetriever()
        self.gemini = GeminiClient()
        self.symbol_db = SymbolDB()
        self.relationship_db = RelationshipDB()

    def answer_question(
        self,
        repository_id: int,
        question: str,
        top_k: int = 5
    ):
        """
        Answer repository-related questions using
        retrieved code and Gemini.
        """

        # Step 1: Retrieve relevant code chunks
        retrieved_chunks = self.retriever.retrieve(
            repository_id=repository_id,
            query=question,
            top_k=top_k
        )

        # Step 2: Check whether relevant code was found
        if not retrieved_chunks:
            return {
                "question": question,
                "answer": "I could not find relevant code in this repository to answer your question.",
                "sources": []
            }

        # Step 3: Prepare retrieved code as context
        context_parts = []
        sources = []

        for index, chunk in enumerate(retrieved_chunks, start=1):

            source = {
                "file_path": chunk["file_path"],
                "symbol_name": chunk["symbol_name"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "similarity": chunk["score"]
            }

            sources.append(source)

            # Find the matching symbol in SQLite
            symbol = self.symbol_db.find_symbol(
                repository_id=repository_id,
                name=chunk["symbol_name"],
                file_path=str(Path(chunk["file_path"]).resolve())
            )

            # Retrieve relationships where this symbol is the caller
            relationships = []

            if symbol:
                relationships = self.relationship_db.get_relationships(symbol["id"])

            # Convert relationships into readable context
            dependency_lines = []

            for relationship in relationships:
                dependency_lines.append(
                    f"- {relationship['source_name']} "
                    f"{relationship['relationship']} "
                    f"{relationship['target_name']} "
                    f"(target file: {relationship['target_file']})"
                )

            dependency_context = (
                "\n".join(dependency_lines)
                if dependency_lines
                else "No outgoing dependencies recorded."
            )

            context_parts.append(
                f"""
                Source {index}:
                File: {chunk['file_path']}
                Function/Class: {chunk['symbol_name']}
                Lines: {chunk['start_line']}-{chunk['end_line']}

                Code:
                {chunk['content']}

                Dependencies:
                {dependency_context}
                """
            )

        context = "\n".join(context_parts)


        # Step 4: Construct a grounded prompt
        prompt = f"""
You are RepoPilot, an expert Python code analysis assistant.

Answer the user's question using ONLY the source code
provided in the context below.

Rules:
1. Do not invent functions, classes, or code behavior.
2. If the context does not contain enough information,
   clearly state that.
3. Explain the code in simple, understandable language.
4. When describing implementation details, mention
   the relevant file path and line numbers.
5. Distinguish between what the code actually does
   and what cannot be determined from the available code.

Retrieved Code Context:
{context}

User Question:
{question}

Provide a clear and structured answer.
"""

        # Step 5: Generate an answer using Gemini
        answer = self.gemini.generate_response(prompt)

        # Step 6: Return the answer with source references
        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }

