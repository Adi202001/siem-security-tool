import { useState, useEffect } from 'react';
import { alertsAPI } from '../services/api';
import { formatDate, getSeverityColor, getStatusColor } from '../utils/helpers';
import { FiCheckCircle, FiXCircle, FiFilter, FiRefreshCw } from 'react-icons/fi';
import { toast } from 'react-toastify';

const AlertViewer = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAlert, setSelectedAlert] = useState(null);

  // Filters
  const [filters, setFilters] = useState({
    severity: '',
    status: '',
    alert_type: '',
    unacknowledged_only: false,
  });

  const [page, setPage] = useState(0);
  const [limit] = useState(20);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [filters, page]);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const params = {
        skip: page * limit,
        limit,
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => v !== '' && v !== false)
        ),
      };

      const response = await alertsAPI.getAll(params);
      setAlerts(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(0);
  };

  const handleAcknowledge = async (alertId) => {
    try {
      await alertsAPI.acknowledge(alertId);
      toast.success('Alert acknowledged');
      fetchAlerts();
    } catch (err) {
      toast.error('Failed to acknowledge alert');
    }
  };

  const handleUpdateStatus = async (alertId, status) => {
    try {
      await alertsAPI.update(alertId, { status });
      toast.success(`Alert marked as ${status}`);
      fetchAlerts();
      setSelectedAlert(null);
    } catch (err) {
      toast.error('Failed to update alert');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Security Alerts</h1>
        <button
          onClick={fetchAlerts}
          className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
        >
          <FiRefreshCw className={loading ? 'animate-spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Severity
            </label>
            <select
              value={filters.severity}
              onChange={(e) => handleFilterChange('severity', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All</option>
              <option value="open">Open</option>
              <option value="investigating">Investigating</option>
              <option value="resolved">Resolved</option>
              <option value="false_positive">False Positive</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={filters.alert_type}
              onChange={(e) => handleFilterChange('alert_type', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All</option>
              <option value="rule-based">Rule-Based</option>
              <option value="anomaly">Anomaly</option>
              <option value="manual">Manual</option>
            </select>
          </div>

          <div className="flex items-end">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={filters.unacknowledged_only}
                onChange={(e) => handleFilterChange('unacknowledged_only', e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Unacknowledged Only</span>
            </label>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading alerts...</div>
          </div>
        ) : error ? (
          <div className="p-4 bg-red-50 border border-red-200 text-red-800">
            {error}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {alerts.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                No alerts found
              </div>
            ) : (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="px-6 py-4 hover:bg-gray-50 transition cursor-pointer"
                  onClick={() => setSelectedAlert(alert)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getSeverityColor(alert.severity)}`}>
                          {alert.severity?.toUpperCase()}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(alert.status)}`}>
                          {alert.status?.toUpperCase().replace('_', ' ')}
                        </span>
                        <span className="text-xs text-gray-500">{alert.alert_type}</span>
                      </div>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">{alert.title}</h3>
                      <p className="mt-1 text-sm text-gray-600">{alert.description}</p>
                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                        {alert.source && <span>Source: {alert.source}</span>}
                        {alert.destination && <span>Dest: {alert.destination}</span>}
                        <span>{formatDate(alert.timestamp)}</span>
                      </div>
                    </div>
                    <div className="ml-4 flex items-center space-x-2">
                      {!alert.is_acknowledged && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAcknowledge(alert.id);
                          }}
                          className="px-3 py-1 text-xs font-medium text-blue-600 hover:text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 flex items-center space-x-1"
                        >
                          <FiCheckCircle />
                          <span>Acknowledge</span>
                        </button>
                      )}
                      {alert.is_acknowledged && (
                        <span className="text-xs text-green-600 flex items-center space-x-1">
                          <FiCheckCircle />
                          <span>Acknowledged</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Pagination */}
        {!loading && alerts.length > 0 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="text-sm text-gray-700">
              Page {page + 1}
            </span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={alerts.length < limit}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Alert Details Modal */}
      {selectedAlert && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setSelectedAlert(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Alert Details</h2>
              <button
                onClick={() => setSelectedAlert(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div className="flex space-x-2">
                <span className={`px-2 py-1 text-xs font-medium rounded ${getSeverityColor(selectedAlert.severity)}`}>
                  {selectedAlert.severity?.toUpperCase()}
                </span>
                <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(selectedAlert.status)}`}>
                  {selectedAlert.status?.toUpperCase().replace('_', ' ')}
                </span>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Title</label>
                <p className="mt-1 text-sm text-gray-900">{selectedAlert.title}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Description</label>
                <p className="mt-1 text-sm text-gray-900">{selectedAlert.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Source</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedAlert.source || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Destination</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedAlert.destination || 'N/A'}</p>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Timestamp</label>
                <p className="mt-1 text-sm text-gray-900">{formatDate(selectedAlert.timestamp)}</p>
              </div>

              {selectedAlert.resolution_notes && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Resolution Notes</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedAlert.resolution_notes}</p>
                </div>
              )}

              <div className="pt-4 border-t border-gray-200 flex space-x-2">
                {selectedAlert.status === 'open' && (
                  <button
                    onClick={() => handleUpdateStatus(selectedAlert.id, 'investigating')}
                    className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                  >
                    Mark as Investigating
                  </button>
                )}
                {(selectedAlert.status === 'open' || selectedAlert.status === 'investigating') && (
                  <>
                    <button
                      onClick={() => handleUpdateStatus(selectedAlert.id, 'resolved')}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      Mark as Resolved
                    </button>
                    <button
                      onClick={() => handleUpdateStatus(selectedAlert.id, 'false_positive')}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                    >
                      Mark as False Positive
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertViewer;
