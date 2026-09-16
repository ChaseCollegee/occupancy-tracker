import { useState, useEffect } from 'react';
import GraphCard from './GraphCard';

export default function App() {
  // 1. Declare state for API data and loading status
  const [livePercentage, setLivePercentage] = useState(80);
  const [apiConnected, setApiConnected] = useState(false);

  // Fixed 18-hour skeleton generator
  function normalizeHourlyData(actualPoints = []) {
    const fullDayHours = [
      '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', '12 PM', 
      '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', 
      '8 PM', '9 PM', '10 PM', '11 PM', '12 AM'
    ];

    return fullDayHours.map(hour => {
      const match = actualPoints.find(p => p.time === hour);
      return {
        time: hour,
        count: match ? match.count : null
      };
    });
  }

  // 2. Fetch live data from FastAPI when component mounts
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/occupancy/live')
      .then((res) => {
        if (!res.ok) throw new Error('API network response failed');
        return res.json();
      })
      .then((data) => {
        console.log('Successfully fetched API data:', data);
        setApiConnected(true);
        
        if (data.percentage) {
          setLivePercentage(data.percentage);
        }
      })
      .catch((error) => {
        console.error('Error connecting to FastAPI backend:', error);
        setApiConnected(false);
      });
  }, []);

  // Existing mock time-series data structure
  const nickLevel1Data = {
    today: normalizeHourlyData([
      { time: '6 AM', count: 10 },
      { time: '7 AM', count: 20 },
      { time: '8 AM', count: 35 },
      { time: '9 AM', count: 50 },
      { time: '10 AM', count: 65 },
      { time: '11 AM', count: 75 },
      { time: '12 PM', count: 85 },
      { time: '1 PM', count: 80 },
    ]),
    mon: normalizeHourlyData([
      { time: '6 AM', count: 15 },
      { time: '8 AM', count: 40 },
      { time: '12 PM', count: 70 },
      { time: '4 PM', count: 85 },
      { time: '8 PM', count: 50 },
    ]),
  };

  return (
    <div style={{ maxWidth: '750px', margin: '0 auto', padding: '2rem' }}>
      <h1 style={{ color: '#c5050c', textAlign: 'center', marginBottom: '1rem' }}>
        Nick Gym Occupancy Tracker
      </h1>

      {/* Quick connection verification banner */}
      <div style={{
        textAlign: 'center',
        marginBottom: '1.5rem',
        fontSize: '0.9rem',
        color: apiConnected ? '#2e7d32' : '#c5050c',
        fontWeight: 'bold'
      }}>
        API Connection Status: {apiConnected ? '🟢 Connected to FastAPI' : '🔴 Disconnected (Check uvicorn)'}
      </div>

      <GraphCard
        title="Nick — Level 1 Fitness"
        percentage={livePercentage}
        timeframeData={nickLevel1Data}
      />
    </div>
  );
}