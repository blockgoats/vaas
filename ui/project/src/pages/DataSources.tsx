import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Database, Wifi, WifiOff, MoreVertical, TestTube } from 'lucide-react';

const dataSources = [
  {
    id: '1',
    name: 'Production PostgreSQL',
    type: 'PostgreSQL',
    host: 'prod-db.company.com',
    status: 'connected',
    lastTest: '2 minutes ago',
    tables: 45,
  },
  {
    id: '2',
    name: 'Analytics Warehouse',
    type: 'Snowflake',
    host: 'xy12345.snowflakecomputing.com',
    status: 'connected',
    lastTest: '5 minutes ago',
    tables: 23,
  },
  {
    id: '3',
    name: 'Marketing Data',
    type: 'BigQuery',
    host: 'bigquery.googleapis.com',
    status: 'error',
    lastTest: '1 hour ago',
    tables: 12,
  },
  {
    id: '4',
    name: 'Customer MySQL',
    type: 'MySQL',
    host: 'customer-db.internal',
    status: 'connected',
    lastTest: '10 minutes ago',
    tables: 18,
  },
];

export default function DataSources() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDataSource, setNewDataSource] = useState({
    name: '',
    type: 'PostgreSQL',
    host: '',
    port: '5432',
    database: '',
    username: '',
    password: '',
  });

  const testConnection = (id: string) => {
    // Simulate connection test
    console.log('Testing connection for:', id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Sources</h1>
          <p className="text-gray-600">Connect and manage your database connections</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Data Source
        </motion.button>
      </div>

      {/* Data Sources List */}
      <div className="space-y-4">
        {dataSources.map((source, index) => (
          <motion.div
            key={source.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-secondary-100 rounded-xl flex items-center justify-center">
                  <Database className="w-6 h-6 text-secondary-600" />
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{source.name}</h3>
                  <p className="text-sm text-gray-600">{source.type} • {source.host}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="flex items-center space-x-2">
                    {source.status === 'connected' ? (
                      <Wifi className="w-4 h-4 text-success-500" />
                    ) : (
                      <WifiOff className="w-4 h-4 text-error-500" />
                    )}
                    <span className={`text-sm font-medium ${
                      source.status === 'connected' ? 'text-success-600' : 'text-error-600'
                    }`}>
                      {source.status === 'connected' ? 'Connected' : 'Error'}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">Last test: {source.lastTest}</p>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => testConnection(source.id)}
                    className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                    title="Test Connection"
                  >
                    <TestTube className="w-4 h-4 text-gray-600" />
                  </button>
                  <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
                    <MoreVertical className="w-4 h-4 text-gray-600" />
                  </button>
                </div>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Tables:</span>
                  <span className="ml-2 font-medium text-gray-900">{source.tables}</span>
                </div>
                <div>
                  <span className="text-gray-500">Type:</span>
                  <span className="ml-2 font-medium text-gray-900">{source.type}</span>
                </div>
                <div>
                  <span className="text-gray-500">Status:</span>
                  <span className={`ml-2 font-medium ${
                    source.status === 'connected' ? 'text-success-600' : 'text-error-600'
                  }`}>
                    {source.status === 'connected' ? 'Active' : 'Error'}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Create Data Source Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Data Source</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  value={newDataSource.name}
                  onChange={(e) => setNewDataSource({ ...newDataSource, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Production Database"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Database Type
                </label>
                <select
                  value={newDataSource.type}
                  onChange={(e) => setNewDataSource({ ...newDataSource, type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="PostgreSQL">PostgreSQL</option>
                  <option value="MySQL">MySQL</option>
                  <option value="Snowflake">Snowflake</option>
                  <option value="BigQuery">BigQuery</option>
                  <option value="Redshift">Redshift</option>
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Host
                  </label>
                  <input
                    type="text"
                    value={newDataSource.host}
                    onChange={(e) => setNewDataSource({ ...newDataSource, host: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="localhost"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Port
                  </label>
                  <input
                    type="text"
                    value={newDataSource.port}
                    onChange={(e) => setNewDataSource({ ...newDataSource, port: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="5432"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Database
                </label>
                <input
                  type="text"
                  value={newDataSource.database}
                  onChange={(e) => setNewDataSource({ ...newDataSource, database: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="database_name"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value={newDataSource.username}
                    onChange={(e) => setNewDataSource({ ...newDataSource, username: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="username"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    value={newDataSource.password}
                    onChange={(e) => setNewDataSource({ ...newDataSource, password: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="password"
                  />
                </div>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Test & Save
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}