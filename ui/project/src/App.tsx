import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './stores/authStore';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Workspaces from './pages/Workspaces';
import DataSources from './pages/DataSources';
import Charts from './pages/Charts';
import Users from './pages/Users';
import Settings from './pages/Settings';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import OnboardingWizard from './components/OnboardingWizard';
import Dashboards from './components/Dashboards';
import Pipelines from './components/Pipelines';
import NotFound from './components/NotFound';
import NavBar from './components/NavBar';

const queryClient = new QueryClient();

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          {!isAuthenticated ? (
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          ) : (
            <Layout>
              <Routes>
              <Route path="/onboarding" element={<OnboardingWizard />} />
        <Route path="/dashboards" element={<Dashboards />} />
        <Route path="/pipelines" element={<Pipelines />} />
        <Route path="/" element={<Navigate to="/onboarding" replace />} />
        <Route path="*" element={<NotFound />} />

                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/workspaces" element={<Workspaces />} />
                <Route path="/data-sources" element={<DataSources />} />
                <Route path="/charts" element={<Charts />} />
                <Route path="/users" element={<Users />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Layout>
          )}
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;




