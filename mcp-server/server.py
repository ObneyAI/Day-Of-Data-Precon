"""WorkshopCatalog MCPServer (Slice 3): the FastMCP scaffold + its first Tool.

`get_schema()` reports the Catalog's tables/columns (name + type) over STDIO so the
Model can write correct T-SQL later. Pure `serialize_schema` is unit-tested with fake
rows; the `connection` seam is injected (real default via `get_connection`, faked/
monkeypatched in tests). S4/S5/S6 add more Tools onto this scaffold.
"""
import os
import re
import sys
from typing import Annotated

from fastmcp import FastMCP

# The project root holds the `db` package (db/embeddings.py). This module lives in
# mcp-server/ (imported by path), so make the root importable to reuse its helpers.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.catalog import validate_product  # noqa: E402
from db.embeddings import default_embedder, vector_literal  # noqa: E402
from backends import get_backend  # noqa: E402

mcp = FastMCP("WorkshopCatalog")

DB_NAME = "WorkshopCatalog"

# Injected seam: text -> 384-float Embedding. Real default (all-MiniLM-L6-v2, lazy);
# a deterministic fake is monkeypatched in unit tests so no model loads.
_embedder = default_embedder


def is_read_only_sql(query: str) -> bool:
    """PURE: True only for a single read-only SELECT (or WITH...SELECT) statement.

    The friendly gate in front of the read-only login. Strips comments, rejects
    multi-statement input, and requires the statement to start with SELECT/WITH."""
    stripped = _strip_sql_comments(query).strip()
    # Reject multi-statement input: a single trailing `;` is fine, an interior one is not.
    if ";" in stripped.rstrip().rstrip(";"):
        return False
    lowered = stripped.lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        return False
    # Defense-in-depth: a statement can START with SELECT/WITH yet still write —
    # `WITH x AS (...) DELETE ...` (CTE-prefixed write) and `SELECT ... INTO t` both do.
    # Reject any write/DDL keyword appearing as a whole word. (The read-only login is the
    # real fence; this errs safe — it may reject a SELECT that mentions such a word in a
    # string literal, which is fine for this read-only catalog Tool.)
    if re.search(
        r"\b(insert|update|delete|drop|alter|create|truncate|exec|execute|"
        r"merge|grant|revoke|into)\b",
        lowered,
    ):
        return False
    return True


def format_rows(columns, rows, max_rows=50) -> str:
    """PURE: compact, LLM-friendly rendering of a result set. Shows a header row,
    each data row as pipe-joined values, and notes truncation past max_rows."""
    if not rows:
        return "Query returned no rows."
    header = " | ".join(str(c) for c in columns)
    shown = rows[:max_rows]
    lines = [header, "-" * len(header)]
    for row in shown:
        lines.append(" | ".join("NULL" if v is None else str(v) for v in row))
    if len(rows) > max_rows:
        lines.append(f"... ({len(rows)} rows total, showing first {max_rows})")
    return "\n".join(lines)


def _strip_sql_comments(sql: str) -> str:
    """Remove /* block */ and -- line comments so they cannot hide a write."""
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n]*", " ", sql)
    return sql

# Enriched schema query: INFORMATION_SCHEMA.COLUMNS reports the VECTOR column as
# DATA_TYPE='vector' with CHARACTER_MAXIMUM_LENGTH=1544 (storage bytes, NOT the
# dimension). The LEFT JOIN to sys.columns pulls the true vector_dimensions (384)
# into the MAX_LENGTH slot so serialize_schema can render "vector(384)".
_SCHEMA_SQL = (
    "SELECT c.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE, "
    "       CASE WHEN c.DATA_TYPE = 'vector' THEN sc.vector_dimensions "
    "            ELSE c.CHARACTER_MAXIMUM_LENGTH END AS MAX_LENGTH, "
    "       c.IS_NULLABLE "
    "FROM INFORMATION_SCHEMA.COLUMNS c "
    "LEFT JOIN sys.columns sc "
    "       ON sc.object_id = OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME) "
    "      AND sc.name = c.COLUMN_NAME "
    "WHERE c.TABLE_NAME = 'Products' "
    "ORDER BY c.ORDINAL_POSITION"
)

