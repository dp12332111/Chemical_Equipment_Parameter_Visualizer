import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Upload from './pages/Upload';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Visualizations from './pages/Visualizations';
import axios from 'axios';
import './App.css';

function App() {
  const [authSet, setAuthSet] = useState(false);
  const [error, setError] = useState('');
  const isSettingAuth = useRef(false);

  useEffect(() => {
    if (isSettingAuth.current) return;
    isSettingAuth.current = true;

    const validateCredentials = async (username, password) => {
      try {
        const token = btoa(`${username}:${password}`);
        const response = await axios.get('http://localhost:8000/api/summary/', {
          headers: { Authorization: `Basic ${token}` }
        });
        // Any successful response (even if empty data) means creds are valid
        return true;
      } catch (err) {
        // Only consider auth failure if it's explicitly 401 (Unauthorized)
        if (err.response?.status === 401) {
          return false;
        }
        // For other errors (e.g., network issues, 404, 500), do not assume valid
        // Instead, throw or handle as failure to avoid false positives
        console.error('Validation error:', err);
        throw err; // Let the caller handle the error
      }
    };

    const setupAuth = async () => {
      console.log('Auth check running'); // Debug
      let username = localStorage.getItem('username');
      let password = localStorage.getItem('password');

      // If missing or invalid, prompt and validate
      let isValid = false;
      while (!isValid) {
        if (!username || !password) {
          username = prompt('Enter username:');
          password = prompt('Enter password:');
          if (!username || !password) {
            setError('Authentication required. App cannot proceed.');
            return;
          }
        }

        try {
          isValid = await validateCredentials(username, password);
          if (isValid) {
            localStorage.setItem('username', username);
            localStorage.setItem('password', password);
            const token = btoa(`${username}:${password}`);
            axios.defaults.headers.common['Authorization'] = `Basic ${token}`;
            setAuthSet(true);
          } else {
            alert('Invalid credentials. Please try again.');
            username = null; // Force re-prompt
            password = null;
          }
        } catch (err) {
          alert('Error during validation. Please check if the backend is running and try again.');
          username = null; // Force re-prompt on next attempt
          password = null;
        }
      }
    };

    setupAuth();
  }, []);

  if (error) return <div style={{ color: 'red', padding: '40px', textAlign: 'center' }}>{error}</div>;
  if (!authSet) return <div style={{ padding: '40px', textAlign: 'center' }}>Setting up authentication...</div>;

  return (
    <Router>
      <div className="app">
        <nav>
          <ul className="tabs">
            <li><Link to="/upload">Upload</Link></li>
            <li><Link to="/dashboard">Dashboard (Summary)</Link></li>
            <li><Link to="/history">History</Link></li>
            <li><Link to="/visualizations">Visualizations</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/upload" element={<Upload />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="/visualizations" element={<Visualizations />} />
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;