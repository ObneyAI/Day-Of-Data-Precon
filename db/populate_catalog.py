"""One-command populate: fill every Product's DescriptionEmbedding VECTOR column
in the live WorkshopCatalog using the real all-MiniLM-L6-v2 embedder.

Run: .venv/bin/python db/populate_catalog.py
"""
import os

import mssql_python
from dotenv import dotenv_values

from embeddings import default_embedder, populate_embeddings

HERE = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "WorkshopCatalog"


def _conn_string():
    """Read MSSQL_CONN from db/.env, falling back to the committed .env.example."""
    for fname in (".env", ".env.example"):
        path = os.path.join(HERE, fname)
        if os.path.exists(path):
            conn = dotenv_values(path).get("MSSQL_CONN")
            if conn:
                return conn
    raise RuntimeError("No MSSQL_CONN found in db/.env or db/.env.example")


def _with_database(conn_str, database):
    """Return conn_str with its Database=... set to `database`."""
    parts = [p for p in conn_str.split(";") if p and not p.lower().startswith("database=")]
    parts.append(f"Database={database}")
    return ";".join(parts) + ";"


def main():
    conn_str = _with_database(_conn_string(), DB_NAME)
    conn = mssql_python.connect(conn_str)  # committing connection (not autocommit)
    count = populate_embeddings(conn, default_embedder)
    conn.close()
    print(f"Populated DescriptionEmbedding for {count} Products in {DB_NAME}.Products")


if __name__ == "__main__":
    main()
