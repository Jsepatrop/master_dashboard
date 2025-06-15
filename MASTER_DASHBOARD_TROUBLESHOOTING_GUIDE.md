# 🔧 MASTER DASHBOARD - TROUBLESHOOTING GUIDE

## 🎯 Quick Reference

**Version:** 2.0  
**Last Updated:** June 15, 2024  
**Emergency Contact:** System Administrator  
**System Status Check:** `curl http://localhost:8000/api/v1/health`

---

## 🚨 Emergency Quick Fixes

### System Not Responding
```bash
# 1. Check if services are running
sudo systemctl status master-dashboard

# 2. If failed, restart services
sudo systemctl restart master-dashboard

# 3. If still failing, emergency recovery
/opt/master-dashboard/scripts/emergency-recovery.sh
```

### Frontend Not Loading
```bash
# 1. Check frontend container
docker-compose logs frontend

# 2. Restart frontend only
docker-compose restart frontend

# 3. Check if API is accessible
curl http://localhost:8000/api/v1/health
```

### Database Connection Issues
```bash
# 1. Check PostgreSQL container
docker-compose logs postgres

# 2. Test database connection
docker exec -it master-dashboard-postgres psql -U dashboard -d master_dashboard

# 3. Restart database if needed
docker-compose restart postgres
```

---

## 🔍 Common Issues and Solutions

### Issue 1: Frontend Shows White Screen

**Symptoms:**
- Browser shows blank white page
- No console errors visible
- API endpoints respond correctly

**Diagnosis:**
```bash
# Check frontend container logs
docker-compose logs frontend

# Check if frontend is running
curl -I http://localhost:3000

# Check network connectivity
docker network inspect master-dashboard_default
```

**Solutions:**

**Solution A: Container Issue**
```bash
# Restart frontend container
docker-compose restart frontend

# If that fails, rebuild
docker-compose build frontend
docker-compose up -d frontend
```

**Solution B: Build Issue**
```bash
# Check if frontend built correctly
docker exec master-dashboard-frontend ls -la /app/dist

# Rebuild if dist folder is empty
cd /opt/master-dashboard/frontend
npm run build
docker-compose build frontend
docker-compose up -d frontend
```

**Solution C: Environment Variables**
```bash
# Check frontend environment
docker exec master-dashboard-frontend env | grep VITE

# Update .env file if needed
nano /opt/master-dashboard/.env
# Add: VITE_API_URL=http://localhost:8000
# Add: VITE_WS_URL=ws://localhost:8000

docker-compose up -d
```

### Issue 2: WebSocket Connection Failed

**Symptoms:**
- Real-time data not updating
- Console shows WebSocket errors
- 3D visualizations static

**Diagnosis:**
```bash
# Test WebSocket endpoint
wscat -c ws://localhost:8000/ws/metrics

# Check backend WebSocket logs
docker-compose logs backend | grep -i websocket

# Check active connections
curl http://localhost:8000/api/v1/health | jq '.metrics.active_connections'
```

**Solutions:**

**Solution A: CORS Issues**
```bash
# Check CORS configuration
grep CORS /opt/master-dashboard/.env

# Update CORS origins
echo "CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000" >> .env
docker-compose restart backend
```

**Solution B: WebSocket URL**
```bash
# Check frontend WebSocket URL
docker exec master-dashboard-frontend cat /app/src/utils/api.js | grep ws

# Update if incorrect
sed -i 's/wss:/ws:/g' /opt/master-dashboard/frontend/src/utils/api.js
docker-compose build frontend
docker-compose up -d frontend
```

**Solution C: Backend WebSocket Handler**
```bash
# Restart backend to reset WebSocket connections
docker-compose restart backend

# Check if WebSocket manager is working
docker-compose logs backend | grep -i "websocket.*connected"
```

### Issue 3: Database Connection Errors

**Symptoms:**
- API returns 500 errors
- Backend logs show database connection errors
- Health check shows database unhealthy

**Diagnosis:**
```bash
# Check PostgreSQL container status
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection manually
docker exec -it master-dashboard-postgres pg_isready -U dashboard
```

