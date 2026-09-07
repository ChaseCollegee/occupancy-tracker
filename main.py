from pathlib import Path
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Rec Well Occupancy Tracker API")

# Enable CORS for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamically resolve the absolute path to gym_data.db in the same directory as main.py
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "gym_data.db"


@app.get("/")
def read_root():
    """Health check endpoint to verify the server is running."""
    return {"status": "online", "message": "Nick & Bakke Occupancy Tracker API"}


@app.get("/api/occupancy/live")
def get_live_occupancy():
    """Fetches the most recent snapshot for each tracked gym location."""
    # Connect using the absolute path to avoid running into empty database creation issues
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query using the exact table name defined in processor.py ('occupancy_logs')
    cursor.execute('''
        SELECT facility_name, location_name, last_count, total_capacity, percentage, recorded_at
        FROM occupancy_logs
        WHERE id IN (
            SELECT MAX(id) 
            FROM occupancy_logs
            GROUP BY location_name
        )
        ORDER BY facility_name, location_name
    ''')

    rows = cursor.fetchall()
    conn.close()

    results = [dict(row) for row in rows]
    return {"count": len(results), "data": results}