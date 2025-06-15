# Project Summary
The Master Dashboard project is an advanced multi-machine monitoring system that provides real-time insights into system performance through an interactive 3D interface. It integrates various data sources and technologies, utilizing FastAPI for the backend, WebSocket for real-time communication, and React with Three.js for a dynamic frontend. The dashboard enhances operational efficiency and decision-making by allowing users to visualize machine metrics, manage alerts, and configure settings intuitively. It now includes client agents for Linux and Windows, enabling the collection and transmission of machine data to the server.

# Project Module Description
The project includes the following functional modules:
- **API Module**: Facilitates communication between the frontend and backend services, offering endpoints for machines, metrics, alerts, and settings.
- **WebSocket Service**: Ensures real-time data flow and notifications between the client and server.
- **3D Visualization**: Displays a 3D interactive representation of machine metrics in real-time, including detailed motherboard models.
- **Settings Management**: Provides an interface for users to configure system parameters and preferences.
- **Python Agents**: Monitors various machines and publishes metrics via WebSocket.
- **Client Agents**: New agents for Linux and Windows that collect system metrics and send them to the Master Dashboard server.

# Directory Tree
```
master_dashboard_complete/
├── app/
│   ├── api/
│   │   └── api_v1/
│   │       ├── routes/
│   │       │   ├── machines.py
│   │       │   └── metrics.py
│   │       └── api.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   ├── machine.py
│   │   └── metrics.py
│   ├── services/
│   │   ├── monitoring_service.py
│   │   └── websocket_manager.py
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AlertsPanel.jsx
│   │   │   ├── Dashboard3D.jsx
│   │   │   ├── MachineModel.jsx
│   │   │   └── MetricsPanel.jsx
│   │   ├── hooks/
│   │   │   └── useWebSocket.js
│   │   ├── utils/
│   │   │   └── api.js
│   │   ├── styles/
│   │   │   └── globals.css
│   │   └── App.jsx
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── clients/
│   ├── linux/
│   │   ├── agent.py
│   │   ├── config.json
│   │   ├── install.sh
│   │   ├── uninstall.sh
│   │   ├── master-dashboard-agent.service
│   │   └── requirements.txt
│   ├── windows/
│   │   ├── agent.py
│   │   ├── config.json
│   │   ├── install.ps1
│   │   ├── uninstall.ps1
│   │   └── install-service.ps1
│   └── shared/
│       ├── metrics_collector.py
│       ├── communication.py
│       ├── utils.py
│       ├── README.md
│       └── INSTALLATION.md
├── docker-compose.yml
├── master_dashboard_class_diagram.mermaid
├── master_dashboard_sequence_diagram.mermaid
└── README.md
```

# File Description Inventory
- **app/api/api_v1/routes/machines.py**: Contains API routes for machine management.
- **app/core/config.py**: Core configuration for the FastAPI application.
- **app/models/**: Defines data models for machines and metrics.
- **app/services/**: Services for monitoring and WebSocket management.
- **app/main.py**: Entry point for the FastAPI application.
- **frontend/src/components/**: React components for the user interface.
- **frontend/src/hooks/**: Custom hooks for WebSocket integration.
- **frontend/src/utils/**: Utility functions for API interactions, including demo mode.
- **frontend/src/styles/**: CSS styles for the application.
- **clients/linux/**: Contains client agent scripts for Linux, including installation and service files.
- **clients/windows/**: Contains client agent scripts for Windows, including installation scripts.
- **clients/shared/**: Shared utility modules for both client agents.
- **docker-compose.yml**: Configuration for container deployment.
- **master_dashboard_class_diagram.mermaid**: Diagram illustrating the architecture of the dashboard.
- **master_dashboard_sequence_diagram.mermaid**: Diagram showing the sequence of operations within the dashboard.
- **README.md**: Documentation and setup instructions.

# Technology Stack
- **Backend**: FastAPI, Python, WebSocket.
- **Frontend**: React, Three.js, Tailwind CSS.
- **Real-time**: WebSocket connections for live updates.
- **3D Graphics**: WebGL with optimized rendering.
- **Deployment**: Docker for container orchestration.

# Usage
To install dependencies, build, and run the application:
1. Navigate to the backend directory:
   ```bash
   cd master_dashboard_complete/app
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```
4. For the frontend, navigate to the frontend directory and install dependencies:
   ```bash
   cd frontend && npm install
   ```
5. Build the frontend application:
   ```bash
   npm run build
   ```
6. Start the frontend application:
   ```bash
   npm run dev
   ```
7. For client agents installation:
   - **Linux**: 
     ```bash
     curl -sSL https://raw.../install.sh | sudo bash
     ```
   - **Windows** (PowerShell Admin):
     ```powershell
     .\clients\windows\install.ps1
     ```
