"""Create the read-only `workshop_ro` login for the run_sql Tool (Slice 4).

The real read-only fence: a `db_datareader`-only login the engine physically
prevents from writing (proven in P2). The Tool's SELECT-guard is the friendly
gate in front of this. Idempotent — safe to re-run.

Run: .venv/bin/python db/create_readonly_login.py
"""
import os

import mssql_python
from dotenv import dotenv_values

HERE = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "WorkshopCatalog"
RO_USER, RO_PWD = "workshop_ro", "ReadOnly!2026"


def _conn_string():
    """Read the sa MSSQL_CONN from db/.env, falling back to db/.env.example."""
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


def _exec(conn_str, database, stmts):
    """Run DDL statements (autocommit — P1/P2 finding) on `database`."""
    conn = mssql_python.connect(_with_database(conn_str, database), autocommit=True)
    cur = conn.cursor()
    for s in stmts:
        cur.execute(s)
    conn.close()


def main():
    conn_str = _conn_string()

    # 1) Server-level login on master (drop-and-recreate keeps the password known).
    _exec(conn_str, "master", [
        f"IF SUSER_ID('{RO_USER}') IS NOT NULL DROP LOGIN {RO_USER};",
        f"CREATE LOGIN {RO_USER} WITH PASSWORD = '{RO_PWD}';",
    ])

    # 2) Map the login into WorkshopCatalog as db_datareader ONLY (read-only).
    _exec(conn_str, DB_NAME, [
        f"IF USER_ID('{RO_USER}') IS NOT NULL DROP USER {RO_USER};",
        f"CREATE USER {RO_USER} FOR LOGIN {RO_USER};",
        f"ALTER ROLE db_datareader ADD MEMBER {RO_USER};",
    ])

    print(f"Read-only login '{RO_USER}' ready on {DB_NAME} (db_datareader only).")


if __name__ == "__main__":
    main()
