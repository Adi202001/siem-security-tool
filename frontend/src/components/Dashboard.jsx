import { useState, useEffect } from 'react';
import { logsAPI, alertsAPI } from '../services/api';
import { formatRelativeTime, getSeverityColor } from '../utils/helpers';
import { FiAlertTriangle, FiActivity, FiShield, FiFileText } from 'react-icons/fi';
import ThreatVisualization from './ThreatVisualization';

const Dashboard = () => {
  const [logStats, setLogStats] = useState(null);
  const [alertStats, setAlertStats] = useState(null);
  const [recentAlerts, setRecentAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState(24);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [logsRes, alertsRes, recentAlertsRes] = await Promise.all([
        logsAPI.getStats(timeRange),
        alertsAPI.getStats(timeRange),
        alertsAPI.getAll({ limit: 5, unacknowledged_only: false }),
      ]);

      setLogStats(logsRes.data);
      setAlertStats(alertsRes.data);
      setRecentAlerts(recentAlertsRes.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color, subtitle }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className={`text-3xl font-bold ${color}`}>{value || 0}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full ${color.replace('text', 'bg').replace('600', '100')}`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </div>
  );

  if (loading && !logStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Security Dashboard</h1>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value={1}>Last Hour</option>
          <option value={24}>Last 24 Hours</option>
          <option value={168}>Last Week</option>
        </select>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Logs"
          value={logStats?.total_logs}
          icon={FiFileText}
          color="text-blue-600"
          subtitle={`Last ${timeRange}h`}
        />
        <StatCard
          title="Active Alerts"
          value={alertStats?.total_alerts}
          icon={FiAlertTriangle}
          color="text-red-600"
          subtitle={`${alertStats?.unacknowledged || 0} unacknowledged`}
        />
        <StatCard
          title="Anomalies Detected"
          value={logStats?.anomalies}
          icon={FiActivity}
          color="text-orange-600"
          subtitle="ML-based detection"
        />
        <StatCard
          title="Critical Severity"
          value={logStats?.logs_by_severity?.critical || 0}
          icon={FiShield}
          color="text-purple-600"
          subtitle="Requires immediate attention"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ThreatVisualization
          logStats={logStats}
          alertStats={alertStats}
        />
      </div>

      {/* Recent Alerts */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Recent Alerts</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentAlerts.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              No alerts in the selected time range
            </div>
          ) : (
            recentAlerts.map((alert) => (
              <div key={alert.id} className="px-6 py-4 hover:bg-gray-50 transition">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${getSeverityColor(alert.severity)}`}>
                        {alert.severity?.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-500">{alert.alert_type}</span>
                    </div>
                    <h3 className="mt-2 text-sm font-medium text-gray-900">{alert.title}</h3>
                    <p className="mt-1 text-sm text-gray-600">{alert.description}</p>
                    <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                      {alert.source && <span>Source: {alert.source}</span>}
                      <span>{formatRelativeTime(alert.timestamp)}</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    {alert.is_acknowledged ? (
                      <span className="text-xs text-green-600">✓ Acknowledged</span>
                    ) : (
                      <span className="text-xs text-gray-400">Pending</span>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
