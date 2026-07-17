"""Backend seam for the WorkshopCatalog MCPServer (Slice 7 — the SQLite Fallback).

Two backends expose the SAME four operations the Tools need; the Tools stay
identical and just delegate to `get_backend()`:

- `MssqlBackend` — wraps today's live SQL Server 2025 behavior. Its methods call the
  MODULE-LEVEL seams on `server` (`get_connection`, `get_readonly_connection`,
  `vector_literal`, `build_semantic_sql`, ...) at call time, so the existing unit
  tests that monkeypatch those seams keep passing unchanged. Nothing is stashed at
  import time.
- `SqliteBackend` — the Fallback: a local SQLite file, Embeddings stored as JSON TEXT
  (SQLite has no VECTOR type), ranked in Python by `cosine_distance` (proven
  ranking-identical to VECTOR_DISTANCE by prototype p4). Reads open the connection
  read-only via `sqlite3.connect("file:<path>?mode=ro", uri=True)` — the engine fence.

`get_backend()` selects from the `WORKSHOP_DB` env var (default "mssql").

Each backend method returns a plain shape the Tool renders:
  - `schema_rows()`        -> list of 5-tuples for `serialize_schema`
  - `run_readonly(query)`  -> (columns, rows)
  - `semantic_rank(emb, k)`-> (columns, rows) with columns Name, Category, Price, distance
  - `insert_product(...)`  -> None (performs the write + commit)
"""
import json
import os
import sqlite3
import sys

# The project root holds the `db` package. This module lives in mcp-server/ (imported
# by path), so make the root importable to reuse the shared pure helpers.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.embeddings import cosine_distance  # noqa: E402

DEFAULT_SQLITE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "db",
    "workshop_catalog.sqlite",
)

_SEMANTIC_COLUMNS = ["Name", "Category", "Price", "distance"]


class MssqlBackend:
    """The default backend: today's live SQL Server 2025 behavior, byte-identical.

    Every method reaches the seams through the `server` module AT CALL TIME (lazy
    import) — never stashing references — so unit tests that monkeypatch
    `server.get_connection` / `server.get_readonly_connection` / `server.vector_literal`
    keep working unchanged."""

    def _server(self):
        import server

        return server

    def schema_rows(self):
        server = self._server()
        connection = server.get_connection()
        try:
            return server.fetch_schema_rows(connection)
        finally:
            connection.close()

    def run_readonly(self, query):
        server = self._server()
        connection = server.get_readonly_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            columns = [d[0] for d in cursor.description] if cursor.description else []
            rows = [tuple(r) for r in cursor.fetchall()]
            return columns, rows
        finally:
            connection.close()

    def semantic_rank(self, embedding, top_k):
        server = self._server()
        vec = server.vector_literal(embedding)
        connection = server.get_readonly_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(server.build_semantic_sql(), [top_k, vec])
            columns = [d[0] for d in cursor.description] if cursor.description else []
            rows = [tuple(r) for r in cursor.fetchall()]
            return columns, rows
        finally:
            connection.close()

    def insert_product(self, name, description, category, price, embedding):
        server = self._server()
        vec = server.vector_literal(embedding)
        connection = server.get_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                server.build_insert_product_sql(),
                [name, description, category, price, vec],
            )
            connection.commit()
        finally:
            connection.close()


class SqliteBackend:
    """The Fallback backend: a local SQLite mirror of the Catalog."""

    def __init__(self, path=DEFAULT_SQLITE_PATH):
        self.path = path

    def _readonly_connection(self):
        """Engine-level read-only fence: SQLite opens the file in ?mode=ro, so any
        write is rejected by the engine even if the pure guard were bypassed."""
        return sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)

    def _readwrite_connection(self):
        return sqlite3.connect(self.path)

    def run_readonly(self, query):
        """Run a read-only Query on the ?mode=ro connection; return (columns, rows)."""
        connection = self._readonly_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            columns = [d[0] for d in cursor.description] if cursor.description else []
            rows = [tuple(r) for r in cursor.fetchall()]
            return columns, rows
        finally:
            connection.close()

    def semantic_rank(self, embedding, top_k):
        """Rank every Product by cosine distance (Python, over stored JSON
        Embeddings) to the query Embedding; return the nearest top_k as
        (columns, rows) matching the mssql path's shape."""
        connection = self._readonly_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT Name, Category, Price, DescriptionEmbedding FROM Products"
            )
            scored = []
            for name, category, price, emb_json in cursor.fetchall():
                stored = json.loads(emb_json)
                distance = cosine_distance(embedding, stored)
                scored.append((name, category, price, round(distance, 6)))
        finally:
            connection.close()
        scored.sort(key=lambda r: r[3])
        return list(_SEMANTIC_COLUMNS), scored[:top_k]

    def insert_product(self, name, description, category, price, embedding):
        """Insert a new Product on the read-write connection, storing the
        Embedding as JSON TEXT. Parameterized; commits."""
        connection = self._readwrite_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Products "
                "(Name, Description, Category, Price, DescriptionEmbedding) "
                "VALUES (?, ?, ?, ?, ?)",
                [name, description, category, price, json.dumps(list(embedding))],
            )
            connection.commit()
        finally:
            connection.close()

    def schema_rows(self):
        """Return Products columns as 5-tuples (table, column, data_type,
        max_length, is_nullable) for serialize_schema — mirrors the mssql shape."""
        connection = self._readonly_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("PRAGMA table_info(Products)")
            info = cursor.fetchall()
        finally:
            connection.close()
        rows = []
        for _cid, name, col_type, notnull, _default, _pk in info:
            is_nullable = "NO" if notnull else "YES"
            rows.append(("Products", name, col_type.lower() if col_type else "", None, is_nullable))
        return rows


def get_backend():
    """Select the backend from WORKSHOP_DB (default 'mssql'). Read at call time so
    the Fallback switch honors the current environment (and test monkeypatching).
    An optional WORKSHOP_SQLITE_PATH overrides the SQLite file location."""
    choice = os.environ.get("WORKSHOP_DB", "mssql").strip().lower()
    if choice == "sqlite":
        return SqliteBackend(os.environ.get("WORKSHOP_SQLITE_PATH", DEFAULT_SQLITE_PATH))
    return MssqlBackend()
