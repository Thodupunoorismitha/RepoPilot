
from pathlib import Path

from app.db.database import get_connection


class RepositoryPersistence:

    def save_analysis(
        self,
        repo_path: str,
        scan_results: list,
        graph_builder
    ):
        """
        Save complete repository analysis in one transaction.
        """

        # Normalize repository path
        repo_path = str(Path(repo_path).resolve())
        
        connection = get_connection()
        cursor = connection.cursor()

        try:

            # Step 1: Find or create repository
            cursor.execute(
                """
                SELECT id FROM repositories
                WHERE repo_path = ?
                """,
                (repo_path,)
            )

            repository = cursor.fetchone()

            if repository:
                repository_id = repository["id"]

            else:
                cursor.execute(
                    """
                    INSERT INTO repositories (repo_path)
                    VALUES (?)
                    """,
                    (repo_path,)
                )

                repository_id = cursor.lastrowid

            # Step 2: Delete previous relationships
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

            # Step 3: Delete previous symbols
            cursor.execute(
                """
                DELETE FROM symbols
                WHERE repository_id = ?
                """,
                (repository_id,)
            )

            # Step 4: Insert new symbols
            symbol_id_map = {}

            for file_result in scan_results:

                if file_result["status"] != "success":
                    continue

                file_path = file_result["file_path"]
                analysis = file_result["analysis"]

                functions = analysis["functions"]
                classes = analysis["classes"]

                for symbol_type, items in [
                    ("function", functions),
                    ("class", classes)
                ]:

                    for item in items:

                        cursor.execute(
                            """
                            INSERT INTO symbols (
                                repository_id,
                                name,
                                file_path,
                                start_line,
                                end_line,
                                type
                            )
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                repository_id,
                                item["name"],
                                file_path,
                                item["start_line"],
                                item["end_line"],
                                symbol_type
                            )
                        )

                        database_symbol_id = cursor.lastrowid

                        normalized_path = Path(file_path).as_posix()

                        graph_node_id = (
                            f"{normalized_path}:{item['name']}"
                        )

                        symbol_id_map[graph_node_id] = database_symbol_id

            # Step 5: Insert graph relationships
            graph = graph_builder.graph

            relationships_saved = 0

            for source_node, target_node, edge_data in graph.edges(data=True):

                source_id = symbol_id_map.get(source_node)
                target_id = symbol_id_map.get(target_node)

                if source_id is None or target_id is None:
                    continue

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
                        source_id,
                        target_id,
                        edge_data.get("relationship", "calls")
                    )
                )

                relationships_saved += 1

            # Step 6: Commit all changes
            connection.commit()

            return {
                "repository_id": repository_id,
                "symbols_saved": len(symbol_id_map),
                "relationships_saved": relationships_saved
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()
