"""One-command setup: create the WorkshopCatalog database, create the Products
table, and load the Seed into the live SQL Server 2025 container.

Run: .venv/bin/python db/setup_catalog.py
"""
import json
import os

import mssql_python
from dotenv import dotenv_values

from catalog import create_table, ensure_database, load_seed

HERE = os.path.dirname(os.path.abspath(__file__))
SEED_PATH = os.path.join(HERE, "seed_products.json")
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
    conn_str = _conn_string()

    # 1) DDL on master needs an autocommit connection (P1 finding).
    admin = mssql_python.connect(_with_database(conn_str, "master"), autocommit=True)
    ensure_database(admin, DB_NAME)
    admin.close()

    # 2) Create the table inside WorkshopCatalog (autocommit — CREATE TABLE is DDL).
    catalog_conn = mssql_python.connect(_with_database(conn_str, DB_NAME), autocommit=True)
    cur = catalog_conn.cursor()
    # Make the setup re-runnable: start from a clean table each time.
    cur.execute("IF OBJECT_ID('Products', 'U') IS NOT NULL DROP TABLE Products;")
    create_table(catalog_conn)
    catalog_conn.close()

    # 3) Load the Seed (parameterized inserts; needs a committing connection).
    seed = json.load(open(SEED_PATH, encoding="utf-8"))
    load_conn = mssql_python.connect(_with_database(conn_str, DB_NAME))
    count = load_seed(load_conn, seed)
    load_conn.close()

    print(f"Loaded {count} Products into {DB_NAME}.Products")


if __name__ == "__main__":
    main()
