import React, { useState, useEffect } from 'react';
// import axios from 'axios';

// For demo, use mock data. Replace with axios calls to your backend.
const mockWorkspaces = [
  { id: 1, name: 'Demo Workspace' },
  { id: 2, name: 'Analytics Team' },
];

export default function WorkspaceStep({ onNext }) {
  const [workspaces, setWorkspaces] = useState([]);
  const [selected, setSelected] = useState('');
  const [newName, setNewName] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // axios.get('/workspaces/').then(res => setWorkspaces(res.data));
    setTimeout(() => setWorkspaces(mockWorkspaces), 500); // Simulate API
  }, []);

  const createWorkspace = () => {
    setLoading(true);
    // axios.post('/workspaces/', { name: newName }).then(res => {
    //   onNext(res.data);
    // });
    setTimeout(() => {
      const ws = { id: Math.random(), name: newName };
      setWorkspaces([...workspaces, ws]);
      setSelected(ws.id);
      setLoading(false);
      onNext(ws);
    }, 800);
  };

  return (
    <div>
      <h2>Select or Create Workspace</h2>
      <select value={selected} onChange={e => setSelected(e.target.value)} style={{ width: '100%', marginBottom: 12 }}>
        <option value="">-- Select --</option>
        {workspaces.map(ws => (
          <option key={ws.id} value={ws.id}>{ws.name}</option>
        ))}
      </select>
      <button disabled={!selected} onClick={() => onNext(workspaces.find(ws => ws.id == selected))} style={{ marginBottom: 16 }}>
        Next
      </button>
      <div style={{ marginTop: 16 }}>
        <input placeholder="New workspace name" value={newName} onChange={e => setNewName(e.target.value)} style={{ width: '70%' }} />
        <button onClick={createWorkspace} disabled={!newName || loading} style={{ marginLeft: 8 }}>Create</button>
      </div>
    </div>
  );
} 