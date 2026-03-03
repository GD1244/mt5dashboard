# VPS Deployment Guide for MT5 Dashboard

This guide explains how to deploy the MT5 Dashboard backend on a VPS running MetaTrader 5 instances.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         VPS                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   MT5 #1     │  │   MT5 #2     │  │   MT5 #N     │      │
│  │  (Terminal)  │  │  (Terminal)  │  │  (Terminal)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Python Backend (server.py)              │   │
│  │  • Socket.io Server (port 5000)                      │   │
│  │  • SQLite Database                                   │   │
│  │  • Metrics Engine                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ▲                                │
│  ┌─────────────────────────┴─────────────────────────────┐ │
│  │           VPS Collector (vps_collector.py)            │ │
│  │  • Connects to MT5 via MetaTrader5 API               │ │
│  │  • Collects account data every 60s                   │ │
│  │  • Sends to local server                             │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Vercel (Frontend)                        │
│              Next.js Dashboard (Static)                     │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- VPS with Ubuntu/Debian (2GB+ RAM recommended)
- MetaTrader 5 terminals installed and running
- Python 3.8+
- Open port 5000 for the backend server

## Quick Setup

### 1. Run the Setup Script

```bash
# Upload the backend files to your VPS
cd ~/
git clone <your-repo> mt5-dashboard
cd mt5-dashboard/backend

# Make setup script executable
chmod +x vps_setup.sh

# Run setup
./vps_setup.sh
```

This will:
- Install Python and dependencies
- Create virtual environment
- Install MetaTrader5 Python module
- Create systemd services

### 2. Configure MT5 Access

The collector uses the `MetaTrader5` Python module to connect to your MT5 terminals. Make sure:

1. MT5 terminals are running
2. Auto-trading is enabled (if needed)
3. Python can access MT5 via the terminal's API

### 3. Start the Services

```bash
cd ~/mt5-dashboard/backend

# Option A: Use the start script
./start_services.sh

# Option B: Use systemd
sudo systemctl start mt5-server
sudo systemctl start mt5-collector
```

### 4. Check Logs

```bash
# Server logs
tail -f server.log

# Collector logs
tail -f collector.log

# Systemd logs
sudo journalctl -u mt5-server -f
sudo journalctl -u mt5-collector -f
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# backend/.env
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
UPDATE_INTERVAL=60
```

### Multiple MT5 Instances

If you have multiple MT5 terminals on the same VPS, modify `vps_collector.py`:

```python
# Add paths to different MT5 data folders
collector.add_mt5_instance("/path/to/mt5/account1")
collector.add_mt5_instance("/path/to/mt5/account2")
```

## Firewall Configuration

Open port 5000 for the backend server:

```bash
# UFW (Ubuntu)
sudo ufw allow 5000/tcp

# Or iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

## Monitoring

### Check Service Status

```bash
# Systemd status
sudo systemctl status mt5-server
sudo systemctl status mt5-collector

# Process check
ps aux | grep python
```

### Auto-Restart on Crash

The systemd services are configured to auto-restart:

```ini
Restart=always
RestartSec=10
```

### Log Rotation

Set up log rotation to prevent disk fill:

```bash
sudo tee /etc/logrotate.d/mt5-dashboard > /dev/null <<EOF
/home/*/mt5-dashboard/backend/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 $(whoami) $(whoami)
}
EOF
```

## Troubleshooting

### MT5 Not Connecting

1. Check if MT5 is running:
```bash
ps aux | grep MetaTrader
```

2. Test MT5 Python connection:
```bash
cd ~/mt5-dashboard/backend
source venv/bin/activate
python mt5_connector.py
```

### Server Not Accessible

1. Check if port 5000 is listening:
```bash
netstat -tlnp | grep 5000
```

2. Check firewall:
```bash
sudo ufw status
```

3. Check server logs:
```bash
tail -f server.log
```

### High Memory Usage

If you have 40+ MT5 instances, consider:
- Using a VPS with more RAM (4GB+)
- Running MT5 terminals with minimal charts
- Closing unused MT5 instances periodically

## Security

1. **Use a firewall** - Only open port 5000
2. **Use HTTPS/WSS** - Consider using nginx as a reverse proxy with SSL
3. **Rate limiting** - The backend has built-in rate limiting
4. **Authentication** - Consider adding API key authentication

## Updating

To update the code:

```bash
cd ~/mt5-dashboard

# Pull latest changes
git pull

# Restart services
./backend/stop_services.sh
./backend/start_services.sh

# Or with systemd
sudo systemctl restart mt5-server
sudo systemctl restart mt5-collector