import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, BarChart3, Brain, Eye, Edit, Share, MoreVertical } from 'lucide-react';

const charts = [
  {
    id: '1',
    name: 'Sales Performance',
    type: 'Bar Chart',
    workspace: 'Analytics Team',
    created: '2024-01-15',
    views: 1234,
    isAIGenerated: false,
  },
  {
    id: '2',
    name: 'User Engagement Trends',
    type: 'Line Chart',
    workspace: 'Marketing Dashboard',
    created: '2024-01-18',
    views: 892,
    isAIGenerated: true,
  },
  {
    id: '3',
    name: 'Revenue by Region',
    type: 'Pie Chart',
    workspace: 'Analytics Team',
    created: '2024-01-20',
    views: 567,
    isAIGenerated: false,
  },
  {
    id: '4',
    name: 'Customer Retention Analysis',
    type: 'Area Chart',
    workspace: 'Analytics Team',
    created: '2024-01-22',
    views: 345,
    isAIGenerated: true,
  },
];

export default function Charts() {
  const [showAIModal, setShowAIModal] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleAIGenerate = async () => {
    setIsGenerating(true);
    // Simulate AI chart generation
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsGenerating(false);
    setShowAIModal(false);
    setAiPrompt('');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Charts & Dashboards</h1>
          <p className="text-gray-600">Create and manage your data visualizations</p>
        </div>
        <div className="flex space-x-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowAIModal(true)}
            className="flex items-center px-4 py-2 bg-secondary-100 text-secondary-700 rounded-lg hover:bg-secondary-200 transition-colors"
          >
            <Brain className="w-4 h-4 mr-2" />
            AI Generate
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Chart
          </motion.button>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {charts.map((chart, index) => (
          <motion.div
            key={chart.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all"
          >
            {/* Chart Preview */}
            <div className="h-32 bg-gradient-to-br from-primary-50 to-secondary-50 rounded-t-xl flex items-center justify-center">
              <BarChart3 className="w-12 h-12 text-primary-400" />
            </div>
            
            {/* Chart Info */}
            <div className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">{chart.name}</h3>
                <button className="p-1 rounded-md hover:bg-gray-100">
                  <MoreVertical className="w-4 h-4 text-gray-400" />
                </button>
              </div>
              
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-sm text-gray-600">{chart.type}</span>
                {chart.isAIGenerated && (
                  <span className="px-2 py-1 text-xs font-medium bg-secondary-100 text-secondary-700 rounded-full flex items-center">
                    <Brain className="w-3 h-3 mr-1" />
                    AI
                  </span>
                )}
              </div>
              
              <div className="space-y-1 text-sm text-gray-500 mb-4">
                <p>Workspace: {chart.workspace}</p>
                <p>Created: {chart.created}</p>
                <div className="flex items-center">
                  <Eye className="w-3 h-3 mr-1" />
                  {chart.views} views
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button className="flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                  <Eye className="w-4 h-4 mr-1" />
                  View
                </button>
                <button className="flex items-center justify-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                  <Edit className="w-4 h-4" />
                </button>
                <button className="flex items-center justify-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                  <Share className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* AI Chart Generation Modal */}
      {showAIModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl p-6 w-full max-w-lg mx-4"
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-secondary-100 rounded-xl flex items-center justify-center">
                <Brain className="w-5 h-5 text-secondary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">AI Chart Generator</h3>
            </div>
            
            <p className="text-gray-600 mb-4">
              Describe the chart you want to create in natural language, and our AI will generate it for you.
            </p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Describe your chart
                </label>
                <textarea
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  rows={3}
                  placeholder="e.g., Show me sales by region for the last 6 months as a bar chart"
                />
              </div>
              
              <div className="bg-gray-50 p-3 rounded-lg">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Example prompts:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Create a line chart showing user growth over time</li>
                  <li>• Show revenue breakdown by product category as a pie chart</li>
                  <li>• Display monthly recurring revenue trends</li>
                </ul>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowAIModal(false)}
                disabled={isGenerating}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAIGenerate}
                disabled={!aiPrompt || isGenerating}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
              >
                {isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Generating...
                  </>
                ) : (
                  'Generate Chart'
                )}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}