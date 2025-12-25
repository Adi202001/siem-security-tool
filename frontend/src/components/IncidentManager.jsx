import { useState, useEffect } from 'react';
import { incidentsAPI } from '../services/api';
import { formatDate, getSeverityColor, getStatusColor } from '../utils/helpers';
import { FiPlus, FiEdit } from 'react-icons/fi';
import { toast } from 'react-toastify';

const IncidentManager = () => {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    severity: '',
  });

  useEffect(() => {
    fetchIncidents();
  }, [filters]);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const params = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== '')
      );
      const response = await incidentsAPI.getAll(params);
      setIncidents(response.data);
    } catch (err) {
      toast.error('Failed to fetch incidents');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (incidentId, status) => {
    try {
      await incidentsAPI.update(incidentId, { status });
      toast.success(`Incident marked as ${status}`);
      fetchIncidents();
      setSelectedIncident(null);
    } catch (err) {
      toast.error('Failed to update incident');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Security Incidents</h1>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2">
          <FiPlus />
          <span>New Incident</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All</option>
              <option value="open">Open</option>
              <option value="investigating">Investigating</option>
              <option value="contained">Contained</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Severity
            </label>
            <select
              value={filters.severity}
              onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Incidents List */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading incidents...</div>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {incidents.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                No incidents found
              </div>
            ) : (
              incidents.map((incident) => (
                <div
                  key={incident.id}
                  className="px-6 py-4 hover:bg-gray-50 transition cursor-pointer"
                  onClick={() => setSelectedIncident(incident)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-sm text-gray-600">
                          {incident.incident_id}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getSeverityColor(incident.severity)}`}>
                          {incident.severity?.toUpperCase()}
                        </span>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(incident.status)}`}>
                          {incident.status?.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">{incident.category}</span>
                      </div>
                      <h3 className="mt-2 text-lg font-medium text-gray-900">{incident.title}</h3>
                      <p className="mt-1 text-sm text-gray-600">{incident.description}</p>
                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                        <span>Priority: {incident.priority}</span>
                        {incident.assigned_to && <span>Assigned: {incident.assigned_to}</span>}
                        <span>Detected: {formatDate(incident.detected_at)}</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedIncident(incident);
                      }}
                      className="ml-4 p-2 text-blue-600 hover:text-blue-700"
                    >
                      <FiEdit className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Incident Details Modal */}
      {selectedIncident && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setSelectedIncident(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Incident Details</h2>
                <p className="text-sm text-gray-500 font-mono">{selectedIncident.incident_id}</p>
              </div>
              <button
                onClick={() => setSelectedIncident(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <div className="px-6 py-4 space-y-4">
              <div className="flex space-x-2">
                <span className={`px-2 py-1 text-xs font-medium rounded ${getSeverityColor(selectedIncident.severity)}`}>
                  {selectedIncident.severity?.toUpperCase()}
                </span>
                <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(selectedIncident.status)}`}>
                  {selectedIncident.status?.toUpperCase()}
                </span>
                <span className="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-600">
                  {selectedIncident.category}
                </span>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Title</label>
                <p className="mt-1 text-sm text-gray-900">{selectedIncident.title}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Description</label>
                <p className="mt-1 text-sm text-gray-900">{selectedIncident.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Priority</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedIncident.priority}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Assigned To</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedIncident.assigned_to || 'Unassigned'}</p>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">Detected At</label>
                <p className="mt-1 text-sm text-gray-900">{formatDate(selectedIncident.detected_at)}</p>
              </div>

              {selectedIncident.affected_systems && selectedIncident.affected_systems.length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Affected Systems</label>
                  <div className="mt-1 flex flex-wrap gap-2">
                    {selectedIncident.affected_systems.map((system, idx) => (
                      <span key={idx} className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded">
                        {system}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedIncident.resolution_notes && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Resolution Notes</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedIncident.resolution_notes}</p>
                </div>
              )}

              <div className="pt-4 border-t border-gray-200 flex space-x-2">
                {selectedIncident.status === 'open' && (
                  <button
                    onClick={() => handleUpdateStatus(selectedIncident.incident_id, 'investigating')}
                    className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
                  >
                    Start Investigation
                  </button>
                )}
                {selectedIncident.status === 'investigating' && (
                  <button
                    onClick={() => handleUpdateStatus(selectedIncident.incident_id, 'contained')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Mark as Contained
                  </button>
                )}
                {(selectedIncident.status === 'investigating' || selectedIncident.status === 'contained') && (
                  <button
                    onClick={() => handleUpdateStatus(selectedIncident.incident_id, 'resolved')}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Mark as Resolved
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IncidentManager;
