# Master Dashboard Agent

A comprehensive system monitoring agent that collects real-time hardware and system metrics and sends them to the Master Dashboard server for visualization and analysis.

## Features

### 🖥️ System Monitoring
- **CPU Metrics**: Usage, frequency, load average, core-specific data
- **Memory Monitoring**: RAM, swap, detailed memory breakdown
- **Disk Statistics**: Usage, I/O operations, partition information
- **Network Analytics**: Interface statistics, connection tracking, traffic rates

### 🔧 Hardware Detection
- **Automatic Discovery**: Detects all available hardware components
- **GPU Support**: NVIDIA (with CUDA), AMD, Intel graphics
- **TPU Detection**: Google TPU, Coral Edge TPU, other AI accelerators
- **Sensor Monitoring**: Temperature, fan speeds, voltages, power consumption
- **Smart Adaptation**: Configures collection based on available hardware

### 📊 Process Monitoring
- **Comprehensive Tracking**: All running processes with detailed metrics
- **Resource Usage**: CPU, memory, disk I/O, network per process
- **GPU Process Tracking**: NVIDIA GPU memory usage by process
- **Top Consumers**: Real-time ranking by resource consumption
- **Process Trees**: Parent-child relationships and process hierarchies

### 🌐 Network Intelligence
- **Interface Analysis**: Detailed network interface information
- **Connection Monitoring**: Active network connections per process
- **Traffic Analysis**: Real-time bandwidth usage and transfer rates
- **DNS Configuration**: Nameserver and search domain detection

### 🔒 Security & Authentication
- **Secure Communication**: TLS/SSL encrypted data transmission
- **API Key Authentication**: Robust authentication with the dashboard server
- **Machine Fingerprinting**: Unique, persistent machine identification
- **Data Integrity**: Cryptographic signatures and checksums

### 🚀 Real-time Communication
- **WebSocket Support**: Low-latency real-time data streaming
- **HTTP Fallback**: Reliable data transmission with retry logic
- **Automatic Reconnection**: Resilient connection management
- **Batch Processing**: Efficient bulk data transmission

## Installation

### Prerequisites

- **Python 3.8+** (3.9+ recommended)
- **Operating System**: Windows 10+, Linux (Ubuntu 18.04+, CentOS 7+), macOS 10.15+
- **Network Access**: Connection to Master Dashboard server
- **Permissions**: Administrator/root privileges for installation

### Quick Install

#### Windows

1. **Download** the client agent files to your system
2. **Run as Administrator**: Right-click on `scripts/install.bat` and select "Run as administrator"
3. **Follow the prompts** to configure your server URL and API key
4. **Service Installation**: The script will automatically install and start the Windows service

```cmd
# Manual installation
cd master-dashboard-agent\client
scripts\install.bat

# Service management
sc start MasterDashboardAgent    # Start service
sc stop MasterDashboardAgent     # Stop service
sc query MasterDashboardAgent    # Check status
```

#### Linux

1. **Download** and extract the client agent files
2. **Run the installer** with root privileges
3. **Configure** server connection and API key
4. **Systemd Service**: Automatically installs and enables the systemd service

```bash
# Installation
sudo chmod +x scripts/install.sh
sudo ./scripts/install.sh

# Service management
sudo systemctl start master-dashboard-agent
sudo systemctl stop master-dashboard-agent
sudo systemctl status master-dashboard-agent
sudo systemctl enable master-dashboard-agent  # Enable auto-start
```

#### macOS

```bash
# Install dependencies
brew install python@3.9
pip3 install -r requirements.txt

# Manual run (for testing)
python3 agent.py config.yaml

# For production, use launchd (advanced users)
```

### Manual Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the Agent**:
   - Copy `config.yaml` to your desired location
   - Edit the configuration file with your server details
   - Set your API key and server URL

3. **Run the Agent**:
   ```bash
   python agent.py /path/to/config.yaml
   ```

## Configuration

### Basic Configuration

Edit `config.yaml` to configure the agent:

```yaml
server:
  url: "http://your-dashboard.com:8000"
  websocket_url: "ws://your-dashboard.com:8000/ws"
  reconnect_interval: 5

authentication:
  api_key: "your-api-key-here"

collection:
  interval: 5  # Collect metrics every 5 seconds
  metrics:
    system: true      # CPU, Memory, Disk
    hardware: true    # Temperature, Fans, GPU
    network: true     # Network interfaces
    processes: true   # Process monitoring

logging:
  level: "INFO"
  file: "agent.log"
```

### Advanced Configuration

#### Hardware Monitoring
```yaml
collection:
  hardware_config:
    temperature: true
    fan_speed: true
    voltage: false
    temp_unit: "celsius"
```

#### Process Monitoring
```yaml
collection:
  system_config:
    per_core_cpu: true
    disk_io: true
    memory_details: true
```

#### Network Monitoring
```yaml
collection:
  network_config:
    interface_details: true
    connection_stats: true
```

## Usage

### Service Management

#### Windows
```cmd
# Service status
sc query MasterDashboardAgent

# Start/Stop service
sc start MasterDashboardAgent
sc stop MasterDashboardAgent

# View logs
type "%ProgramData%\MasterDashboardAgent\logs\agent.log"
```

#### Linux
```bash
# Service status
sudo systemctl status master-dashboard-agent

# View logs
sudo journalctl -u master-dashboard-agent -f
sudo tail -f /var/log/master-dashboard-agent/agent.log
```

### Manual Execution

```bash
# Run with default config
python agent.py

# Run with custom config
python agent.py /path/to/custom-config.yaml

# Debug mode
python agent.py --debug
```

