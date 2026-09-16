import { useState, useEffect } from 'react';
import GraphCard from './GraphCard';

export default function App() {
  const [liveDataMap, setLiveDataMap] = useState({});
  const [apiConnected, setApiConnected] = useState(false);

  const targetLocations = [
    "Nick Level 1 Fitness",
    "Nick Level 2 Fitness",
    "Nick Level 3 Fitness",
    "Nick Power House",
    "Nick Track",
    "Nick Courts 1 & 2",
    "Nick Courts 3-6",
    "Nick Courts 7 & 8",
  ];

  // Fetch live snapshot numbers for all locations
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/occupancy/live')
      .then((res) => {
        if (!res.ok) throw new Error('API network response failed');
        return res.json();
      })
      .then((resData) => {
        setApiConnected(true);
        // Build a lookup object: { "Nick Level 1 Fitness": 85, "Nick Power House": 61, ... }
        const map = {};
        if (resData.data) {
          resData.data.forEach((item) => {
            map[item.location_name] = item.percentage;
          });
        }
        setLiveDataMap(map);
      })
      .catch((error) => {
        console.error('Error connecting to FastAPI backend:', error);
        setApiConnected(false);
      });
  }, []);

  return (
    <div style={{ maxWidth: '750px', margin: '0 auto', padding: '2rem' }}>
      <h1 style={{ color: '#c5050c', textAlign: 'center', marginBottom: '1rem' }}>
        Nick Gym Occupancy Tracker
      </h1>

      <div style={{
        textAlign: 'center',
        marginBottom: '1.5rem',
        fontSize: '0.9rem',
        color: apiConnected ? '#2e7d32' : '#c5050c',
        fontWeight: 'bold'
      }}>
        API Connection Status: {apiConnected ? '🟢 Connected to FastAPI' : '🔴 Disconnected (Check uvicorn)'}
      </div>

      {targetLocations.map((location) => (
        <GraphCard
          key={location}
          locationName={location}
          livePercentage={liveDataMap[location]}
        />
      ))}
    </div>
  );
}