_SIZED_TYPES = {"nvarchar", "varchar", "nchar", "char", "varbinary", "binary"}


def serialize_schema(rows):
    """PURE: rows = [(table, column, data_type, max_length, is_nullable), ...]
    -> compact, LLM-friendly text grouped by table. Empty rows -> a clear message."""
    if not rows:
        return "No tables found in the Catalog."
    lines = []
    current_table = None
    for table, column, data_type, max_length, is_nullable in rows:
        if table != current_table:
            lines.append(f"Table: {table}")
            current_table = table
        nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
        lines.append(f"  - {column}: {_format_type(data_type, max_length)} {nullable}")
    return "\n".join(lines)


def _format_type(data_type, max_length):
    """Render a column's SQL type for the Model. VECTOR reports DATA_TYPE='vector'
    with its true dimension supplied in max_length (from sys.columns.vector_dimensions);
    (n)char/(n)varchar/binary carry a length, with -1 meaning MAX."""
    if data_type == "vector" and max_length:
        return f"vector({max_length})"
    if data_type in _SIZED_TYPES and max_length is not None:
        size = "max" if max_length == -1 else max_length
        return f"{data_type}({size})"
    return data_type


def fetch_schema_rows(connection):
    """Thin: run the enriched INFORMATION_SCHEMA query and return plain 5-tuples."""
    cursor = connection.cursor()
    cursor.execute(_SCHEMA_SQL)
    return [tuple(row) for row in cursor.fetchall()]


def _conn_string():
    """Read MSSQL_CONN from mcp-server/.env, then db/.env, then db/.env.example."""
    from dotenv import dotenv_values

    here = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(os.path.dirname(here), "db")
    for path in (
        os.path.join(here, ".env"),
        os.path.join(db_dir, ".env"),
        os.path.join(db_dir, ".env.example"),
    ):
        if os.path.exists(path):
            conn = dotenv_values(path).get("MSSQL_CONN")
            if conn:
                return conn
    raise RuntimeError("No MSSQL_CONN found in mcp-server/.env, db/.env or db/.env.example")


def get_connection():
    """Injected seam: a real read-only connection to the live Catalog. Faked in tests."""
    import mssql_python

    return mssql_python.connect(_conn_string())


def _readonly_conn_string():
    """Read WORKSHOP_RO_CONN from mcp-server/.env, then db/.env, then db/.env.example."""
    from dotenv import dotenv_values

    here = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(os.path.dirname(here), "db")
    for path in (
        os.path.join(here, ".env"),
        os.path.join(db_dir, ".env"),
        os.path.join(db_dir, ".env.example"),
    ):
        if os.path.exists(path):
            conn = dotenv_values(path).get("WORKSHOP_RO_CONN")
            if conn:
                return conn
    raise RuntimeError(
        "No WORKSHOP_RO_CONN found in mcp-server/.env, db/.env or db/.env.example"
    )


def get_readonly_connection():
    """Injected seam: connect as the read-only `workshop_ro` login (db_datareader) —
    the real engine-level fence. The friendly guard runs first; this is the backstop."""
    import mssql_python

    return mssql_python.connect(_readonly_conn_string())


_REJECTION = (
    "Only read-only SELECT queries are allowed. "
    "Rejected: writes, DDL, EXEC, and multi-statement input."
)


