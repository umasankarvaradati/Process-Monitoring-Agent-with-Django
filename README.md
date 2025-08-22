# Process Monitoring Agent

A comprehensive system for monitoring running processes on Windows machines with a Django backend and web interface.

## Architecture Overview

The system consists of three main components:

1. **Agent**: A Python script that collects process data and sends it to the backend
2. **Backend**: Django REST API that receives and stores process data
3. **Frontend**: Web interface to view process hierarchies and system information

## Features

- ✅ Real-time process monitoring (CPU, memory, parent-child relationships)
- ✅ System information collection (OS, CPU, RAM, storage)
- ✅ Interactive process tree with expandable/collapsible subprocesses
- ✅ Hostname identification and multiple host support
- ✅ RESTful API with authentication
- ✅ SQLite database storage
- ✅ Responsive web interface

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip
- Windows OS (for agent functionality)

### Backend Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Start the Django development server:
```bash
python manage.py runserver
```

The backend will be available at `http://127.0.0.1:8000/`

### Agent Setup

1. Ensure the backend is running
2. Configure the agent (optional environment variables):
   - `PROCESS_MONITOR_API_KEY`: API key for authentication (default: hardcoded)
   - `PROCESS_MONITOR_BACKEND`: Backend URL (default: http://127.0.0.1:8000/api/process-data/)
   - `PROCESS_MONITOR_INTERVAL`: Data collection interval in seconds (default: 60)
   - `PROCESS_MONITOR_CPU_SAMPLE_DELAY`: CPU sampling delay (default: 0.15)


### Compile Agent to EXE (Standalone Deployment)

To create a standalone executable that can be run by double-clicking (no Python installation required):

1. **Convert agent.py to EXE**:
```bash
pyinstaller agent.spec
```

2. **The executable will be created** in the `dist/agent/` directory as `agent.exe`

3. **Run the executable** by double-clicking on `agent.exe` or from command line:
```bash
dist/agent/agent.exe
```

The standalone executable includes all dependencies and can be distributed to any Windows machine without requiring Python installation.

## API Endpoints

### POST `/api/process-data/`
Receive process data from agents. Requires API key authentication.

**Headers:**
- `Authorization: Token {API_KEY}`
- `Content-Type: application/json`

**Payload:**
```json
{
  "hostname": "machine-name",
  "timestamp": "2024-01-01T12:00:00Z",
  "processes": [
    {
      "pid": 1234,
      "ppid": 567,
      "name": "process.exe",
      "cpu": 2.5,
      "memory": 324.66,
      "cmdline": "process.exe --arg",
      "username": "user"
    }
  ],
  "os": "Windows 10",
  "processor": "Intel Core i7",
  "cores": 4,
  "threads": 8,
  "ram_gb": 16.0,
  "used_ram_gb": 8.2,
  "free_ram_gb": 7.8,
  "storage_free_gb": 465.2,
  "storage_total_gb": 931.5,
  "storage_used_gb": 466.3
}
```

### GET `/api/latest/`
Retrieve the latest process snapshot for the frontend.

**Response:**
```json
{
  "hostname": "machine-name",
  "timestamp": "2024-01-01T12:00:00Z",
  "system": {
    "os": "Windows 10",
    "processor": "Intel Core i7",
    "cores": 4,
    "threads": 8,
    "ram_gb": 16.0,
    "used极_ram_gb": 8.2,
    "free_ram_gb": 7.8,
    "storage_free_gb": 465.2,
    "storage_total_gb": 931.5,
    "storage_used_gb": 466.3
  },
  "processes": [
    {
      "pid": 1234,
      "ppid": 567,
      "name": "process.exe",
      "cpu": 2.5,
      "memory": 324.66,
      "cmdline": "process.exe --arg",
      "username": "user"
    }
  ]
}
```

## Database Schema

### ProcessSnapshot
- `hostname`: CharField (100)
- `timestamp`: DateTimeField (auto_now_add)
- System info fields (os, processor, cores, threads, ram_gb, etc.)

### Process
- `snapshot`: ForeignKey to ProcessSnapshot
- `pid`: IntegerField (indexed)
- `ppid`: IntegerField (indexed, nullable)
- `name`: CharField (255)
- `cpu`: FloatField (CPU usage in percent)
- `memory`: FloatField (Memory in MB)
- `cmdline`: TextField
- `username`: CharField (150)

## Usage

1. **Start the backend**: Run `python manage.py runserver`
2. **Run the agent**: 
   - **Development**: Execute `python agent.py` 
   - **Production**: Convert `agent.py` to EXE using `pyinstaller agent.spec` and then run `dist/agent/agent.exe` by double-clicking
3. **Access the web interface**: Open `http://127.0.0.1:8000/` in your browser

The web interface allows you to:
- View system details for each host
- Browse process hierarchies with expandable trees
- See CPU and memory usage for each process
- Refresh data manually

## Security Notes

- The default API key is hardcoded for development purposes
- In production, use environment variables for sensitive data
- Consider adding rate limiting and additional authentication
- SQLite is used for simplicity; consider PostgreSQL for production

## Troubleshooting

**Agent can't connect to backend:**
- Check if Django server is running
- Verify the BACKEND_URL configuration
- Check firewall settings

**No data in frontend:**
- Ensure the agent has successfully sent data
- Check browser console for JavaScript errors

**High CPU usage during sampling:**
- Adjust CPU_SAMPLE_DELAY environment variable

## Future Enhancements

- Real-time updates with WebSockets
- Historical data viewing and charts
- Process filtering and search
- Alerting system for high resource usage
- Multi-user support with proper authentication
- Docker containerization
- Performance optimizations for large process trees