**Solutions:**

**Solution A: Container Not Running**
```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Wait for startup
sleep 15

# Verify connection
docker exec master-dashboard-postgres pg_isready -U dashboard
```

**Solution B: Wrong Credentials**
```bash
# Check database URL in environment
grep DATABASE_URL /opt/master-dashboard/.env

# Should be: postgresql://dashboard:password@postgres:5432/master_dashboard

# Update if incorrect
sed -i 's/DATABASE_URL=.*/DATABASE_URL=postgresql:\/\/dashboard:password@postgres:5432\/master_dashboard/' .env
docker-compose restart backend
```

**Solution C: Database Corruption**
```bash
# Check database integrity
docker exec master-dashboard-postgres psql -U dashboard -d master_dashboard -c "SELECT version();"

# If corrupted, restore from backup
/opt/master-dashboard/scripts/restore-system.sh $(ls -t /opt/master-dashboard/backups/manifest_*.json | head -1 | sed 's/.*manifest_//' | sed 's/.json//')
```

### Issue 4: High CPU Usage

**Symptoms:**
- System becomes slow
- CPU usage above 90%
- Containers consuming excessive resources

**Diagnosis:**
```bash
# Check overall CPU usage
top -bn1 | grep "Cpu(s)"

# Check container CPU usage
docker stats --no-stream

# Check for CPU-intensive processes
top -p $(pgrep -d, -f master-dashboard)
```

**Solutions:**

**Solution A: Container Resource Limits**
```bash
# Add resource limits to docker-compose.yml
echo "    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G" >> docker-compose.yml

docker-compose up -d
```

**Solution B: Memory Leak**
```bash
# Restart containers to clear memory leaks
docker-compose restart

# Monitor memory usage
watch -n 5 'docker stats --no-stream'
```

**Solution C: Too Many Connections**
```bash
# Check active connections
ss -tuln | grep -E ':(3000|8000|5432|6379)'

# Limit WebSocket connections in backend
echo "MAX_WEBSOCKET_CONNECTIONS=50" >> .env
docker-compose restart backend
```

### Issue 5: SSL/HTTPS Issues

**Symptoms:**
- HTTPS not working
- Certificate errors in browser
- Mixed content warnings

**Diagnosis:**
```bash
# Check SSL certificate
openssl x509 -in /opt/master-dashboard/ssl/dashboard.crt -text -noout

# Check certificate expiry
openssl x509 -in /opt/master-dashboard/ssl/dashboard.crt -noout -enddate

# Test HTTPS endpoint
curl -k https://localhost/api/v1/health
```

**Solutions:**

**Solution A: Generate New Certificate**
```bash
# Generate self-signed certificate
sudo mkdir -p /opt/master-dashboard/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/master-dashboard/ssl/dashboard.key \
  -out /opt/master-dashboard/ssl/dashboard.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Update nginx configuration
docker-compose restart nginx
```

**Solution B: Update Environment for HTTPS**
```bash
# Update frontend URLs for HTTPS
echo "VITE_API_URL=https://localhost" >> .env
echo "VITE_WS_URL=wss://localhost" >> .env

docker-compose build frontend
docker-compose up -d
```

---

## 📊 Diagnostic Tools

