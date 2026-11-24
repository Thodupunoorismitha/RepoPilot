
from app.db.database import get_connection


class ChunkDB:

    def save_chunks(self, repository_id: int, chunks: list):
        """
        Save code chunks belonging to a repository.
        """

        connection = get_connection()
        cursor = connection.cursor()

        try:
            # Remove previously saved chunks
            cursor.execute(
                """
                DELETE FROM code_chunks
                WHERE repository_id = ?
                """,
                (repository_id,)
            )

            saved_count = 0

            # Insert the latest chunks
            for chunk in chunks:

                cursor.execute(
                    """
                    INSERT INTO code_chunks (
                        repository_id,
                        file_path,
                        symbol_name,
                        chunk_type,
                        start_line,
                        end_line,
                        content
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        repository_id,
                        chunk["file_path"],
                        chunk["symbol_name"],
                        chunk["chunk_type"],
                        chunk["start_line"],
                        chunk["end_line"],
                        chunk["content"]
                    )
                )

                saved_count += 1

            connection.commit()

            return saved_count

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()


    def get_chunks_by_repository(self, repository_id: int):
        """
        Retrieve all code chunks belonging to a repository.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM code_chunks
            WHERE repository_id = ?
            ORDER BY id
            """,
            (repository_id,)
        )

        chunks = cursor.fetchall()

        connection.close()

        return chunks
