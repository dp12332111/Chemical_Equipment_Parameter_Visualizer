import React, { useState, useEffect, useMemo } from 'react';
import { getHistory } from '../services/api';
import { useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table';
import axios from 'axios';

function History() {
  const [history, setHistory] = useState([]);
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

  const fetchHistory = async () => {
    if (!authSet) return;
    try {
      const response = await getHistory();
      setHistory(response.data);
      setFetched(true);
    } catch (err) {
      setError('Failed to fetch history: ' + (err.response?.data?.error || err.message));
    }
  };

  // Define columns for the table (adjusted for flat structure)
  const columns = useMemo(
    () => [
      {
        accessorKey: 'id',
        header: 'ID',
      },
      {
        accessorKey: 'upload_date',
        header: 'Upload Date',
      },
      {
        accessorKey: 'total_count',
        header: 'Total Count',
      },
      {
        accessorKey: 'avg_flowrate',
        header: 'Avg Flowrate',
        cell: ({ getValue }) => getValue()?.toFixed(2) ?? 'N/A', // ?? for nullish coalescing
      },
      {
        accessorKey: 'avg_pressure',
        header: 'Avg Pressure',
        cell: ({ getValue }) => getValue()?.toFixed(2) ?? 'N/A',
      },
      {
        accessorKey: 'avg_temperature',
        header: 'Avg Temperature',
        cell: ({ getValue }) => getValue()?.toFixed(2) ?? 'N/A', // Matches desktop's .2f
      },
      {
        accessorKey: 'type_distribution',
        header: 'Type Distribution',
        cell: ({ getValue }) => (
          <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
            {JSON.stringify(getValue() ?? 'N/A', null, 2)} {/* Handle N/A like desktop */}
          </pre>
        ),
      },
    ],
    []
  );

  // No transformation needed since data is flat
  const data = useMemo(() => history, [history]);

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
      <h2>Upload History (Last 5)</h2>
      <button onClick={fetchHistory} disabled={!authSet}>Fetch History</button> {/* Button like desktop */}
      {fetched && history.length ? (
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
      ) : (
        <p>{fetched ? 'No history available' : 'Click "Fetch History" to load data.'}</p>
      )}
    </div>
  );
}

export default History;