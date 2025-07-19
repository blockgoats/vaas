import React from 'react';

export default function SuccessStep() {
  return (
    <div style={{ textAlign: 'center', marginTop: 40 }}>
      <h2>🎉 Your dashboards and pipelines are ready!</h2>
      <a href="/dashboards" style={{
        display: 'inline-block',
        marginTop: 24,
        padding: '12px 32px',
        background: '#1976d2',
        color: '#fff',
        borderRadius: 6,
        textDecoration: 'none',
        fontWeight: 'bold',
        fontSize: 18
      }}>Go to Dashboards</a>
    </div>
  );
} 