# 🏗️ MASTER DASHBOARD - ARCHITECTURE & DEVELOPER GUIDE

## 📋 System Overview

The Master Dashboard is a production-ready, real-time 3D infrastructure monitoring system built with modern technologies and enterprise-grade security.

### Core Components
- **Frontend**: React + Three.js (3D visualization)
- **Backend**: FastAPI + WebSocket (Real-time API)
- **Simulator**: Python async data generator
- **Agents**: Linux/Windows system monitors
- **Database**: PostgreSQL + Redis
- **Proxy**: Nginx reverse proxy

---

## 🚀 Quick Start Guide

### Ubuntu Server Installation
```bash
# 1. Download system
wget https://github.com/your-repo/master-dashboard/archive/main.zip
unzip main.zip && cd master-dashboard-main

# 2. Automated installation
sudo ./install-ubuntu.sh

# 3. Configure environment
sudo nano /opt/master-dashboard/.env

# 4. Start services
sudo systemctl start master-dashboard
sudo systemctl enable master-dashboard

# 5. Verify installation
curl http://localhost:8000/api/v1/health
```

### Access Points
- **Dashboard**: http://your-server:3000
- **API**: http://your-server:8000
- **Docs**: http://your-server:8000/docs

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER DASHBOARD SYSTEM                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Frontend  │    │   Backend   │    │  Simulator  │    │
│  │   (React)   │◄──►│  (FastAPI)  │◄──►│  (Python)   │    │
│  │   Port 3000 │    │  Port 8000  │    │  WebSocket  │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │    Nginx    │    │ PostgreSQL  │    │    Redis    │    │
│  │  Port 80/443│    │  Port 5432  │    │  Port 6379  │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Development Setup

### Prerequisites
```bash
# Install development tools
sudo apt install -y python3 python3-pip nodejs npm git docker.io

# Install Python dependencies
pip3 install fastapi uvicorn websockets pydantic

# Install Node.js dependencies
npm install -g vite @vitejs/plugin-react
```

### Local Development
```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
npm install
npm run dev

# Simulator development
cd simulator
python simulator.py --verbose
```

---

## 📚 API Reference

### Authentication
```http
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "password"
}
```

### Machine Management
```http
# Get all machines
GET /api/v1/machines

# Get machine by ID
GET /api/v1/machines/{machine_id}

# Create new machine
POST /api/v1/machines
{
  "name": "New Server",
  "type": "WEB_SERVER",
  "position": {"x": 0, "y": 0, "z": 0}
}
```

### Metrics API
```http
# Get machine metrics
GET /api/v1/machines/{machine_id}/metrics

# Submit metrics
POST /api/v1/metrics
{
  "machine_id": "machine-001",
  "metrics": [
    {"type": "CPU_USAGE", "value": 67.5, "unit": "%"}
  ]
}
```

### WebSocket Real-time
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/metrics')
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // Handle real-time updates
}
```

---

## 🛠️ Operations Guide

### Service Management
```bash
# Check status
sudo systemctl status master-dashboard

# Start/Stop/Restart
sudo systemctl start master-dashboard
sudo systemctl stop master-dashboard
sudo systemctl restart master-dashboard

# View logs
sudo journalctl -u master-dashboard -f
```

### Docker Management
```bash
# View containers
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update containers
docker-compose pull && docker-compose up -d
```

### Health Monitoring
```bash
# System health check
curl http://localhost:8000/api/v1/health

# Performance monitoring
docker stats --no-stream

# Resource usage
df -h /opt/master-dashboard
free -h
```

---

## 🔒 Security Guide

### Production Security
- **HTTPS/TLS**: All traffic encrypted
- **JWT Authentication**: Token-based security
- **CORS Protection**: Origin restrictions
- **Container Security**: Non-root users
- **Input Validation**: Pydantic models
- **Rate Limiting**: API protection

### Security Configuration
```bash
# Generate secure secret key
SECRET_KEY=$(openssl rand -base64 32)

# SSL certificate setup
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/master-dashboard/ssl/dashboard.key \
  -out /opt/master-dashboard/ssl/dashboard.crt

