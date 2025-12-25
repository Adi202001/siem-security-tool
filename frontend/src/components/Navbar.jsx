import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FiHome, FiAlertTriangle, FiFileText, FiShield, FiList, FiLogOut } from 'react-icons/fi';

const Navbar = () => {
  const location = useLocation();
  const { logout } = useAuth();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: FiHome },
    { path: '/logs', label: 'Logs', icon: FiFileText },
    { path: '/alerts', label: 'Alerts', icon: FiAlertTriangle },
    { path: '/rules', label: 'Rules', icon: FiShield },
    { path: '/incidents', label: 'Incidents', icon: FiList },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <FiShield className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">SIEM Security</span>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center space-x-1">
            {navItems.map(({ path, label, icon: Icon }) => (
              <Link
                key={path}
                to={path}
                className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition ${
                  isActive(path)
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="font-medium">{label}</span>
              </Link>
            ))}

            {/* Logout Button */}
            <button
              onClick={logout}
              className="ml-4 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg flex items-center space-x-2 transition"
            >
              <FiLogOut className="w-4 h-4" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
