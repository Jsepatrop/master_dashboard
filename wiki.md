# Project Summary
The Master Dashboard Revolutionary project is a cutting-edge 3D infrastructure monitoring dashboard designed to provide real-time system metrics for IT administrators and data center managers. Utilizing FastAPI for backend services, WebSocket for real-time communication, and React with Three.js for a visually immersive frontend, this application enables users to monitor hardware performance, manage configurations, and receive alerts through an engaging cyberpunk-themed interface, thereby enhancing operational efficiency and decision-making.

# Project Module Description
The project consists of the following functional modules:
- **Backend Module**: Built with FastAPI, handles API requests, machine configurations, and metrics processing.
- **WebSocket Service**: Provides real-time updates and notifications to connected clients.
- **3D Visualization Module**: Utilizes Three.js for interactive 3D models of hardware metrics and components.
- **Client Agent**: A lightweight program that runs on monitored machines, collecting and sending real system metrics (CPU, RAM, disk, network) to the server.
- **Simulator Module**: Generates realistic hardware data for testing and demonstration (to be replaced by the Client Agent).
- **Alert Management**: Monitors metrics against thresholds and triggers alerts.

# Directory Tree
```
master_dashboard_revolutionary/
├── backend/                         # API FastAPI
│   ├── app/                         # Application FastAPI
│   │   ├── api/                     # Endpoints API
│   │   ├── core/                    # Core configuration
│   │   ├── models/                  # Data models
│   │   ├── schemas/                 # Pydantic schemas
│   │   └── services/                # Business logic services
│   ├── requirements.txt             # Python dependencies
│   └── main.py                      # Entry point for API
├── frontend/                        # Application React
│   ├── src/                         # Source files
│   ├── package.json                 # npm dependencies
│   ├── vite.config.js               # Vite configuration
│   ├── tailwind.config.js           # Tailwind configuration
│   └── index.html                   # HTML entry point
├── client/                          # Client agent for system monitoring
│   ├── agent.py                     # Main agent
│   ├── config.yaml                  # Configuration file
│   ├── requirements.txt             # Dependencies for the client
│   ├── install.py                   # Installation script
│   ├── service_manager.py           # Service management utilities
│   ├── collectors/                  # Collectors for system metrics
│   │   ├── system_metrics.py        # CPU, memory, disk metrics
│   │   ├── hardware_sensors.py      # Temperature, fan metrics
│   │   ├── network_stats.py         # Network monitoring
│   │   ├── process_monitor.py       # Process tracking
│   │   └── hardware_detector.py     # Hardware detection
│   ├── communication/               # Communication modules
│   │   ├── websocket_client.py       # WebSocket client
│   │   └── http_client.py           # HTTP client
│   ├── utils/                       # Utility functions
│   │   ├── logger.py                # Logging utilities
│   │   └── crypto.py                # Cryptographic utilities
│   ├── scripts/                     # Installation scripts
│   │   ├── install.sh               # Linux installation script
│   │   ├── install.bat              # Windows installation script
│   │   ├── uninstall.sh             # Linux uninstallation script
│   │   └── uninstall.bat            # Windows uninstallation script
│   ├── systemd/                     # Linux service configuration
│   │   └── master-dashboard-agent.service # Systemd service file
│   └── windows/                     # Windows service configuration
│       └── service.py               # Windows service wrapper
├── start.sh                         # Startup script
├── README.md                        # Main documentation
├── CHANGELOG.md                     # Version history
├── CONTRIBUTING.md                  # Contribution guidelines
├── LICENSE                           # MIT License
└── PROJECT_SUMMARY.md               # Project summary
```

# File Description Inventory
- **backend/app/api/**: API endpoints for managing machines, metrics, configuration, and alerts.
- **backend/app/core/**: Core functionalities including configuration, database connection, and WebSocket management.
- **backend/app/models/**: Data models for alerts, configuration, and hardware metrics.
- **backend/app/schemas/**: Pydantic schemas for data validation.
- **backend/app/services/**: Services for alert management and hardware simulation.
- **frontend/src/**: Frontend components, hooks, utilities, and styles for the dashboard.
- **client/**: Contains the client agent code for system monitoring, including collectors, communication modules, and installation scripts.
- **start.sh**: Script to initiate the entire application stack.
- **README.md**: Comprehensive documentation with detailed instructions.
- **CHANGELOG.md**: Log of notable changes and version history.
- **CONTRIBUTING.md**: Guidelines for contributing to the project.
- **LICENSE**: License information for the project.
- **PROJECT_SUMMARY.md**: Executive summary of the project.

# Technology Stack
- **Backend**: FastAPI, PostgreSQL, Redis, WebSocket.
- **Frontend**: React, TypeScript, Three.js, Tailwind CSS.
- **Real-time Communication**: WebSocket for live updates.
- **Containerization**: Docker for deployment.
- **Monitoring and Logging**: Prometheus for metrics, Nginx for reverse proxy.
- **Client Agent**: Python for cross-platform support.

# Usage
To install dependencies, build, and run the application:
1. Navigate to the backend directory:
   ```bash
   cd master_dashboard_revolutionary/backend
   ```
2. Build and start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. For the frontend, navigate to the frontend directory and install dependencies:
   ```bash
   cd frontend && npm install
   ```
4. Build the frontend application:
   ```bash
   npm run build
   ```
5. Start the frontend application:
   ```bash
   npm run dev
   ```
6. For the client agent, install it on target machines using the provided scripts.
