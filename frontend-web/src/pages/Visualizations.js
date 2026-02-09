import { useState, useEffect } from 'react';
import { Pie, Bar } from 'react-chartjs-2';
import { getSummary } from '../services/api';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import axios from 'axios';

ChartJS.register(ArcElement, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

function Visualizations() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [authSet, setAuthSet] = useState(false);
  const [fetched, setFetched] = useState(false); // Track if fetched

  useEffect(() => {
    const username = localStorage.getItem('username');
    const password = localStorage.getItem('password');
    if (!username || !password) {
      const user = prompt('Enter username:');
      const pass = prompt('Enter password:');
      if (user && pass) {
        localStorage.setItem('username', user);
        localStorage.setItem('password', pass);
        const token = btoa(`${user}:${pass}`);
        axios.defaults.headers.common['Authorization'] = `Basic ${token}`;
        setAuthSet(true);
      } else {
        setError('Authentication required');
        return;
      }
    } else {
      const token = btoa(`${username}:${password}`);
      axios.defaults.headers.common['Authorization'] = `Basic ${token}`;
      setAuthSet(true);
    }
  }, []);

  const fetchData = async () => {
    if (!authSet) return;
    try {
      const response = await getSummary();
      setData(response.data);
      setFetched(true);
    } catch (err) {
      setError('Failed to fetch data: ' + (err.response?.data?.error || err.message));
    }
  };

  if (error) return <p>{error}</p>;
  if (!authSet) return <p>Setting up authentication...</p>;

  // Dynamic colors for pie chart
  const generateColors = (num) => {
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];
    return Array.from({ length: num }, (_, i) => colors[i % colors.length]);
  };

  return (
    <div>
      <h2>Visualizations</h2>
      <button onClick={fetchData} disabled={!authSet}>Generate Visualizations</button> {/* Button like desktop */}
      {fetched && data ? (
        <>
          <div style={{ width: '400px', marginBottom: '20px' }}>
            <h3>Type Distribution</h3>
            <Pie
              data={{
                labels: Object.keys(data.type_distribution ?? {}),
                datasets: [
                  {
                    data: Object.values(data.type_distribution ?? {}),
                    backgroundColor: generateColors(Object.keys(data.type_distribution ?? {}).length),
                  },
                ],
              }}
            />
          </div>
          <div style={{ width: '400px' }}>
            <h3>Averages</h3>
            <Bar
              data={{
                labels: ['Avg Flowrate', 'Avg Pressure', 'Avg Temperature'],
                datasets: [
                  {
                    label: 'Averages',
                    data: [data.avg_flowrate?.toFixed(2) ?? 'N/A', data.avg_pressure?.toFixed(2) ?? 'N/A', data.avg_temperature?.toFixed(1) ?? 'N/A'], // formatting/N/A
                    backgroundColor: '#36A2EB',
                  },
                ],
              }}
            />
          </div>
        </>
      ) : (
        <p>{fetched ? 'No data available' : 'Click "Generate Visualizations" to load data.'}</p>
      )}
    </div>
  );
}

export default Visualizations;