# Update CORS origins
CORS_ORIGINS=https://yourdomain.com,https://dashboard.yourdomain.com
```

---

## 🚨 Troubleshooting

### Common Issues

#### Frontend not loading
```bash
# Check frontend container
docker-compose logs frontend

# Verify API connection
curl http://localhost:8000/api/v1/health

# Check network configuration
docker network ls
```

#### WebSocket connection issues
```bash
# Check WebSocket endpoint
wscat -c ws://localhost:8000/ws/metrics

# Verify CORS settings
grep CORS /opt/master-dashboard/.env

# Check firewall rules
sudo ufw status
```

#### Database connection errors
```bash
# Check PostgreSQL container
docker-compose logs postgres

# Test database connection
docker exec -it master-dashboard-postgres psql -U dashboard -d master_dashboard

# Check environment variables
grep DATABASE_URL /opt/master-dashboard/.env
```

#### High CPU/Memory usage
```bash
# Monitor container resources
docker stats

# Check system resources
top -p $(pgrep -d, -f master-dashboard)

# Restart services if needed
docker-compose restart
```

---

## 📊 Performance Optimization

### Resource Monitoring
```bash
# Container resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# System performance
vmstat 1 5
iostat -x 1 5

# Network monitoring
ss -tuln | grep -E ':(3000|8000|5432|6379)'
```

### Optimization Tips
- **Database**: Use connection pooling
- **WebSocket**: Implement connection limits
- **Frontend**: Enable compression and caching
- **Backend**: Use async/await patterns
- **Docker**: Use multi-stage builds
- **Nginx**: Enable gzip compression

---

## 🔄 Maintenance Procedures

### Regular Maintenance
```bash
#!/bin/bash
# Weekly maintenance script

echo "=== Master Dashboard Maintenance ==="

# Update containers
docker-compose pull
docker-compose up -d

# Clean old logs
journalctl --vacuum-time=7d

# Clean Docker images
docker image prune -f

# Backup database
pg_dump -U dashboard master_dashboard > backup_$(date +%Y%m%d).sql

# Check disk space
df -h /opt/master-dashboard

echo "Maintenance completed"
```

### Backup Strategy
```bash
# Database backup
docker exec master-dashboard-postgres pg_dump -U dashboard master_dashboard > db_backup.sql

# Configuration backup
tar -czf config_backup.tar.gz /opt/master-dashboard/.env /opt/master-dashboard/docker-compose.yml

# Full system backup
rsync -av /opt/master-dashboard/ backup_location/
```

---

## 📈 Scaling Guide

### Horizontal Scaling
- **Load Balancer**: Multiple frontend instances
- **Database**: Read replicas
- **Cache**: Redis cluster
- **WebSocket**: Connection distribution

### Vertical Scaling
- **CPU**: Increase container limits
- **Memory**: Adjust heap sizes
- **Storage**: SSD storage recommended
- **Network**: 10Gbps for high load

---

## 🎯 Production Checklist

### Pre-deployment
- [ ] SSL certificates configured
- [ ] Environment variables set
- [ ] Database initialized
- [ ] Backup procedures tested
- [ ] Monitoring configured
- [ ] Security hardening applied

### Post-deployment
- [ ] Health checks passing
- [ ] Performance monitoring active
- [ ] Log aggregation configured
- [ ] Alerting rules set up
- [ ] Documentation updated
- [ ] Team training completed

---

## 📞 Support Information

### Documentation
- Architecture Guide: This document
- API Documentation: http://your-server:8000/docs
- Troubleshooting: See section above

### Monitoring
- Health endpoint: `/api/v1/health`
- Metrics endpoint: `/api/v1/metrics`
- WebSocket status: Connection count in health response

### Emergency Procedures
1. Check service status: `systemctl status master-dashboard`
2. Review logs: `journalctl -u master-dashboard -f`
3. Restart if needed: `systemctl restart master-dashboard`
4. Contact support with logs and error details

---

**Master Dashboard v2 - Production Ready**  
**Last Updated:** June 15, 2024  
**Status:** ✅ Fully Tested & Validated for Ubuntu Deployment