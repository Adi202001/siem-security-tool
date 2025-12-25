import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

const ThreatVisualization = ({ logStats, alertStats }) => {
  // Prepare severity data
  const severityData = [
    { name: 'Critical', value: logStats?.logs_by_severity?.critical || 0, color: '#dc2626' },
    { name: 'High', value: logStats?.logs_by_severity?.high || 0, color: '#ea580c' },
    { name: 'Medium', value: logStats?.logs_by_severity?.medium || 0, color: '#ca8a04' },
    { name: 'Low', value: logStats?.logs_by_severity?.low || 0, color: '#2563eb' },
  ];

  // Prepare alert status data
  const statusData = Object.entries(alertStats?.alerts_by_status || {}).map(([name, value]) => ({
    name: name.replace('_', ' ').toUpperCase(),
    value,
  }));

  // Prepare top IPs data
  const topIPsData = (logStats?.top_source_ips || []).slice(0, 5).map((item) => ({
    ip: item.ip || 'Unknown',
    count: item.count,
  }));

  const COLORS = ['#dc2626', '#ea580c', '#ca8a04', '#2563eb', '#10b981'];

  return (
    <>
      {/* Severity Distribution */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Log Severity Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={severityData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) =>
                percent > 0 ? `${name} ${(percent * 100).toFixed(0)}%` : ''
              }
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {severityData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Top Source IPs */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Source IPs</h3>
        {topIPsData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topIPsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="ip" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-500">
            No data available
          </div>
        )}
      </div>

      {/* Alert Status Distribution */}
      {statusData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Alert Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  percent > 0 ? `${name} ${(percent * 100).toFixed(0)}%` : ''
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </>
  );
};

export default ThreatVisualization;
