import React from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  Users,
  Database,
  TrendingUp,
  Plus,
  Brain,
  Zap,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const stats = [
  { name: 'Total Dashboards', value: '24', icon: BarChart3, change: '+12%' },
  { name: 'Active Users', value: '156', icon: Users, change: '+8%' },
  { name: 'Data Sources', value: '8', icon: Database, change: '+2' },
  { name: 'Charts Created', value: '89', icon: TrendingUp, change: '+23%' },
];

const chartData = [
  { name: 'Jan', users: 400, dashboards: 240 },
  { name: 'Feb', users: 300, dashboards: 139 },
  { name: 'Mar', users: 200, dashboards: 980 },
  { name: 'Apr', users: 278, dashboards: 390 },
  { name: 'May', users: 189, dashboards: 480 },
  { name: 'Jun', users: 239, dashboards: 380 },
];

const pieData = [
  { name: 'PostgreSQL', value: 35, color: '#3b82f6' },
  { name: 'MySQL', value: 25, color: '#14b8a6' },
  { name: 'BigQuery', value: 20, color: '#f97316' },
  { name: 'Snowflake', value: 20, color: '#8b5cf6' },
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back! Here's your analytics overview.</p>
        </div>
        <div className="flex space-x-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center px-4 py-2 bg-secondary-100 text-secondary-700 rounded-lg hover:bg-secondary-200 transition-colors"
          >
            <Brain className="w-4 h-4 mr-2" />
            AI Assistant
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Dashboard
          </motion.button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-success-600 font-medium">{stat.change}</p>
              </div>
              <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                <stat.icon className="w-6 h-6 text-primary-600" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Usage Trends */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="users"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Users"
              />
              <Line
                type="monotone"
                dataKey="dashboards"
                stroke="#14b8a6"
                strokeWidth={2}
                name="Dashboards"
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Data Source Distribution */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Sources</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white rounded-xl shadow-sm border border-gray-200"
      >
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {[
              {
                icon: BarChart3,
                title: 'Sales Dashboard updated',
                time: '2 hours ago',
                user: 'John Doe',
              },
              {
                icon: Database,
                title: 'New PostgreSQL connection added',
                time: '4 hours ago',
                user: 'Jane Smith',
              },
              {
                icon: Brain,
                title: 'AI-generated chart created',
                time: '6 hours ago',
                user: 'AI Assistant',
              },
              {
                icon: Users,
                title: 'New user invited to workspace',
                time: '1 day ago',
                user: 'Admin',
              },
            ].map((activity, index) => (
              <div key={index} className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                  <activity.icon className="w-5 h-5 text-gray-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                  <p className="text-xs text-gray-500">by {activity.user} • {activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* AI Features Showcase */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-6 border border-primary-200"
      >
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <Zap className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">AI-Powered Analytics</h3>
            <p className="text-gray-600">
              Generate charts and insights from natural language. Try "Show me sales by region" or "Create a user retention chart".
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}