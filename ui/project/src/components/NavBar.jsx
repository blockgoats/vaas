import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function NavBar() {
  const { pathname } = useLocation();
  return (
    <nav style={{ padding: 16, background: '#f5f5f5', marginBottom: 24 }}>
      <Link to="/onboarding" style={{ marginRight: 24, fontWeight: pathname === '/onboarding' ? 'bold' : 'normal' }}>Onboarding</Link>
      <Link to="/dashboards" style={{ marginRight: 24, fontWeight: pathname === '/dashboards' ? 'bold' : 'normal' }}>Dashboards</Link>
      <Link to="/pipelines" style={{ fontWeight: pathname === '/pipelines' ? 'bold' : 'normal' }}>Pipelines</Link>
    </nav>
  );
} 