"""Embedding helpers for the WorkshopCatalog.

Pure logic (`vector_literal`) and the VECTOR-column populate step live here so
they stay unit-testable with a fake embedder + fake connection — no model load,
no DB. `default_embedder` wraps the real all-MiniLM-L6-v2 model (lazily loaded).
"""
import json
import math

VECTOR_DIM = 384


def cosine_distance(a, b):
    """PURE: cosine distance between two Embeddings, matching SQL Server 2025's
    VECTOR_DISTANCE('cosine', ...) semantics — parallel -> 0, orthogonal -> 1,
    opposite -> 2. Magnitude-independent. This is the SQLite Fallback's ranker
    (proven ranking-identical to VECTOR_DISTANCE by prototype p4)."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return 1.0 - dot / (na * nb)


def vector_literal(floats):
    """Format 384 numbers as the JSON-array string SQL Server's VECTOR expects."""
    values = list(floats)
    if len(values) != VECTOR_DIM:
        raise ValueError(f"Embedding must have exactly {VECTOR_DIM} numbers, got {len(values)}")
    try:
        return json.dumps([round(float(x), 6) for x in values])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Embedding elements must all be numeric: {exc}") from exc


_SELECT_PRODUCTS_SQL = "SELECT ProductID, Description FROM Products"
_UPDATE_EMBEDDING_SQL = (
    f"UPDATE Products SET DescriptionEmbedding = CAST(? AS VECTOR({VECTOR_DIM})) "
    "WHERE ProductID = ?"
)


def populate_embeddings(connection, embedder):
    """Embed each Product's Description and UPDATE its VECTOR column.

    `embedder(text) -> list[float]` (length 384) is injected (real default,
    faked in tests). Parameterized UPDATEs only. Returns the count updated.
    """
    cursor = connection.cursor()
    cursor.execute(_SELECT_PRODUCTS_SQL)
    rows = cursor.fetchall()
    count = 0
    for product_id, description in rows:
        embedding = embedder(description)
        cursor.execute(_UPDATE_EMBEDDING_SQL, [vector_literal(embedding), product_id])
        count += 1
    connection.commit()
    return count


_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None


def _get_model():
    """Lazily load the sentence-transformers model (heavy import kept out of
    module import so unit tests never touch it)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def default_embedder(text):
    """Real embedder: text -> 384-float Embedding via all-MiniLM-L6-v2."""
    return _get_model().encode(text).tolist()
