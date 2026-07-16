# AI for the Rest of Us — Workshop Files 🛠️
### Day of Data BR Pre-Con

Welcome! These are the files you'll work with during the workshop. Your instructor drives the day from the
slides — this repo is *your* working copy. You'll load a small database, run a couple of notebooks, and then
**build your own AI tool** that talks to that database.

---

## 1. Turn on your environment
You installed the tools + a Python environment ahead of time. Activate that environment (the `.venv` you built),
then confirm it's on:

```bash
# Mac — point this at wherever you made your dod-workshop folder
source ~/Documents/dod-workshop/.venv/bin/activate
# Windows (PowerShell)
#   ...\dod-workshop\.venv\Scripts\activate

python -c "import fastmcp, mssql_python, sentence_transformers; print('ready')"
```
Didn't finish the pre-work? The full step-by-step install guide is in **[`SETUP.md`](SETUP.md)**, and there's a no-Docker backup so nobody's stuck.

## 2. Load your catalog (once, in a terminal)
```bash
python db/setup_catalog.py           # create WorkshopCatalog + 70 sample Products
python db/populate_catalog.py        # embed each product description into the VECTOR column
python db/create_readonly_login.py   # create the read-only DB login you'll use in Module 5
```
> **No Docker?** Instead run `python db/setup_sqlite.py` and set `WORKSHOP_DB=sqlite`. Same results, no container.

## 3. Follow along
📊 **The lesson slides are in [`lesson-slides/`](lesson-slides/)** — open `welcome.html`, `m3.html`, and `mcp.html`
in your browser to follow along at your own pace (arrow keys / number keys to navigate).

Launch Jupyter Lab (`jupyter lab`) and open the notebooks in `modules/`:

- **Module 1 — Vectors & Embeddings** → `modules/M1_embeddings.ipynb`
- **Module 2 — SQL Server 2025 as a Vector Store** → `modules/M2_vector_store.ipynb`
- **Module 3 — Vibe Coding** → you'll build a tiny browser extension with Claude Code in a *fresh* folder (follow the screen).
- **Modules 4 & 5 — MCP** → you'll **build your own MCP server** with Claude Code so an AI can query this database in
  plain English. Everything your server needs to connect and search is in `db/` (below). Follow the instructor's slides.

---

## What's in `db/`
| File | What it is |
|------|-----------|
| `seed_products.json` | the 70 sample products |
| `setup_catalog.py` · `populate_catalog.py` | create + fill the SQL Server catalog |
| `setup_sqlite.py` | the no-Docker backup catalog |
| `create_readonly_login.py` | the read-only login your `run_sql` tool uses |
| `catalog.py` · `embeddings.py` | helper functions your MCP server can reuse (embeddings, vector formatting) |
| `ssms_demo.sql` | semantic search as pure SQL |
| `.env.example` | the database connection-string template |

You're going to build something real today. Have fun. 🚀
