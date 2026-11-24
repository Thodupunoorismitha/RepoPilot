
from app.db.database import get_connection


def initialize_database():
    """
    Create all required database tables.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # Table 1: Repositories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_path TEXT NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table 2: Symbols
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            start_line INTEGER,
            end_line INTEGER,
            type TEXT NOT NULL,

            FOREIGN KEY (repository_id)
                REFERENCES repositories(id)
        )
    """)

    # Table 3: Relationships
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_symbol_id INTEGER NOT NULL,
            target_symbol_id INTEGER NOT NULL,
            relationship TEXT NOT NULL,

            FOREIGN KEY (source_symbol_id)
                REFERENCES symbols(id),

            FOREIGN KEY (target_symbol_id)
                REFERENCES symbols(id)
        )
    """)

    # Table 4: Code chunks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS code_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            symbol_name TEXT NOT NULL,
            chunk_type TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            content TEXT NOT NULL,

            FOREIGN KEY (repository_id)
                REFERENCES repositories(id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database tables created successfully!")
