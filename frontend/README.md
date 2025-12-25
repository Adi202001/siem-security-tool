# SIEM Security Tool - Frontend

React-based frontend for the SIEM Security Tool with real-time monitoring, threat visualization, and incident management.

## Features

- **Dashboard**: Real-time security metrics and visualizations
- **Log Viewer**: Search, filter, and analyze security logs
- **Alert Management**: View, acknowledge, and manage security alerts
- **Detection Rules**: Create and manage custom detection rules
- **Incident Response**: Track and manage security incidents
- **Authentication**: Secure JWT-based authentication
- **Responsive Design**: Mobile-friendly interface

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Recharts**: Data visualization and charts
- **Tailwind CSS**: Utility-first CSS framework
- **React Icons**: Icon library
- **React Toastify**: Toast notifications
- **Zustand**: State management (if needed)

## Installation

### Using Node.js (Development)

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your API URL:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   VITE_API_PREFIX=/api/v1
   ```

4. Start development server:
   ```bash
   npm run dev
   ```

5. Open http://localhost:3000

### Using Docker

1. Build and run:
   ```bash
   docker build -t siem-frontend .
   docker run -p 3000:80 siem-frontend
   ```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Project Structure

```
frontend/
├── public/              # Static files
├── src/
│   ├── components/      # React components
│   │   ├── Dashboard.jsx
│   │   ├── LogViewer.jsx
│   │   ├── AlertViewer.jsx
│   │   ├── RulesManager.jsx
│   │   ├── IncidentManager.jsx
│   │   ├── Navbar.jsx
│   │   └── ThreatVisualization.jsx
│   ├── pages/           # Page components
│   │   └── Login.jsx
│   ├── contexts/        # React contexts
│   │   └── AuthContext.jsx
│   ├── services/        # API services
│   │   └── api.js
│   ├── utils/           # Utility functions
│   │   └── helpers.js
│   ├── types/           # Type definitions
│   │   └── index.js
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── Dockerfile
├── nginx.conf
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Features Overview

### Dashboard
- Real-time statistics (total logs, active alerts, anomalies)
- Severity distribution charts
- Top source IPs
- Recent alerts feed
- Auto-refresh every 30 seconds

### Log Viewer
- Search and filter logs
- View by severity, event type, source IP
- Export to CSV
- Anomaly highlighting
- Detailed log view with parsed data

### Alert Management
- Filter by severity, status, type
- Acknowledge alerts
- Update alert status
- View alert details
- Real-time updates

### Detection Rules
- Create custom detection rules
- Toggle rules on/off
- Edit and delete rules
- JSON-based conditions
- Rule statistics

### Incident Management
- Track security incidents
- Update incident status
- Assign incidents
- View affected systems
- Resolution tracking

## API Integration

The frontend communicates with the backend API using Axios. All API calls are centralized in `src/services/api.js`.

### Authentication

```javascript
import { authAPI } from './services/api';

// Login
const result = await authAPI.login(username, password);

// Register
const result = await authAPI.register(userData);
```

### Example API Calls

```javascript
// Get logs
const logs = await logsAPI.getAll({ severity: 'high', limit: 50 });

// Create alert
const alert = await alertsAPI.create(alertData);

// Update rule
const rule = await rulesAPI.update(ruleId, updateData);
```

## Environment Variables

- `VITE_API_BASE_URL` - Backend API base URL (default: http://localhost:8000)
- `VITE_API_PREFIX` - API prefix (default: /api/v1)
- `VITE_REFRESH_INTERVAL` - Dashboard refresh interval in ms (default: 30000)

## Building for Production

1. Build the application:
   ```bash
   npm run build
   ```

2. The build output will be in the `dist/` directory

3. Serve with any static file server or use the included Nginx configuration

## Docker Deployment

The included Dockerfile uses a multi-stage build:

1. Build stage: Compiles the React app
2. Production stage: Serves with Nginx

The Nginx configuration includes:
- API proxy to backend
- Gzip compression
- Static asset caching
- React Router support

## Default Credentials

For testing purposes:

- **Username**: admin
- **Password**: admin123

or

- **Username**: analyst
- **Password**: analyst123

## Contributing

1. Follow the existing code style
2. Use functional components with hooks
3. Keep components small and focused
4. Add proper error handling
5. Test responsive design

## License

MIT License