### System Health Check Script
```bash
#!/bin/bash
# Save as: /opt/master-dashboard/scripts/diagnose-system.sh

echo "🔍 MASTER DASHBOARD SYSTEM DIAGNOSIS"
echo "==================================="
date

# 1. Service Status
echo "\n1. SERVICE STATUS:"
sudo systemctl is-active master-dashboard
echo "Service Status: $(sudo systemctl is-active master-dashboard)"
echo "Service Enabled: $(sudo systemctl is-enabled master-dashboard)"

# 2. Container Status
echo "\n2. CONTAINER STATUS:"
docker-compose ps

# 3. Port Status
echo "\n3. PORT STATUS:"
echo "Port 3000 (Frontend): $(ss -tuln | grep :3000 | wc -l) listeners"
echo "Port 8000 (Backend): $(ss -tuln | grep :8000 | wc -l) listeners"
echo "Port 5432 (Database): $(ss -tuln | grep :5432 | wc -l) listeners"
echo "Port 6379 (Redis): $(ss -tuln | grep :6379 | wc -l) listeners"

# 4. API Health
echo "\n4. API HEALTH:"
API_RESPONSE=$(curl -s -w "HTTP_CODE:%{http_code}" http://localhost:8000/api/v1/health)
echo "API Response: $API_RESPONSE"

# 5. Database Status
echo "\n5. DATABASE STATUS:"
DB_STATUS=$(docker exec master-dashboard-postgres pg_isready -U dashboard -d master_dashboard 2>/dev/null)
echo "Database Status: $DB_STATUS"

# 6. Redis Status
echo "\n6. REDIS STATUS:"
REDIS_STATUS=$(docker exec master-dashboard-redis redis-cli ping 2>/dev/null)
echo "Redis Status: $REDIS_STATUS"

# 7. Resource Usage
echo "\n7. RESOURCE USAGE:"
echo "CPU: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}')"
echo "Memory: $(free -h | awk 'NR==2{printf "Used: %s, Available: %s", $3, $7}')"
echo "Disk: $(df -h /opt/master-dashboard | awk 'NR==2{printf "Used: %s, Available: %s", $3, $4}')"

# 8. Recent Errors
echo "\n8. RECENT ERRORS (Last 1 hour):"
ERROR_COUNT=$(sudo journalctl -u master-dashboard --since "1 hour ago" --grep "ERROR" --no-pager 2>/dev/null | wc -l)
echo "Error Count: $ERROR_COUNT"

if [ $ERROR_COUNT -gt 0 ]; then
    echo "Recent Errors:"
    sudo journalctl -u master-dashboard --since "1 hour ago" --grep "ERROR" --no-pager | tail -3
fi

# 9. Network Connectivity
echo "\n9. NETWORK CONNECTIVITY:"
echo "Localhost API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)"
echo "Frontend Access: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)"

# 10. Container Logs (last 10 lines)
echo "\n10. RECENT CONTAINER LOGS:"
echo "Backend logs:"
docker-compose logs --tail=5 backend 2>/dev/null | tail -3
echo "Frontend logs:"
docker-compose logs --tail=5 frontend 2>/dev/null | tail -3

echo "\n==================================="
echo "✅ DIAGNOSIS COMPLETED"
echo "\nIf issues persist, check detailed logs:"
echo "  sudo journalctl -u master-dashboard -f"
echo "  docker-compose logs -f"
```

### Performance Analysis Tool
```bash
#!/bin/bash
# Save as: /opt/master-dashboard/scripts/analyze-performance.sh

echo "📊 PERFORMANCE ANALYSIS"
echo "====================="

# 1. Response Time Analysis
echo "\n1. API RESPONSE TIMES:"
for i in {1..5}; do
    START=$(date +%s%N)
    curl -s http://localhost:8000/api/v1/health > /dev/null
    END=$(date +%s%N)
    TIME=$(( (END - START) / 1000000 ))
    echo "Request $i: ${TIME}ms"
done

# 2. Container Resource Analysis
echo "\n2. CONTAINER RESOURCES:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# 3. System Load Analysis
echo "\n3. SYSTEM LOAD:"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
echo "CPU Cores: $(nproc)"
echo "Memory Info: $(free -h | awk 'NR==2{printf "Total: %s, Used: %s (%.0f%%)", $2, $3, $3/$2*100}')"

# 4. Disk I/O Analysis
echo "\n4. DISK I/O:"
if command -v iostat > /dev/null; then
    iostat -x 1 1 | grep -A 20 "Device"
else
    echo "iostat not available - install sysstat package"
fi

# 5. Network Analysis
echo "\n5. NETWORK STATISTICS:"
echo "Active Connections by Port:"
ss -tuln | grep -E ':(3000|8000|5432|6379)' | awk '{print $1, $4}' | sort | uniq -c

# 6. Database Performance
echo "\n6. DATABASE PERFORMANCE:"
DB_CONNECTIONS=$(docker exec master-dashboard-postgres psql -U dashboard -d master_dashboard -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | xargs)
echo "Database Connections: ${DB_CONNECTIONS:-'N/A'}"

# 7. WebSocket Analysis
echo "\n7. WEBSOCKET STATUS:"
WS_CONNECTIONS=$(curl -s http://localhost:8000/api/v1/health | jq -r '.metrics.active_connections // "N/A"')
echo "Active WebSocket Connections: $WS_CONNECTIONS"

echo "\n====================="
echo "✅ PERFORMANCE ANALYSIS COMPLETED"
```

