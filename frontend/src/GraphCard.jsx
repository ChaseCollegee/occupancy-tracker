import { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, Tooltip, XAxis, YAxis } from 'recharts';
import './GraphCard.css';

export default function GraphCard({ locationName, livePercentage }) {
  const [selectedTimeframe, setSelectedTimeframe] = useState('today');
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  const timeframeOptions = [
    { label: 'Today Only', value: 'today' },
    { label: 'Avg Monday', value: 'mon' },
    { label: 'Avg Tuesday', value: 'tue' },
    { label: 'Avg Wednesday', value: 'wed' },
    { label: 'Avg Thursday', value: 'thu' },
    { label: 'Avg Friday', value: 'fri' },
    { label: 'Avg Saturday', value: 'sat' },
    { label: 'Avg Sunday', value: 'sun' },
  ];

  // Fixed 18-hour skeleton (6 AM to 12 AM)
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

  // Fetch history whenever locationName or selectedTimeframe changes
  useEffect(() => {
    setLoading(true);
    const encodedLocation = encodeURIComponent(locationName);
    
    fetch(`http://127.0.0.1:8000/api/occupancy/history?location_name=${encodedLocation}&timeframe=${selectedTimeframe}`)
      .then((res) => {
        if (!res.ok) throw new Error('Network response failed');
        return res.json();
      })
      .then((resData) => {
        const normalized = normalizeHourlyData(resData.data || []);
        setChartData(normalized);
        setLoading(false);
      })
      .catch((err) => {
        console.error(`Error fetching history for ${locationName}:`, err);
        setChartData(normalizeHourlyData([]));
        setLoading(false);
      });
  }, [locationName, selectedTimeframe]);

  return (
    <div className="graph-card">
      <div className="graph-card-header">
        <div>
          <h3>{locationName}</h3>
          <span className="badge">
            {livePercentage !== null && livePercentage !== undefined 
              ? `${livePercentage}% Full Currently` 
              : 'No Live Data'}
          </span>
        </div>

        <select
          value={selectedTimeframe}
          onChange={(e) => setSelectedTimeframe(e.target.value)}
          className="timeframe-select"
        >
          {timeframeOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="chart-container">
        {loading ? (
          <div style={{ height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>
            Loading history...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={chartData}>
              <XAxis dataKey="time" stroke="#888888" fontSize={11} interval={1} />
              <YAxis stroke="#888888" fontSize={12} domain={[0, 'auto']} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#c5050c"
                strokeWidth={2}
                dot={false}
                connectNulls={true}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}