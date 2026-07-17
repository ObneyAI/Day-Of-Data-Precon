# WorkshopCatalog MCPServer

The FastMCP program that exposes the Catalog's Tools to the Client (Claude Desktop) over
STDIO. Slice 3 ships the scaffold plus its first Tool, `get_schema`, which describes the
`Products` table's columns and types (including the `DescriptionEmbedding vector(384)`
column) so the Model can write correct read-only T-SQL.

## Tools

- **`get_schema()`** — returns the Catalog's tables/columns (name + SQL type), e.g.

  ```
  Table: Products
    - ProductID: int NOT NULL
    - Name: nvarchar(200) NOT NULL
    - Description: nvarchar(max) NOT NULL
    - Category: nvarchar(100) NOT NULL
    - Price: decimal NOT NULL
    - DescriptionEmbedding: vector(384) NULL
  ```

## Connection

The server reads `MSSQL_CONN` from `mcp-server/.env`, then `db/.env`, then the committed
`db/.env.example`. The live `dod-sql` container string is:

```
Server=localhost,1433;Database=WorkshopCatalog;UID=sa;PWD=Workshop!2026Pass;Encrypt=yes;TrustServerCertificate=yes
```

## Run over STDIO

```bash
# from the repo root, with your .venv active:
python mcp-server/server.py
```

## MCP Inspector

Launch the Inspector against the server (STDIO):

```bash
# from the repo root, with your .venv active:
npx @modelcontextprotocol/inspector python mcp-server/server.py
```

Then in the Inspector UI: connect, open **Tools**, list `get_schema`, and **Run** it — you
should see the `Products` schema above returned from the live Catalog.

## Claude Desktop (STDIO)

Add this to `claude_desktop_config.json`
(`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS), then restart
Claude Desktop. The `WorkshopCatalog` server's `get_schema` Tool will appear.

```json
{
  "mcpServers": {
    "WorkshopCatalog": {
      "command": "/full/path/to/.venv/bin/python",
      "args": [
        "/full/path/to/mcp-server/server.py"
      ]
    }
  }
}
```
