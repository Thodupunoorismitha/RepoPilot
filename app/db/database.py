
import sqlite3
from pathlib import Path


# Get the project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Define the database file location
DATABASE_PATH = BASE_DIR / "app" / "db" / "repopilot.db"

def get_connection():
    """
    Create and return a connection to the SQLite database.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    # Enable foreign-key constraint enforcement
    connection.execute("PRAGMA foreign_keys = ON")

    # Return rows as dictionary-like objects
    connection.row_factory = sqlite3.Row

    return connection

