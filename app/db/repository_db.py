
from app.db.database import get_connection


class RepositoryDB:

    def get_repository(self, repository_id: int):
        """
        Retrieve repository information using its ID.
        """

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT * FROM repositories
            WHERE id = ?
            """,
            (repository_id,)
        )

        repository = cursor.fetchone()

        connection.close()

        return repository


    def save_repository(self, repo_path: str):
        """
        Save a repository if it doesn't exist.
        Otherwise, return its existing ID.
        """

        connection = get_connection()
        cursor = connection.cursor()

        # Check whether the repository already exists
        cursor.execute(
            """
            SELECT id FROM repositories
            WHERE repo_path = ?
            """,
            (repo_path,)
        )

        existing_repository = cursor.fetchone()

        if existing_repository:
            repository_id = existing_repository["id"]

        else:
            cursor.execute(
                """
                INSERT INTO repositories (repo_path)
                VALUES (?)
                """,
                (repo_path,)
            )

            repository_id = cursor.lastrowid

            connection.commit()

        connection.close()

        return repository_id

    
    def clear_repository_data(self, repository_id: int):
        """
        Remove previous relationships and symbols
        belonging to a repository.
        """

        connection = get_connection()
        cursor = connection.cursor()

        # Delete relationships involving this repository's symbols
        cursor.execute(
            """
            DELETE FROM relationships
            WHERE source_symbol_id IN (
                SELECT id FROM symbols
                WHERE repository_id = ?
            )
            OR target_symbol_id IN (
                SELECT id FROM symbols
                WHERE repository_id = ?
            )
            """,
            (repository_id, repository_id)
        )

        # Delete the repository's symbols
        cursor.execute(
            """
            DELETE FROM symbols
            WHERE repository_id = ?
            """,
            (repository_id,)
        )

        connection.commit()
        connection.close()

