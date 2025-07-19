import React, { useState } from 'react';
// import axios from 'axios';

export default function DatabaseStep({ workspace, onNext }) {
  const [form, setForm] = useState({ type: 'postgres', host: '', port: 5432, username: '', password: '', database: '' });
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const testConnection = () => {
    setTesting(true);
    setError('');
    setSuccess(false);
    // axios.post('/databases/test', { ...form, workspace_id: workspace.id })
    //   .then(() => setSuccess(true))
    //   .catch(() => setError('Failed to connect'))
    //   .finally(() => setTesting(false));
    setTimeout(() => {
      if (form.host && form.username && form.password && form.database) {
        setSuccess(true);
        setError('');
      } else {
        setError('Failed to connect');
        setSuccess(false);
      }
      setTesting(false);
    }, 800);
  };

  const connectDatabase = () => {
    // axios.post('/databases/', { ...form, workspace_id: workspace.id })
    //   .then(res => onNext(res.data.job_id));
    setTimeout(() => {
      onNext('mock-job-id-123');
    }, 1000);
  };

  return (
    <div>
      <h2>Connect Data Source</h2>
      <div style={{ marginBottom: 8 }}>
        <label>DB Type: </label>
        <select name="type" value={form.type} onChange={handleChange}>
          <option value="postgres">PostgreSQL</option>
          <option value="mysql">MySQL</option>
          <option value="sqlite">SQLite</option>
          <option value="mssql">SQL Server</option>
        </select>
      </div>
      <input name="host" value={form.host} onChange={handleChange} placeholder="Host" style={{ width: '100%', marginBottom: 8 }} />
      <input name="port" value={form.port} onChange={handleChange} placeholder="Port" style={{ width: '100%', marginBottom: 8 }} />
      <input name="username" value={form.username} onChange={handleChange} placeholder="Username" style={{ width: '100%', marginBottom: 8 }} />
      <input name="password" type="password" value={form.password} onChange={handleChange} placeholder="Password" style={{ width: '100%', marginBottom: 8 }} />
      <input name="database" value={form.database} onChange={handleChange} placeholder="Database" style={{ width: '100%', marginBottom: 8 }} />
      <div style={{ marginBottom: 8 }}>
        <button onClick={testConnection} disabled={testing}>Test Connection</button>
        <button onClick={connectDatabase} style={{ marginLeft: 8 }}>Next</button>
      </div>
      {success && <div style={{ color: 'green' }}>Connection successful!</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </div>
  );
} 