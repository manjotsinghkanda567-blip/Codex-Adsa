# Network Connection Analyzer

The existing single-page frontend is in `index.html`. Its device, connection, statistics and graph-analysis data now comes from the FastAPI service backed by SQLite.

## Run locally (Windows PowerShell)

In one terminal, from this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal, serve the frontend over HTTP:

```powershell
py -m http.server 5500
```

Open `http://localhost:5500` and visit `http://localhost:8000/docs` for interactive API documentation. The database is initialized automatically at `backend/network.db` and retains data across restarts. The application starts with an empty database; add devices and connections in the UI.

The API implements CRUD, input validation, uniqueness constraints, cascading connection deletion, statistics and adjacency-list DFS, path finding and connected components. Graph coordinates are stored with each device.
