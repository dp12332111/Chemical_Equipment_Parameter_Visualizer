import React, { useState, useEffect, useMemo } from 'react';
import { getSummary, getPDF } from '../services/api';
import { useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table'; 
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState('');
  const [authSet, setAuthSet] = useState(false);
  const [fetched, setFetched] = useState(false); // Track if fetched to match desktop's button trigger

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

  const fetchSummary = async () => {
    if (!authSet) return;
    try {
      const response = await getSummary();
      setSummary(response.data);
      setFetched(true);
    } catch (err) {
      setError('Failed to fetch summary: ' + (err.response?.data?.error || err.message));
    }
  };

const downloadPDF = async () => {
  try {
    const res = await getPDF();
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'report.pdf');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    alert('Failed to download PDF: ' + (error.response?.data?.error || error.message));
  }
};

  const data = useMemo(() => {
    if (!summary) return [];
    return [
      { key: 'Total Count', value: summary.total_count },
      { key: 'Average Flowrate', value: summary.avg_flowrate?.toFixed(2) || 'N/A' }, // Added .toFixed and N/A like desktop
      { key: 'Average Pressure', value: summary.avg_pressure?.toFixed(2) || 'N/A' },
      { key: 'Average Temperature', value: summary.avg_temperature?.toFixed(1) || 'N/A' }, // .toFixed(1) to match desktop's temp
      { key: 'Type Distribution', value: summary.type_distribution }, // Changed: Pass raw object; custom cell will stringify
    ];
  }, [summary]);

  // Define columns for the table
  const columns = useMemo(
    () => [
      {
        accessorKey: 'key',
        header: 'Metric',
      },
      {
        accessorKey: 'value',
        header: 'Value',
        cell: ({ getValue }) => {
          const value = getValue();
          // If value is object, stringify and render in pre (matches desktop's str())
          return typeof value === 'object' && value !== null ? (
            <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{JSON.stringify(value, null, 2)}</pre>
          ) : (
            value
          );
        },
      },
    ],
    []
  );

  // Initialize the table instance
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (error) return <p>{error}</p>;
  if (!authSet) return <p>Setting up authentication...</p>;

  return (
    <div>
      <h2>Dashboard Summary</h2>
      <button onClick={fetchSummary} disabled={!authSet}>Fetch Summary</button> {/* Button like desktop */}
      <button onClick={downloadPDF} style={{ marginLeft: '10px' }}>Download PDF Report</button>
      {fetched && summary ? (
        <>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th
                      key={header.id}
                      style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}
                    >
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())} {/* Use flexRender */}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} style={{ border: '1px solid #ddd', padding: '8px' }}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())} {/* Use flexRender to invoke custom cell */}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: '20px', width: '400px' }}>
            <h3>Averages Chart</h3>
            <Bar
              data={{
                labels: ['Flowrate', 'Pressure', 'Temperature'],
                datasets: [{ label: 'Averages', data: [summary.avg_flowrate, summary.avg_pressure, summary.avg_temperature], backgroundColor: '#4a90e2' }]
              }}
              options={{ scales: { y: { beginAtZero: true } } }}
            />
          </div>
        </>
      ) : (
        <p>{fetched ? 'No data available' : 'Click "Fetch Summary" to load data.'}</p>
      )}
    </div>
  );
}

export default Dashboard;