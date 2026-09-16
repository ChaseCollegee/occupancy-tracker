from pathlib import Path
import sqlite3
from fastapi import FastAPI, Query
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

# List of valid target locations tracked in the database
TARGET_LOCATIONS = [
    "Nick Level 1 Fitness",
    "Nick Level 2 Fitness",
    "Nick Level 3 Fitness",
    "Nick Power House",
    "Nick Track",
    "Nick Courts 1 & 2",
    "Nick Courts 3-6",
    "Nick Courts 7 & 8",
    "Nick Soderholm Family Aquatic Center"
]


@app.get("/")
def read_root():
    """Health check endpoint to verify the server is running."""
    return {
        "status": "online", 
        "message": "Nick Gym Occupancy Tracker API",
        "tracked_locations": TARGET_LOCATIONS
    }


@app.get("/api/occupancy/live")
def get_live_occupancy():
    """Fetches the most recent snapshot for each tracked gym location."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

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


@app.get("/api/occupancy/history")
def get_occupancy_history(
    location_name: str = Query(..., description="Target location name, e.g., 'Nick Level 1 Fitness'"),
    timeframe: str = Query("today", description="Options: today, mon, tue, wed, thu, fri, sat, sun")
):
    """
    Returns hourly time-series data for Recharts.
    - 'today': Returns today's actual hourly averages (local time).
    - 'mon'-'sun': Returns historical hourly averages for that specific day of the week.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Map frontend dropdown timeframe keys to SQLite strftime day numbers (0 = Sunday, 1 = Monday, ...)
    day_map = {
        "sun": "0",
        "mon": "1",
        "tue": "2",
        "wed": "3",
        "thu": "4",
        "fri": "5",
        "sat": "6"
    }

    if timeframe == "today":
        # Replace 'T' in ISO timestamps for SQLite parsing & align to local date
        cursor.execute('''
            SELECT 
                strftime('%H', replace(recorded_at, 'T', ' ')) AS hour_24,
                ROUND(AVG(last_count)) AS count
            FROM occupancy_logs
            WHERE location_name = ? 
              AND date(replace(recorded_at, 'T', ' '), 'localtime') = date('now', 'localtime')
            GROUP BY hour_24
            ORDER BY hour_24 ASC
        ''', (location_name,))
    else:
        target_day = day_map.get(timeframe.lower(), "1")
        cursor.execute('''
            SELECT 
                strftime('%H', replace(recorded_at, 'T', ' ')) AS hour_24,
                ROUND(AVG(last_count)) AS count
            FROM occupancy_logs
            WHERE location_name = ? 
              AND strftime('%w', replace(recorded_at, 'T', ' '), 'localtime') = ?
            GROUP BY hour_24
            ORDER BY hour_24 ASC
        ''', (location_name, target_day))

    rows = cursor.fetchall()
    conn.close()

    formatted_data = []
    for row in rows:
        hour_int = int(row["hour_24"])
        if hour_int == 0:
            time_label = "12 AM"
        elif hour_int < 12:
            time_label = f"{hour_int} AM"
        elif hour_int == 12:
            time_label = "12 PM"
        else:
            time_label = f"{hour_int - 12} PM"

        formatted_data.append({
            "time": time_label,
            "count": int(row["count"]) if row["count"] is not None else None
        })

    return {"location": location_name, "timeframe": timeframe, "data": formatted_data}