def build_semantic_sql() -> str:
    """PURE: the parameterized SemanticSearch ranking Query. Ranks Products by cosine
    VECTOR_DISTANCE against a bound VECTOR(384) param, nearest first. Both TOP and the
    query Vector are parameters (params order: [top_k, vector_literal]) — nothing is
    string-concatenated. Reuses P1's proven CAST(? AS VECTOR(384)) shape."""
    return (
        "SELECT TOP (?) Name, Category, Price, "
        "CAST(VECTOR_DISTANCE('cosine', DescriptionEmbedding, "
        "CAST(? AS VECTOR(384))) AS DECIMAL(9,6)) AS distance "
        "FROM Products ORDER BY distance"
    )


def build_insert_product_sql() -> str:
    """PURE: the parameterized INSERT for a new Product WITH its Embedding. Binds
    Name/Description/Category/Price as scalars and the Embedding through
    CAST(? AS VECTOR(384)) (reusing P1's proven vector-bind shape) — nothing is
    string-concatenated. Params order: [name, description, category, price, vector]."""
    return (
        "INSERT INTO Products "
        "(Name, Description, Category, Price, DescriptionEmbedding) "
        "VALUES (?, ?, ?, ?, CAST(? AS VECTOR(384)))"
    )


@mcp.tool
def run_sql(
    query: Annotated[
        str, "A single read-only SQL SELECT statement to run against the Products catalog"
    ] = "SELECT TOP 5 Name, Category, Price FROM Products ORDER BY Price DESC",
) -> str:
    """Run a read-only SELECT Query against the Catalog and return the rows.

    Only a single SELECT (or WITH...SELECT) statement is allowed; writes, DDL,
    EXEC/MERGE, comment-hidden writes, and multi-statement input are rejected.
    The Tool also connects as a read-only login, so the engine blocks any write
    that slips past the guard."""
    if not is_read_only_sql(query):
        return _REJECTION
    columns, rows = get_backend().run_readonly(query)
    return format_rows(columns, rows)


@mcp.tool
def semantic_search(
    text: Annotated[
        str, "A plain-English description of the kind of product you're looking for"
    ] = "a waterproof jacket for cold hikes",
    top_k: Annotated[int, "How many of the closest-matching products to return"] = 5,
) -> str:
    """Find the Products most similar in MEANING to `text` (SemanticSearch).

    Embeds `text`, then ranks Products by cosine VECTOR_DISTANCE against their
    DescriptionEmbedding and returns the nearest `top_k` as Name, Category, Price,
    distance (smaller distance = more similar). A read against the read-only login."""
    # Guard first: a bad top_k must never reach the model or the DB. (bool is an int
    # subclass but not a sensible count, so exclude it explicitly.)
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError(f"top_k must be a positive integer, got {top_k!r}")
    embedding = _embedder(text)
    columns, rows = get_backend().semantic_rank(embedding, top_k)
    return format_rows(columns, rows)


@mcp.tool
def add_product(
    name: Annotated[str, "The product name"],
    description: Annotated[str, "A sentence or two describing the product; this text is embedded for semantic search"],
    category: Annotated[str, "The product category, e.g. Outdoor, Kitchen, Electronics, Apparel, Office"],
    price: Annotated[float, "The price in dollars; must be greater than 0"],
) -> str:
    """Add a new Product to the Catalog AND embed its Description in one step.

    The ONLY write Tool: it validates the input (Name/Description/Category
    non-empty, Price > 0), embeds the Description into the VECTOR(384) column, and
    inserts a parameterized row on the read-WRITE connection (never `workshop_ro`).
    Contrast with `run_sql`, which is read-only and rejects every write."""
    validate_product(
        {"Name": name, "Description": description, "Category": category, "Price": price}
    )
    embedding = _embedder(description)
    get_backend().insert_product(name, description, category, price, embedding)
    return f"Added product: {name} ({category}, ${price})"


@mcp.tool
def get_schema() -> str:
    """Describe the Catalog's tables and columns (name + SQL type) so you can write
    correct read-only T-SQL. Returns the Products table including its VECTOR column."""
    return serialize_schema(get_backend().schema_rows())


if __name__ == "__main__":
    mcp.run()  # STDIO transport (default)
