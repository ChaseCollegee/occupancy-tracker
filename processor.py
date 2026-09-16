import sqlite3
import collector
from datetime import datetime

# Define locations to track
TARGET_LOCATIONS = {
    "Nick Level 1 Fitness",
    "Nick Level 2 Fitness",
    "Nick Level 3 Fitness",
    "Nick Power House",
    "Nick Track",
    "Nick Courts 1 & 2",
    "Nick Courts 3-6",
    "Nick Courts 7 & 8",
    "Nick Soderholm Family Aquatic Center",
}

DB_NAME = "gym_data.db"

def init_db():
    """Ensures the SQL table and index exist before inserting data."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS occupancy_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_name TEXT NOT NULL,
            location_name TEXT NOT NULL,
            last_count INTEGER NOT NULL,
            total_capacity INTEGER NOT NULL,
            percentage INTEGER NOT NULL,
            recorded_at TEXT NOT NULL
        )
    ''')
    
    # Create an index on location_name and recorded_at to make deduplication queries instant
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_location_recorded 
        ON occupancy_logs (location_name, recorded_at)
    ''')
    
    conn.commit()
    conn.close()


def is_new_data(cursor, location_name, new_timestamp):
    """Checks if the API timestamp is strictly newer than the most recent SQL entry for this location."""
    cursor.execute('''
        SELECT recorded_at FROM occupancy_logs 
        WHERE location_name = ? 
        ORDER BY recorded_at DESC LIMIT 1
    ''', (location_name,))
    
    result = cursor.fetchone()
    if result is None:
        return True  # Location hasn't been logged yet
    
    last_saved_timestamp = result[0]
    return new_timestamp > last_saved_timestamp


def process_and_save():
    """Fetches raw data, filters for target locations, checks for fresh timestamps, and saves to SQL."""
    init_db()

    # Get raw JSON payload from collector.py
    raw_data = collector.requestRawData()
    if not raw_data:
        print("No data returned from collector.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    saved_count = 0
    skipped_count = 0

    for item in raw_data:
        location = item.get("LocationName")
        
        # Filter: Only process locations in our target set
        if location in TARGET_LOCATIONS:
            timestamp = item.get("LastUpdatedDateAndTime")
            
            # Deduplication Check
            if is_new_data(cursor, location, timestamp):
                facility = item.get("FacilityName", "").strip()
                count = item.get("LastCount", 0)
                capacity = item.get("TotalCapacity", 0)
                if capacity > 0:
                    percentage = round((count / capacity) * 100)
                else:
                    percentage = 0

                cursor.execute('''
                    INSERT INTO occupancy_logs (facility_name, location_name, last_count, total_capacity, percentage, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (facility, location, count, capacity, percentage, timestamp))
                
                saved_count += 1
            else:
                skipped_count += 1

    conn.commit()
    conn.close()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] Collection complete: {saved_count} new entries saved, {skipped_count} stale entries skipped.")


if __name__ == "__main__":
    process_and_save()