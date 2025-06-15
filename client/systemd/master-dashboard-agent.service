[Unit]
Description=Master Dashboard System Monitoring Agent
Documentation=https://github.com/yourusername/master-dashboard-revolutionary
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=mdagent
Group=mdagent
WorkingDirectory=/opt/master-dashboard-agent
ExecStart=/usr/bin/python3 /opt/master-dashboard-agent/agent.py /etc/master-dashboard-agent/config.yaml
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StartLimitBurst=3
TimeoutStartSec=30
TimeoutStopSec=30

# Environment
Environment=PYTHONPATH=/opt/master-dashboard-agent
Environment=PYTHONUNBUFFERED=1

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=master-dashboard-agent

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictRealtime=yes
RestrictNamespaces=yes
RestrictSUIDSGID=yes
LockPersonality=yes
MemoryDenyWriteExecute=yes
SystemCallArchitectures=native

# File system permissions
ReadWritePaths=/var/log/master-dashboard-agent /etc/master-dashboard-agent
ReadOnlyPaths=/etc/master-dashboard-agent/config.yaml

# Network restrictions (comment out if agent needs broader network access)
# RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
# IPAddressDeny=any
# IPAddressAllow=localhost
# IPAddressAllow=10.0.0.0/8
# IPAddressAllow=172.16.0.0/12
# IPAddressAllow=192.168.0.0/16

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Process management
KillMode=mixed
KillSignal=SIGTERM
FinalKillSignal=SIGKILL
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target