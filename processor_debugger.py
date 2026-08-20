import sqlite3
from datetime import datetime

DB_NAME = "gym_data.db"

def inspect_database():
    """Connects to SQLite and prints summary metrics and recent entries."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # 1. Total row count across the entire table
        cursor.execute("SELECT COUNT(*) FROM occupancy_logs")
        total_rows = cursor.fetchone()[0]

        print("=" * 60)
        print(f" DATABASE SUMMARY ({DB_NAME})")
        print("=" * 60)
        print(f"Total Rows Saved: {total_rows}\n")

        if total_rows == 0:
            print("The occupancy_logs table is currently empty.")
            conn.close()
            return

        # 2. Get the latest recorded entry for each unique location
        print("LATEST SNAPSHOT PER ZONE:")
        print("-" * 60)
        
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
        
        latest_entries = cursor.fetchall()

        for row in latest_entries:
            facility, location, count, capacity, pct, recorded_at = row
            print(f"• [{facility}] {location.ljust(35)} | {str(count).rjust(3)}/{str(capacity).ljust(3)} ({str(pct).rjust(2)}%) | Last Update: {recorded_at}")

        # 3. Frequency check (number of entries logged per zone)
        print("\nENTRY COUNT PER ZONE (Deduplication Check):")
        print("-" * 60)
        cursor.execute('''
            SELECT location_name, COUNT(*) 
            FROM occupancy_logs 
            GROUP BY location_name 
            ORDER BY COUNT(*) DESC
        ''')
        
        counts = cursor.fetchall()
        for loc, num_entries in counts:
            print(f"• {loc.ljust(38)}: {num_entries} row(s)")

        print("=" * 60)
        conn.close()

    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")

if __name__ == "__main__":
    inspect_database()