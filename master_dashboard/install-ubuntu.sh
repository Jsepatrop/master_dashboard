#!/bin/bash

# Master Dashboard Ubuntu Installation Script
set -e

echo "🚀 Installing Master Dashboard on Ubuntu..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update -y

# Install dependencies
echo "📦 Installing dependencies..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    python3 \
    python3-pip \
    python3-dev \
    gcc \
    linux-headers-$(uname -r)

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose already installed"
fi

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/master-dashboard
cd /opt/master-dashboard

# Copy application files (assuming current directory contains the app)
if [[ -f "docker-compose.yml" ]]; then
    echo "✅ Application files found in current directory"
else
    echo "❌ Please run this script from the master-dashboard directory"
    exit 1
fi

# Setup environment
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        echo "📝 Created .env file from template"
        echo "⚠️  Please edit /opt/master-dashboard/.env with your configuration"
    fi
fi

# Setup systemd service
if [[ -f "systemd/master-dashboard.service" ]]; then
    cp systemd/master-dashboard.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable master-dashboard
    echo "✅ Systemd service installed"
fi

# Create logs directory
mkdir -p /var/log/master-dashboard

# Setup firewall rules
if command -v ufw &> /dev/null; then
    echo "🔥 Configuring firewall..."
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 8000/tcp
    ufw allow 3000/tcp
fi

echo "✅ Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit /opt/master-dashboard/.env with your configuration"
echo "2. Start the service: systemctl start master-dashboard"
echo "3. Check status: systemctl status master-dashboard"
echo "4. Access the dashboard at: http://your-server-ip:3000"
