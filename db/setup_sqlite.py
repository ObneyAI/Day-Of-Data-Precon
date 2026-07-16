"""One-command setup for the SQLite Fallback: build db/workshop_catalog.sqlite from
the SAME db/seed_products.json, embedding each Description with the real all-MiniLM-L6-v2
model and storing the Embedding as JSON TEXT (SQLite has no VECTOR type).

Mirrors setup_catalog.py + populate_catalog.py for the mssql Catalog. The Embedding is
stored via `vector_literal` (rounded to 6 decimals) so it matches the value the mssql
VECTOR column holds — keeping SemanticSearch ranking identical (proven by prototype p4).

Run: .venv/bin/python db/setup_sqlite.py
"""
import json
import os
import sqlite3

from embeddings import default_embedder, vector_literal

HERE = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.join(HERE, "seed_products.json")
SQLITE_PATH = os.path.join(HERE, "workshop_catalog.sqlite")

# Mirror of the mssql Products shape; DescriptionEmbedding is JSON TEXT, not VECTOR.
PRODUCTS_TABLE_DDL_SQLITE = (
    "CREATE TABLE Products ("
    "ProductID INTEGER PRIMARY KEY AUTOINCREMENT, "
    "Name TEXT NOT NULL, "
    "Description TEXT NOT NULL, "
    "Category TEXT NOT NULL, "
    "Price REAL NOT NULL, "
    "DescriptionEmbedding TEXT"
    ")"
)


def build_sqlite_mirror(path=SQLITE_PATH, seed_path=SEED_PATH, embedder=default_embedder):
    """Create a fresh SQLite mirror at `path` from the Seed, embedding each
    Description. `embedder(text) -> list[float]` is injected (real default, fake in
    tests). Returns the count of Products loaded."""
    seed = json.load(open(seed_path, encoding="utf-8"))

    # Re-runnable: start from a clean file each time.
    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    try:
        conn.execute(PRODUCTS_TABLE_DDL_SQLITE)
        count = 0
        for p in seed:
            embedding = embedder(p["Description"])
            conn.execute(
                "INSERT INTO Products "
                "(Name, Description, Category, Price, DescriptionEmbedding) "
                "VALUES (?, ?, ?, ?, ?)",
                [p["Name"], p["Description"], p["Category"], p["Price"],
                 vector_literal(embedding)],
            )
            count += 1
        conn.commit()
    finally:
        conn.close()
    return count


def main():
    count = build_sqlite_mirror()
    print(f"Built SQLite Fallback with {count} Products at {SQLITE_PATH}")


if __name__ == "__main__":
    main()
