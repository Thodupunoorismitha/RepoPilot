
from app.db.database import get_connection


class SymbolDB:

    def save_symbol(
        self,
        repository_id: int,
        name: str,
        file_path: str,
        start_line: int,
        end_line: int,
        symbol_type: str
    ):
        """
        Save a function or class in the symbols table.
        """

        connection = get_connection()
        cursor = connection.cursor()

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
                name,
                file_path,
                start_line,
                end_line,
                symbol_type
            )
        )

        symbol_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return symbol_id


    def get_symbol(self, symbol_id: int):
        """
        Retrieve a symbol using its ID.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT * FROM symbols
            WHERE id = ?
            """,
            (symbol_id,)
        )

        symbol = cursor.fetchone()

        connection.close()

        return symbol


    def save_symbols_from_analysis(
        self,
        repository_id: int,
        scan_results: list
    ):
        """
        Save all functions and classes from repository analysis.
        """

        connection = get_connection()
        cursor = connection.cursor()

        saved_count = 0

        for file_result in scan_results:

            if file_result["status"] != "success":
                continue

            file_path = file_result["file_path"]
            analysis = file_result["analysis"]

            # Save top-level functions
            for function in analysis["functions"]:

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
                        function["name"],
                        file_path,
                        function["start_line"],
                        function["end_line"],
                        "function"
                    )
                )

                saved_count += 1

            # Save classes
            for class_info in analysis["classes"]:

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
                        class_info["name"],
                        file_path,
                        class_info["start_line"],
                        class_info["end_line"],
                        "class"
                    )
                )

                saved_count += 1

        connection.commit()
        connection.close()

        return saved_count


    def get_symbols_by_repository(self, repository_id: int):
        """
        Retrieve all symbols belonging to a repository.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT * FROM symbols
            WHERE repository_id = ?
            ORDER BY id
            """,
            (repository_id,)
        )

        symbols = cursor.fetchall()

        connection.close()

        return symbols

    
    def find_symbol(self, repository_id: int, name: str, file_path: str):
        """
        Find a symbol using repository, name, and file path.
        """

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM symbols
            WHERE repository_id = ?
            AND name = ?
            AND file_path = ?
            """,
            (repository_id, name, file_path)
        )

        symbol = cursor.fetchone()
        connection.close()

        return symbol