### Service Manager Tool

```bash
# Check service status
python service_manager.py status

# Start/stop service
python service_manager.py start
python service_manager.py stop
python service_manager.py restart

# View logs
python service_manager.py logs --lines 100
```

## Hardware Detection

The agent automatically detects and adapts to available hardware:

### Supported Hardware

- **CPUs**: Intel, AMD, ARM (Apple Silicon)
- **GPUs**: NVIDIA (CUDA), AMD (ROCm), Intel Arc
- **TPUs**: Google Cloud TPU, Coral Edge TPU
- **Memory**: DDR3/DDR4/DDR5, ECC memory
- **Storage**: HDD, SSD, NVMe, RAID arrays
- **Network**: Ethernet, Wi-Fi, Bluetooth interfaces
- **Sensors**: lm-sensors (Linux), WMI (Windows), SMC (macOS)

### Detection Process

1. **System Scan**: Identifies CPU, memory, and basic system info
2. **GPU Detection**: Scans for NVIDIA, AMD, Intel graphics
3. **TPU Discovery**: Checks for AI accelerators and edge devices
4. **Sensor Mapping**: Maps available temperature and fan sensors
5. **Network Analysis**: Catalogs all network interfaces
6. **Capability Assessment**: Determines what metrics can be collected

## Metrics Collected

### System Metrics
- CPU usage (overall and per-core)
- Memory usage (RAM, swap, buffers, cache)
- Disk usage and I/O statistics
- System uptime and load average
- Running processes and their resource usage

### Hardware Metrics
- **Temperature**: CPU, GPU, motherboard sensors
- **Fan Speeds**: All detected cooling fans
- **Power**: Battery status, power consumption
- **GPU**: Memory usage, clock speeds, temperature
- **Network**: Interface statistics, connection states

### Process Metrics
- Process list with PID, name, user
- CPU and memory usage per process
- Disk I/O and network usage per process
- GPU memory usage per process (NVIDIA)
- Process relationships (parent/child)

## Troubleshooting

### Common Issues

#### Agent Won't Start
```bash
# Check Python version
python --version

# Verify dependencies
pip check
pip install -r requirements.txt

# Check configuration
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

#### Connection Issues
```bash
# Test server connectivity
curl http://your-server:8000/api/v1/health

# Check firewall settings
telnet your-server 8000

# Verify API key
grep api_key config.yaml
```

#### Permission Errors
```bash
# Linux: Check if running as root for system metrics
sudo python agent.py

# Windows: Run as Administrator
# Right-click -> "Run as administrator"
```

#### Hardware Detection Issues
```bash
# Linux: Install sensor tools
sudo apt-get install lm-sensors
sudo sensors-detect

# NVIDIA: Install NVIDIA drivers and CUDA
nvidia-smi

# Check Python module availability
python -c "import pynvml; print('NVIDIA support available')"
```

### Log Analysis

#### Enable Debug Logging
```yaml
logging:
  level: "DEBUG"
  console: true
```

#### Common Log Messages
- `Hardware detector initialized` - Hardware detection started
- `NVIDIA ML not available` - No NVIDIA GPU or drivers
- `WebSocket connection established` - Successfully connected
- `Metrics collected and sent` - Normal operation
- `Authentication failed` - Check API key

## Development

### Project Structure
```
client/
├── agent.py                 # Main agent entry point
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
├── collectors/             # Metric collection modules
│   ├── system_metrics.py   # System monitoring
│   ├── hardware_sensors.py # Hardware sensors
│   ├── network_stats.py    # Network statistics
│   ├── process_monitor.py  # Process tracking
│   └── hardware_detector.py # Hardware detection
├── communication/          # Communication modules
│   ├── websocket_client.py # WebSocket client
│   └── http_client.py      # HTTP client
├── utils/                  # Utility modules
│   ├── logger.py           # Logging utilities
│   └── crypto.py           # Cryptographic functions
├── scripts/                # Installation scripts
├── systemd/                # Linux service files
└── windows/                # Windows service wrapper
```

### Adding Custom Collectors

1. Create a new collector in `collectors/`
2. Implement the `collect()` async method
3. Return metrics in dictionary format
4. Register in main agent configuration

```python
class CustomCollector:
    def __init__(self, logger):
        self.logger = logger
    
    async def collect(self):
        return {
            'timestamp': time.time(),
            'custom_metric': 42
        }
```

## API Reference

### Agent Class
```python
from agent import MasterDashboardAgent

# Initialize agent
agent = MasterDashboardAgent('config.yaml')

# Start monitoring
await agent.start()

# Stop monitoring
await agent.stop()
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `collection.interval` | int | 5 | Metrics collection interval (seconds) |
| `collection.batch_size` | int | 10 | Batch size for metrics transmission |
| `server.reconnect_interval` | int | 5 | WebSocket reconnection interval |
| `logging.level` | string | "INFO" | Log level (DEBUG, INFO, WARNING, ERROR) |
| `logging.max_size` | int | 10 | Maximum log file size (MB) |

## License

MIT License - see LICENSE file for details.

## Support

For issues and support:
1. Check the troubleshooting section above
2. Review log files for error messages
3. Verify configuration and network connectivity
4. Ensure all dependencies are installed

## Changelog

### Version 1.0.0
- Initial release
- Cross-platform support (Windows, Linux, macOS)
- Comprehensive hardware detection
- Real-time process monitoring
- WebSocket and HTTP communication
- Automatic service installation
- Extensive configuration options