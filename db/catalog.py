"""Catalog schema + Seed loader for the WorkshopCatalog database.

Pure logic (validation, INSERT building) is testable with a fake connection;
real DDL/DML runs against the live SQL Server 2025 container via mssql-python.
"""


PRODUCTS_TABLE_DDL = (
    "CREATE TABLE Products ("
    "ProductID INT IDENTITY PRIMARY KEY, "
    "Name NVARCHAR(200) NOT NULL, "
    "Description NVARCHAR(MAX) NOT NULL, "
    "Category NVARCHAR(100) NOT NULL, "
    "Price DECIMAL(10,2) NOT NULL, "
    "DescriptionEmbedding VECTOR(384) NULL"
    ")"
)


def validate_product(p):
    """Raise ValueError if a Product dict is malformed; otherwise return None."""
    for field in ("Name", "Description", "Category"):
        value = p.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Product {field} must be a non-empty string")

    price = p.get("Price")
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise ValueError("Product Price must be a number")
    if price <= 0:
        raise ValueError("Product Price must be greater than 0")
    return None


# INSERT omits DescriptionEmbedding on purpose — it stays NULL this slice (S2 populates it).
_INSERT_PRODUCT_SQL = (
    "INSERT INTO Products (Name, Description, Category, Price) VALUES (?, ?, ?, ?)"
)


def load_seed(connection, products):
    """Validate each Product, parameterized-INSERT it, commit, return the count."""
    cursor = connection.cursor()
    count = 0
    for p in products:
        validate_product(p)
        cursor.execute(
            _INSERT_PRODUCT_SQL,
            [p["Name"], p["Description"], p["Category"], p["Price"]],
        )
        count += 1
    connection.commit()
    return count


def ensure_database(admin_connection, name="WorkshopCatalog"):
    """Create the Catalog database if it is absent. DDL requires an autocommit
    connection opened on `master` (P1 finding) — the caller supplies it."""
    cursor = admin_connection.cursor()
    # Guard the identifier: only a simple database name is allowed here.
    if not name.isidentifier():
        raise ValueError(f"Invalid database name: {name!r}")
    cursor.execute(f"IF DB_ID('{name}') IS NULL CREATE DATABASE {name};")


def create_table(connection):
    """Create the Products table in the already-selected WorkshopCatalog database."""
    cursor = connection.cursor()
    cursor.execute(PRODUCTS_TABLE_DDL)
