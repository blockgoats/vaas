import React, { useEffect, useState } from 'react';
// import axios from 'axios';

const mockStatuses = [
  'Starting...',
  'Connecting to database...',
  'Discovering schema...',
  'Generating dashboards...',
  'Setting up pipelines...',
  'complete',
];

export default function ProgressStep({ jobId, onComplete }) {
  const [status, setStatus] = useState('Starting...');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let idx = 0;
    const interval = setInterval(() => {
      setStatus(mockStatuses[idx]);
      setProgress(Math.round((idx / (mockStatuses.length - 1)) * 100));
      if (mockStatuses[idx] === 'complete') {
        clearInterval(interval);
        setTimeout(onComplete, 800);
      }
      idx++;
    }, 1200);
    return () => clearInterval(interval);
  }, [jobId, onComplete]);

  return (
    <div>
      <h2>Setting up your analytics...</h2>
      <div style={{ margin: '16px 0' }}>{status !== 'complete' ? status : 'Setup complete!'}</div>
      <div style={{ background: '#eee', borderRadius: 4, height: 16, width: '100%', marginBottom: 8 }}>
        <div style={{ width: `${progress}%`, background: '#4caf50', height: '100%', borderRadius: 4, transition: 'width 0.5s' }} />
      </div>
      {status !== 'complete' && <div>{progress}%</div>}
    </div>
  );
} 