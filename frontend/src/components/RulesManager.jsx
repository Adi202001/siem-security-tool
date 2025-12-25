import { useState, useEffect } from 'react';
import { rulesAPI } from '../services/api';
import { getSeverityColor } from '../utils/helpers';
import { FiPlus, FiEdit, FiTrash2, FiToggleLeft, FiToggleRight } from 'react-icons/fi';
import { toast } from 'react-toastify';

const RulesManager = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingRule, setEditingRule] = useState(null);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    rule_type: 'signature',
    severity: 'medium',
    conditions: '{}',
    is_active: true,
    created_by: 'admin',
  });

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await rulesAPI.getAll({ limit: 100 });
      setRules(response.data);
    } catch (err) {
      toast.error('Failed to fetch rules');
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (id) => {
    try {
      await rulesAPI.toggle(id);
      toast.success('Rule toggled successfully');
      fetchRules();
    } catch (err) {
      toast.error('Failed to toggle rule');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this rule?')) return;

    try {
      await rulesAPI.delete(id);
      toast.success('Rule deleted successfully');
      fetchRules();
    } catch (err) {
      toast.error('Failed to delete rule');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const data = {
        ...formData,
        conditions: JSON.parse(formData.conditions),
      };

      if (editingRule) {
        await rulesAPI.update(editingRule.id, data);
        toast.success('Rule updated successfully');
      } else {
        await rulesAPI.create(data);
        toast.success('Rule created successfully');
      }

      setShowModal(false);
      setEditingRule(null);
      resetForm();
      fetchRules();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save rule');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      rule_type: 'signature',
      severity: 'medium',
      conditions: '{}',
      is_active: true,
      created_by: 'admin',
    });
  };

  const openEditModal = (rule) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      description: rule.description || '',
      rule_type: rule.rule_type,
      severity: rule.severity,
      conditions: JSON.stringify(rule.conditions, null, 2),
      is_active: rule.is_active,
      created_by: rule.created_by,
    });
    setShowModal(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Detection Rules</h1>
        <button
          onClick={() => {
            resetForm();
            setEditingRule(null);
            setShowModal(true);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <FiPlus />
          <span>New Rule</span>
        </button>
      </div>

      {/* Rules List */}
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-500">Loading rules...</div>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {rules.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                No detection rules found
              </div>
            ) : (
              rules.map((rule) => (
                <div key={rule.id} className="px-6 py-4 hover:bg-gray-50 transition">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="text-lg font-medium text-gray-900">{rule.name}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded ${getSeverityColor(rule.severity)}`}>
                          {rule.severity?.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">{rule.rule_type}</span>
                        {rule.is_active ? (
                          <span className="text-xs text-green-600 font-medium">● ACTIVE</span>
                        ) : (
                          <span className="text-xs text-gray-400 font-medium">○ INACTIVE</span>
                        )}
                      </div>
                      <p className="mt-1 text-sm text-gray-600">{rule.description}</p>
                      <div className="mt-2 text-xs text-gray-500">
                        Triggered {rule.trigger_count || 0} times
                        {rule.false_positive_count > 0 && (
                          <span className="ml-2">
                            ({rule.false_positive_count} false positives)
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="ml-4 flex items-center space-x-2">
                      <button
                        onClick={() => handleToggle(rule.id)}
                        className="p-2 text-gray-600 hover:text-gray-900"
                        title={rule.is_active ? 'Disable' : 'Enable'}
                      >
                        {rule.is_active ? (
                          <FiToggleRight className="w-6 h-6 text-green-600" />
                        ) : (
                          <FiToggleLeft className="w-6 h-6" />
                        )}
                      </button>
                      <button
                        onClick={() => openEditModal(rule)}
                        className="p-2 text-blue-600 hover:text-blue-700"
                      >
                        <FiEdit className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(rule.id)}
                        className="p-2 text-red-600 hover:text-red-700"
                      >
                        <FiTrash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingRule ? 'Edit Rule' : 'Create New Rule'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rule Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rule Type *
                  </label>
                  <select
                    value={formData.rule_type}
                    onChange={(e) => setFormData({ ...formData, rule_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="signature">Signature</option>
                    <option value="behavioral">Behavioral</option>
                    <option value="correlation">Correlation</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Severity *
                  </label>
                  <select
                    value={formData.severity}
                    onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Conditions (JSON) *
                </label>
                <textarea
                  required
                  value={formData.conditions}
                  onChange={(e) => setFormData({ ...formData, conditions: e.target.value })}
                  rows={6}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder='{"field_contains": {"message": "failed"}}'
                />
                <p className="mt-1 text-xs text-gray-500">
                  Example: {'{"field_contains": {"message": "failed"}, "min_severity": "medium"}'}
                </p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label className="ml-2 text-sm font-medium text-gray-700">
                  Active
                </label>
              </div>

              <div className="pt-4 border-t border-gray-200 flex space-x-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingRule ? 'Update Rule' : 'Create Rule'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default RulesManager;
