# Backend

Python 3.10+ and SQLite backend. From the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The SQLite database is created automatically at `backend/network.db`; `/docs` hosts interactive OpenAPI documentation. The API exposes device and connection CRUD, statistics, graph data and manual adjacency-list DFS, path, and connected-component algorithms. The static frontend should be opened over HTTP (for example `py -m http.server 5500`) and connects to `http://localhost:8000`.
