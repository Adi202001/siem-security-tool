# SIEM Security Tool

A comprehensive Security Information and Event Management (SIEM) tool built with Python FastAPI backend and React frontend. Features real-time log ingestion, parsing, rule-based threat detection, ML-based anomaly detection, and an interactive dashboard for security monitoring and incident response.

## 🚀 Features

### Backend (FastAPI)
- **Log Ingestion**: RESTful API for ingesting security logs from multiple sources
- **Log Parsing**: Automatic parsing of common log formats (syslog, Apache, firewall, authentication logs)
- **Rule-Based Detection**: Customizable detection rules with flexible condition matching
- **ML Anomaly Detection**: Machine learning-based anomaly detection using Isolation Forest
- **Real-time Alerts**: Automatic alert generation for detected threats
- **Incident Management**: Track and manage security incidents with timeline
- **JWT Authentication**: Secure authentication with role-based access control
- **RESTful API**: Complete API with Swagger/OpenAPI documentation

### Frontend (React)
- **Dashboard**: Real-time security metrics with interactive charts
- **Log Viewer**: Advanced search, filtering, and log analysis
- **Alert Management**: View, acknowledge, and manage security alerts
- **Detection Rules**: Create and manage custom detection rules
- **Incident Response**: Track incidents through their lifecycle
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Auto-refresh for live monitoring

## 📋 Prerequisites

- Docker and Docker Compose (recommended)
- OR:
  - Python 3.11+ (for backend)
  - Node.js 18+ (for frontend)

## 🐳 Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd siem-security-tool
   ```

2. Start all services:
   ```bash
   docker-compose up --build
   ```

3. Initialize the database (in a new terminal):
   ```bash
   docker exec -it siem-backend python init_db.py
   ```

4. Access the application:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

5. Login with default credentials:
   - **Admin**: username: `admin`, password: `admin123`
   - **Analyst**: username: `analyst`, password: `analyst123`

## 🛠️ Manual Installation

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY
   ```

5. Initialize database:
   ```bash
   python init_db.py
   ```

6. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

4. Start development server:
   ```bash
   npm run dev
   ```

## 📊 Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  React Frontend │────────▶│  FastAPI Backend │
│   (Port 3000)   │         │   (Port 8000)    │
└─────────────────┘         └──────────────────┘
                                      │
                            ┌─────────┼─────────┐
                            ▼         ▼         ▼
                     ┌──────────┬─────────┬──────────┐
                     │ SQLite   │  Redis  │  Celery  │
                     │ Database │  Cache  │  Worker  │
                     └──────────┴─────────┴──────────┘
```

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Logs
- `POST /api/v1/logs/ingest` - Ingest single log
- `POST /api/v1/logs/ingest/batch` - Ingest multiple logs
- `GET /api/v1/logs` - Query logs with filters
- `GET /api/v1/logs/stats` - Get log statistics
- `GET /api/v1/logs/{id}` - Get specific log

### Alerts
- `GET /api/v1/alerts` - Get alerts with filters
- `GET /api/v1/alerts/stats` - Get alert statistics
- `POST /api/v1/alerts/{id}/acknowledge` - Acknowledge alert
- `PATCH /api/v1/alerts/{id}` - Update alert status

### Detection Rules
- `POST /api/v1/rules` - Create detection rule
- `GET /api/v1/rules` - List all rules
- `PATCH /api/v1/rules/{id}` - Update rule
- `POST /api/v1/rules/{id}/toggle` - Toggle rule active status

### Incidents
- `POST /api/v1/incidents` - Create incident
- `GET /api/v1/incidents` - List incidents
- `PATCH /api/v1/incidents/{id}` - Update incident
- `GET /api/v1/incidents/{id}` - Get incident details

## 📝 Usage Examples

### Ingest a Log

```bash
curl -X POST "http://localhost:8000/api/v1/logs/ingest" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_log": "Jan 15 10:30:45 server1 sshd[12345]: Failed password for admin from 192.168.1.100 port 22 ssh2",
    "event_type": "authentication",
    "severity": "high",
    "message": "Failed SSH login attempt"
  }'
```

### Create Detection Rule

```bash
curl -X POST "http://localhost:8000/api/v1/rules" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Brute Force Detection",
    "description": "Detect multiple failed login attempts",
    "rule_type": "correlation",
    "severity": "high",
    "created_by": "admin",
    "conditions": {
      "field_contains": {"message": "Failed password"},
      "min_severity": "medium"
    }
  }'
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔒 Security Considerations

- **Change Default Credentials**: Update default admin/analyst passwords immediately
- **Set SECRET_KEY**: Use a strong, random secret key in production
- **Enable HTTPS**: Use SSL/TLS certificates in production
- **Database**: Consider PostgreSQL for production instead of SQLite
- **CORS**: Configure proper CORS origins in production
- **Rate Limiting**: Implement rate limiting for API endpoints
- **Input Validation**: All inputs are validated through Pydantic schemas

## 📈 Performance

- **Async API**: FastAPI with async/await for high performance
- **Database Indexing**: Proper indexes on frequently queried fields
- **Caching**: Redis caching for frequently accessed data
- **Background Jobs**: Celery for async processing of heavy tasks
- **Optimized Queries**: Efficient database queries with SQLAlchemy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React team for the frontend library
- scikit-learn for ML capabilities
- Recharts for data visualization
- Tailwind CSS for styling

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🗺️ Roadmap

- [ ] PostgreSQL database support
- [ ] Elasticsearch integration for log storage
- [ ] Advanced ML models (LSTM, Random Forest)
- [ ] SIEM connector for popular tools (Splunk, ELK)
- [ ] Email notifications for critical alerts
- [ ] Advanced correlation engine
- [ ] Threat intelligence integration
- [ ] Custom dashboard widgets
- [ ] Mobile application
- [ ] Multi-tenancy support

---

**Built with ❤️ for cybersecurity professionals**
