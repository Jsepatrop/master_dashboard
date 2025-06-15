# Project Summary
The Master Dashboard Revolutionary project is a cutting-edge multi-machine monitoring system that provides real-time 3D visualization of hardware metrics. It aims to enhance operational efficiency for IT administrators and data center managers by integrating various technologies such as FastAPI for the backend, WebSocket for real-time communication, and React with Three.js for an interactive, cyberpunk-themed frontend. This system allows users to autonomously monitor machine performance, manage configurations, and receive alerts while delivering an impressive visual experience.

# Project Module Description
The project consists of the following functional modules:
- **Backend Module**: Built with FastAPI, it handles API requests, manages machine configurations, and processes metrics.
- **WebSocket Service**: Facilitates real-time updates and notifications to connected clients.
- **3D Visualization Module**: Utilizes Three.js to render interactive 3D models of machine metrics and hardware components.
- **Client Agent**: Monitors hardware on individual machines and sends metrics to the server.
- **Simulator Module**: Generates realistic hardware data for testing and demonstration purposes.
- **Alert Management**: Monitors metrics against defined thresholds and triggers alerts.

# Directory Tree
```
master_dashboard_revolutionary/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── alerts.py
│   │   │       │   ├── configuration.py
│   │   │       │   ├── health.py
│   │   │       │   ├── machines.py
│   │   │       │   └── metrics.py
│   │   │       └── api.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── websocket_manager.py
│   │   ├── models/
│   │   │   ├── alerts.py
│   │   │   ├── configuration.py
│   │   │   ├── hardware.py
│   │   │   └── metrics.py
│   │   ├── schemas/
│   │   │   ├── alerts.py
│   │   │   ├── configuration.py
│   │   │   ├── hardware.py
│   │   │   └── metrics.py
│   │   ├── services/
│   │   │   ├── alert_manager.py
│   │   │   ├── hardware_simulator.py
│   │   │   └── metrics_processor.py
│   │   └── main.py
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       │   ├── AlertsPanel.tsx
│       │   ├── ConfigurationPanel.tsx
│       │   ├── Dashboard3D.tsx
│       │   ├── LoadingScreen.tsx
│       │   ├── MachineList.tsx
│       │   ├── MetricsPanel.tsx
│       │   └── MotherboardViewer.tsx
│       ├── hooks/
│       │   ├── useApi.ts
│       │   ├── useThree.ts
│       │   └── useWebSocket.ts
│       ├── utils/
│       │   ├── api.ts
│       │   ├── colors.ts
│       │   └── constants.ts
│       └── styles/
│           └── globals.css
├── nginx/
│   └── nginx.conf
├── simulator/
│   └── simulator_server.py
└── start.sh
```

# File Description Inventory
- **backend/app/api/v1/endpoints/**: Contains API endpoints for managing machines, metrics, configuration, and alerts.
- **backend/app/core/**: Core functionality including configuration, database connection, and WebSocket management.
- **backend/app/models/**: Data models for alerts, configuration, and hardware metrics.
- **backend/app/schemas/**: Pydantic schemas for data validation.
- **backend/app/services/**: Contains services for alert management and hardware simulation.
- **frontend/src/**: Contains all frontend components, hooks, utilities, and styles for the dashboard.
- **nginx/nginx.conf**: Configuration file for Nginx as a reverse proxy.
- **simulator/simulator_server.py**: Standalone simulator for generating demo hardware data.
- **start.sh**: Script to start the entire application stack.

# Technology Stack
- **Backend**: FastAPI, PostgreSQL, Redis, WebSocket.
- **Frontend**: React, TypeScript, Three.js, Tailwind CSS.
- **Real-time Communication**: WebSocket for live updates.
- **Containerization**: Docker for deployment.
- **Monitoring and Logging**: Prometheus for metrics, Nginx for reverse proxy.

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