---

## 🔧 Advanced Troubleshooting

### Container Issues

**Problem: Container Won't Start**
```bash
# Check container status
docker-compose ps

# Check container logs
docker-compose logs [container_name]

# Check for port conflicts
ss -tuln | grep -E ':(3000|8000|5432|6379)'

# Remove and recreate containers
docker-compose down
docker-compose up -d
```

**Problem: Container Keeps Restarting**
```bash
# Check restart policy
docker inspect master-dashboard-backend | grep -A 5 RestartPolicy

# Check container exit code
docker-compose ps

# Disable restart to debug
docker update --restart=no master-dashboard-backend

# Run container manually for debugging
docker run -it --rm master-dashboard-backend /bin/bash
```

### Network Issues

**Problem: Containers Can't Communicate**
```bash
# Check Docker networks
docker network ls
docker network inspect master-dashboard_default

# Test connectivity between containers
docker exec master-dashboard-frontend ping backend
docker exec master-dashboard-backend ping postgres

# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

**Problem: External Access Issues**
```bash
# Check firewall rules
sudo ufw status
sudo iptables -L

# Check port binding
docker port master-dashboard-frontend
docker port master-dashboard-backend

# Test from external host
telnet your-server-ip 3000
telnet your-server-ip 8000
```

### Data Issues

**Problem: Data Not Persisting**
```bash
# Check Docker volumes
docker volume ls
docker volume inspect master-dashboard_postgres_data

# Check volume mounts
docker inspect master-dashboard-postgres | grep -A 10 Mounts

# Backup and recreate volumes if corrupted
docker-compose down
docker volume rm master-dashboard_postgres_data
docker-compose up -d
```

**Problem: Metrics Not Updating**
```bash
# Check simulator status
docker-compose logs simulator

# Test WebSocket connection manually
wscat -c ws://localhost:8000/ws/metrics

# Check backend WebSocket handler
docker-compose logs backend | grep -i websocket

# Restart data flow
docker-compose restart simulator backend
```

---

## 📋 Troubleshooting Checklist

### Before Contacting Support
- [ ] Run system diagnosis script
- [ ] Check service status
- [ ] Review container logs
- [ ] Test API endpoints
- [ ] Check system resources
- [ ] Review recent changes
- [ ] Attempt service restart
- [ ] Document error messages

### Information to Gather
- [ ] System specifications
- [ ] Error messages and logs
- [ ] Steps to reproduce issue
- [ ] Recent changes made
- [ ] Current system status
- [ ] Performance metrics
- [ ] Network configuration
- [ ] Security settings

---

## 🆘 Emergency Contacts

### Internal Support
- **System Administrator:** Available 24/7
- **DevOps Team:** Business hours support
- **Database Administrator:** On-call weekends

### External Support
- **Hosting Provider:** 24/7 infrastructure support
- **Security Team:** Emergency security issues
- **Vendor Support:** Business hours technical support

### Escalation Procedure
1. **Level 1:** System restart and basic troubleshooting
2. **Level 2:** Advanced diagnostics and log analysis
3. **Level 3:** Emergency recovery procedures
4. **Level 4:** Vendor support and expert consultation

---

**Master Dashboard Troubleshooting Guide v2.0**  
**Status:** ✅ Production Ready  
**Last Updated:** June 15, 2024  
**Emergency Hotline:** Contact System Administrator