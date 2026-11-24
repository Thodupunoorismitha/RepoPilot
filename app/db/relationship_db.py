
from app.db.database import get_connection


class RelationshipDB:

    def save_relationship(
        self,
        source_symbol_id: int,
        target_symbol_id: int,
        relationship: str
    ):
        """
        Save a relationship between two symbols.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO relationships (
                source_symbol_id,
                target_symbol_id,
                relationship
            )
            VALUES (?, ?, ?)
            """,
            (
                source_symbol_id,
                target_symbol_id,
                relationship
            )
        )

        relationship_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return relationship_id

    
    def get_relationships(self, source_symbol_id: int):
        """
        Retrieve all relationships originating from a symbol.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                relationships.id,
                relationships.relationship,
                source.name AS source_name,
                target.name AS target_name,
                source.file_path AS source_file,
                target.file_path AS target_file
            FROM relationships

            JOIN symbols AS source
                ON relationships.source_symbol_id = source.id

            JOIN symbols AS target
                ON relationships.target_symbol_id = target.id

            WHERE relationships.source_symbol_id = ?
            """,
            (source_symbol_id,)
        )

        results = cursor.fetchall()

        connection.close()

        return results

