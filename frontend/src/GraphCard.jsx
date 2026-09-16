import { useState } from 'react';
import { ResponsiveContainer, LineChart, Line, Tooltip, XAxis, YAxis } from 'recharts';
import './GraphCard.css';

export default function GraphCard({ title, percentage, timeframeData }) {
  // 1. Local state so each card manages its own timeframe independently
  const [selectedTimeframe, setSelectedTimeframe] = useState('today');

  // Timeframe dropdown options
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

  // 2. Select the specific array of data matching the chosen dropdown option
  const activeData = timeframeData[selectedTimeframe] || [];

  return (
    <div className="graph-card">
      <div className="graph-card-header">
        <div>
          <h3>{title}</h3>
          <span className="badge">{percentage}% Full Currently</span>
        </div>

        {/* Local Dropdown Menu */}
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

      {/* Chart displaying active timeframe data */}
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={activeData}>
            <XAxis 
              dataKey="time" 
              stroke="#888888" 
              fontSize={11} 
              interval={1} /* Shows every 2nd hour (6 AM, 8 AM, 10 AM...) so labels fit */
            />
            <YAxis stroke="#888888" fontSize={12} domain={[0, 100]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#c5050c"
              strokeWidth={2}
              dot={false}
              connectNulls={true} /* Connects existing data points smoothly across null gaps */
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}