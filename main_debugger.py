from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "gym_data.db"

def debug_database():
    print("=" * 60)
    print(f"DEBUGGING DATABASE AT: {DB_PATH}")
    print("=" * 60)

    if not DB_PATH.exists():
        print("❌ ERROR: Database file does not exist at this path!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='occupancy_logs';")
    if not cursor.fetchone():
        print("❌ ERROR: Table 'occupancy_logs' does not exist in this database!")
        conn.close()
        return
    print("✅ Table 'occupancy_logs' found.")

    # 2. Total Row Count
    cursor.execute("SELECT COUNT(*) AS total FROM occupancy_logs;")
    total_rows = cursor.fetchone()["total"]
    print(f"📊 Total records in database: {total_rows}")

    if total_rows == 0:
        print("⚠️ DATABASE IS EMPTY! No logs have been recorded yet.")
        conn.close()
        return

    # 3. Check distinct location names
    print("\n--- DISTINCT LOCATION NAMES IN DB ---")
    cursor.execute("SELECT DISTINCT location_name FROM occupancy_logs;")
    locations = [row["location_name"] for row in cursor.fetchall()]
    for loc in locations:
        print(f"  • '{loc}'")

    # 4. Inspect raw timestamp formats (First and Last 3 rows)
    print("\n--- SAMPLE TIMESTAMPS (Most Recent 3 Entries) ---")
    cursor.execute("SELECT id, location_name, last_count, recorded_at FROM occupancy_logs ORDER BY id DESC LIMIT 3;")
    for row in cursor.fetchall():
        print(f"  ID: {row['id']} | Location: '{row['location_name']}' | Count: {row['last_count']} | Timestamp: '{row['recorded_at']}'")

    # 5. Check what SQLite date() sees vs raw string comparison
    print("\n--- TODAY'S DATE EVALUATION ---")
    cursor.execute("SELECT date('now') AS utc_date, date('now', 'localtime') AS local_date;")
    dates = cursor.fetchone()
    print(f"  SQLite date('now'): {dates['utc_date']}")
    print(f"  SQLite date('now', 'localtime'): {dates['local_date']}")

    # 6. Test location matching and today matching
    test_loc = locations[0] if locations else "Level 1 Fitness"
    print(f"\n--- TESTING QUERY FOR LOCATION: '{test_loc}' ---")
    
    # Check matching location count regardless of date
    cursor.execute("SELECT COUNT(*) AS loc_count FROM occupancy_logs WHERE location_name = ?;", (test_loc,))
    print(f"  Total records matching location_name = '{test_loc}': {cursor.fetchone()['loc_count']}")

    # Check matching with LIKE or date functions
    cursor.execute("""
        SELECT recorded_at, last_count 
        FROM occupancy_logs 
        WHERE location_name = ? 
        ORDER BY id DESC LIMIT 5;
    """, (test_loc,))
    print(f"  Recent entries for '{test_loc}':")
    for row in cursor.fetchall():
        print(f"    recorded_at: '{row['recorded_at']}' | count: {row['last_count']}")

    conn.close()
    print("=" * 60)

if __name__ == "__main__":
    debug_database()