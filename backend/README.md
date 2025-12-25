# SIEM Security Tool - Backend

FastAPI-based backend for the SIEM Security Tool with log ingestion, threat detection, and ML-based anomaly detection.

## Features

- **Log Ingestion**: Ingest security logs from multiple sources
- **Log Parsing**: Automatic parsing of common log formats (syslog, Apache, firewall, auth logs)
- **Rule-Based Detection**: Customizable detection rules for threat identification
- **ML Anomaly Detection**: Machine learning-based anomaly detection using Isolation Forest
- **Real-time Alerts**: Automatic alert generation for detected threats
- **Incident Management**: Track and manage security incidents
- **RESTful API**: Complete REST API for integration

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database (easily replaceable with PostgreSQL)
- **scikit-learn**: Machine learning for anomaly detection
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Installation

### Using Docker (Recommended)

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your configuration (especially `SECRET_KEY`)

3. Build and run:
   ```bash
   docker-compose up --build
   ```

### Manual Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy and configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get access token

### Logs
- `POST /api/v1/logs/ingest` - Ingest a single log
- `POST /api/v1/logs/ingest/batch` - Ingest multiple logs
- `GET /api/v1/logs` - Query logs with filters
- `GET /api/v1/logs/stats` - Get log statistics
- `GET /api/v1/logs/{log_id}` - Get specific log

### Alerts
- `GET /api/v1/alerts` - Get alerts with filters
- `GET /api/v1/alerts/stats` - Get alert statistics
- `GET /api/v1/alerts/{alert_id}` - Get specific alert
- `PATCH /api/v1/alerts/{alert_id}` - Update alert
- `POST /api/v1/alerts/{alert_id}/acknowledge` - Acknowledge alert

### Detection Rules
- `POST /api/v1/rules` - Create detection rule
- `GET /api/v1/rules` - Get all rules
- `GET /api/v1/rules/{rule_id}` - Get specific rule
- `PATCH /api/v1/rules/{rule_id}` - Update rule
- `POST /api/v1/rules/{rule_id}/toggle` - Toggle rule active status

### Incidents
- `POST /api/v1/incidents` - Create incident
- `GET /api/v1/incidents` - Get incidents with filters
- `GET /api/v1/incidents/{incident_id}` - Get specific incident
- `PATCH /api/v1/incidents/{incident_id}` - Update incident

## Usage Examples

### Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "securepassword",
    "full_name": "Admin User"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=securepassword"
```

### Ingest a Log
```bash
curl -X POST "http://localhost:8000/api/v1/logs/ingest" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_log": "Jan 15 10:30:45 server1 sshd[12345]: Failed password for invalid user admin from 192.168.1.100 port 22 ssh2",
    "event_type": "authentication",
    "severity": "high",
    "message": "Failed login attempt"
  }'
```

### Create a Detection Rule
```bash
curl -X POST "http://localhost:8000/api/v1/rules" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Failed SSH Login",
    "description": "Detect failed SSH login attempts",
    "rule_type": "signature",
    "severity": "high",
    "created_by": "admin",
    "conditions": {
      "field_contains": {
        "message": "Failed password"
      },
      "min_severity": "medium"
    }
  }'
```

## Architecture

```
backend/
├── app/
│   ├── api/          # API route handlers
│   ├── core/         # Core functionality (config, security, deps)
│   ├── db/           # Database configuration
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic (log parser, rule engine)
│   ├── ml/           # Machine learning modules
│   └── main.py       # Application entry point
├── tests/            # Test files
├── models/           # Trained ML models
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Configuration

Key configuration options in `.env`:

- `SECRET_KEY`: Secret key for JWT tokens (CHANGE IN PRODUCTION!)
- `DATABASE_URL`: Database connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `ANOMALY_DETECTION_THRESHOLD`: ML threshold for anomalies
- `LOG_RETENTION_DAYS`: How long to keep logs

## Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS middleware configured
- Input validation with Pydantic
- SQL injection prevention through SQLAlchemy ORM

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black app/
```

Run linter:
```bash
flake8 app/
```

## License

MIT License
