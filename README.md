# Master Dashboard - 3D Infrastructure Monitoring System

<div align="center">

![Master Dashboard Logo](https://via.placeholder.com/200x80/00ffff/000000?text=MASTER+DASHBOARD)

**Advanced 3D Cyberpunk Dashboard for Real-time Infrastructure Monitoring**

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)](https://reactjs.org/)
[![Three.js](https://img.shields.io/badge/threejs-black?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

## 🌟 Overview

Master Dashboard is a cutting-edge 3D infrastructure monitoring system that provides real-time visualization of your server infrastructure through an immersive cyberpunk-themed interface. Built with modern technologies, it offers a unique way to monitor and manage your systems with interactive 3D motherboard representations of each machine.

### ✨ Key Features

- **🎮 3D Visualization**: Interactive 3D motherboards representing each machine type
- **⚡ Real-time Metrics**: Live CPU, Memory, Disk, and Network monitoring
- **🚨 Smart Alerts**: Intelligent alerting system with configurable thresholds
- **🎨 Cyberpunk UI**: Futuristic interface with neon effects and animations
- **📊 Historical Data**: Track performance trends over time
- **🔄 Auto-scaling**: Responsive design that works on all devices
- **🐳 Containerized**: Easy deployment with Docker Compose
- **📈 Performance Optimized**: 60+ FPS 3D rendering with WebGL

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Simulator     │
│   (React +      │◄──►│   (FastAPI)     │◄──►│   (Python)      │
│   Three.js)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Nginx       │
                    │  (Reverse       │
                    │   Proxy)        │
                    └─────────────────┘
```

### 🛠️ Technology Stack

**Frontend:**
- React 18 with Hooks and Context
- Three.js for 3D visualization  
- Tailwind CSS for styling
- Vite for fast development
- WebSocket for real-time communication

**Backend:**
- FastAPI (Python) with async support
- WebSocket manager for real-time data
- Pydantic for data validation
- Uvicorn ASGI server

**Infrastructure:**
- Docker & Docker Compose
- Nginx reverse proxy
- Redis (optional caching)
- PostgreSQL (optional persistence)

## 🚀 Quick Start

### Prerequisites

- Docker 20.0+
- Docker Compose 2.0+
- 4GB+ RAM
- Modern web browser with WebGL support

### 1-Minute Deployment

```bash
# Clone the repository
git clone https://github.com/your-org/master-dashboard.git
cd master-dashboard

# Start all services
docker-compose up -d

# Wait for services to be ready (about 2-3 minutes)
docker-compose logs -f

# Access the dashboard
open http://localhost:3000
```

### Manual Deployment

1. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Build and Start Services**
```bash
# Build all containers
docker-compose build

# Start services in background
docker-compose up -d

# Check service health
docker-compose ps
```

3. **Verify Deployment**
```bash
# Run health check
./scripts/health-check.sh

# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs simulator
```

## 📱 Usage

### Dashboard Interface

1. **3D Scene Navigation**
   - Left click + drag: Rotate camera
   - Right click + drag: Pan view
   - Scroll wheel: Zoom in/out
   - Click machine: Select for detailed view

2. **Control Panel**
   - Machine list with status indicators
   - System overview statistics
   - View controls and settings
   - Quick action buttons

3. **Metrics Panel**
   - Real-time gauges for selected machine
   - Historical performance charts
   - Performance statistics

4. **Alerts Panel**
   - Active alerts with severity levels
   - Alert filtering and sorting
   - Quick resolution actions

### Machine Types

- **🌐 Web Server**: HTTP/HTTPS services with load monitoring
- **🗄️ Database Server**: Database systems with query performance
- **⚙️ Application Server**: Application runtime environments
- **⚖️ Load Balancer**: Traffic distribution systems
- **💾 Cache Server**: High-speed data caching systems

### Alert Levels

- **🟢 Normal**: System operating within normal parameters
- **🟡 Warning**: Elevated metrics requiring attention
- **🔴 Critical**: High-priority issues needing immediate action

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# API Configuration
API_V1_STR=/api/v1
CORS_ORIGINS=http://localhost:3000

# Database (Optional)
DATABASE_URL=postgresql://user:pass@localhost/db

# WebSocket Settings
WEBSOCKET_HEARTBEAT_INTERVAL=30
MAX_WEBSOCKET_CONNECTIONS=100

# Performance Tuning
UPDATE_INTERVAL=5
WORKER_PROCESSES=auto
```

### Custom Machine Configuration

Add your own machines by modifying `backend/app/main.py`:

```python
sample_machines = [
    {
        "id": "machine-006",
        "name": "Your Custom Server",
        "type": "WEB_SERVER",
        "status": "ONLINE",
        "position": {"x": 3, "y": 0, "z": 0}
    }
]
```

### Alert Thresholds

Customize alert thresholds in `frontend/src/hooks/useMetrics.js`:

```javascript
const alertConditions = {
    CPU_USAGE: { warning: 70, critical: 90 },
    MEMORY_USAGE: { warning: 12, critical: 14 },
    // ... customize as needed
}
```

## 🔌 API Reference

### REST Endpoints

- `GET /api/v1/machines` - List all machines
- `GET /api/v1/machines/{id}` - Get machine details
- `GET /api/v1/metrics/latest` - Get latest metrics
- `GET /api/v1/alerts/active` - Get active alerts
- `GET /api/v1/health` - System health check

### WebSocket Events

- `metrics_batch` - Batch metric updates
- `metric_update` - Single metric update
- `alert_created` - New alert notification
- `alert_updated` - Alert status change

### Example WebSocket Message

```json
{
  "type": "metrics_batch",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": [
    {
      "machine_id": "machine-001",
      "metric_type": "CPU_USAGE",
      "value": 45.2,
      "unit": "%",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React application |
| Backend | 8000 | FastAPI server |
| Nginx | 80/443 | Reverse proxy |
| Redis | 6379 | Cache (optional) |
| PostgreSQL | 5432 | Database (optional) |

## 📊 Performance

### System Requirements

- **Minimum**: 2GB RAM, 2 CPU cores
- **Recommended**: 4GB RAM, 4 CPU cores
- **For 10+ machines**: 8GB RAM, 8 CPU cores

### Performance Targets

- **API Response Time**: < 200ms
- **WebSocket Latency**: < 50ms
- **3D Rendering**: 60+ FPS
- **Memory Usage**: < 500MB per service
- **Browser Support**: Chrome 90+, Firefox 88+, Safari 14+

## 🛡️ Security

### Production Security Checklist

- [ ] Change default passwords and secrets
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable security headers
- [ ] Regular security updates

### Security Features

- CORS protection
- Rate limiting on API endpoints
- Input validation with Pydantic
- Security headers via Nginx
- Optional SSL/TLS encryption

## 🔍 Monitoring & Observability

### Health Checks

```bash
# Manual health check
curl http://localhost:8000/api/v1/health

# Automated monitoring
./scripts/health-check.sh
```

### Metrics Collection

- System performance metrics
- API response times
- WebSocket connection counts
- Error rates and logs

### Logging

```bash
# View all logs
docker-compose logs

# Specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs simulator

# Follow live logs
docker-compose logs -f
```

## 🧪 Development

### Local Development Setup

```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend development
cd frontend
npm install
npm run dev

# Simulator development
cd simulator
python simulator.py --verbose
```

### Adding New Features

1. **New Machine Type**
   - Add to `MACHINE_TYPES` in constants
   - Create 3D model in `MotherboardModel.jsx`
   - Update simulator patterns

2. **New Metric Type**
   - Add to `METRIC_TYPES` in constants
   - Update backend validation schemas
   - Add visualization in frontend

3. **Custom Alerts**
   - Extend alert schemas
   - Add alert logic in `useMetrics.js`
   - Create alert visualization components

## 🐛 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check Docker status
docker-compose ps

# View error logs
docker-compose logs backend

# Restart services
docker-compose restart
```

**3D scene not loading:**
- Check browser WebGL support
- Disable browser extensions
- Check console for JavaScript errors

**WebSocket connection issues:**
- Verify backend is running on port 8000
- Check network connectivity
- Review CORS configuration

**High resource usage:**
- Reduce update interval in simulator
- Limit number of historical metrics
- Disable unused services

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose up

# Browser developer tools
# F12 -> Console -> Look for errors
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use Prettier, follow Airbnb style guide
- **Commits**: Use conventional commit format

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Three.js](https://threejs.org/) for amazing 3D capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent Python framework
- [React](https://reactjs.org/) for the powerful frontend library
- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework

## 📞 Support

- **Documentation**: [Wiki](https://github.com/your-org/master-dashboard/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/master-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/master-dashboard/discussions)
- **Email**: support@masterdashboard.dev

---

<div align="center">

**Built with ❤️ by the Master Dashboard Team**

[Website](https://masterdashboard.dev) • [Documentation](https://docs.masterdashboard.dev) • [Demo](https://demo.masterdashboard.dev)

</div>