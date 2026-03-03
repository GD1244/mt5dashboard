#!/bin/bash
# VPS Setup Script for MT5 Dashboard
# Run this on your VPS to set up the collector service

set -e

echo "=============================================="
echo "MT5 Dashboard VPS Setup"
echo "=============================================="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
echo "Installing Python..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install system dependencies for MT5 (if using Wine)
echo "Installing dependencies..."
sudo apt-get install -y wget curl git

# Create app directory
APP_DIR="$HOME/mt5-dashboard"
mkdir -p $APP_DIR
cd $APP_DIR

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install aiohttp aiohttp-cors python-socketio[asyncio-client] MetaTrader5

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/mt5-collector.service > /dev/null <<EOF
[Unit]
Description=MT5 Dashboard Collector
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="PYTHONPATH=$APP_DIR"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/vps_collector.py --server http://localhost:5000 --interval 60
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create the server service too
sudo tee /etc/systemd/system/mt5-server.service > /dev/null <<EOF
[Unit]
Description=MT5 Dashboard Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="PYTHONPATH=$APP_DIR"
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create start script
cat > start_services.sh <<'EOF'
#!/bin/bash
# Start MT5 Dashboard services

echo "Starting MT5 Dashboard services..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Please don't run as root"
   exit 1
fi

cd "$(dirname "$0")"
source venv/bin/activate

# Start server in background
echo "Starting server..."
nohup python server.py > server.log 2>&1 &
echo $! > server.pid

# Wait for server to start
sleep 3

# Start collector in background
echo "Starting collector..."
nohup python vps_collector.py > collector.log 2>&1 &
echo $! > collector.pid

echo "Services started!"
echo "Server PID: $(cat server.pid)"
echo "Collector PID: $(cat collector.pid)"
echo ""
echo "View logs:"
echo "  tail -f server.log"
echo "  tail -f collector.log"
EOF
chmod +x start_services.sh

# Create stop script
cat > stop_services.sh <<'EOF'
#!/bin/bash
# Stop MT5 Dashboard services

cd "$(dirname "$0")"

if [ -f server.pid ]; then
    echo "Stopping server..."
    kill $(cat server.pid) 2>/dev/null || true
    rm server.pid
fi

if [ -f collector.pid ]; then
    echo "Stopping collector..."
    kill $(cat collector.pid) 2>/dev/null || true
    rm collector.pid
fi

echo "Services stopped!"
EOF
chmod +x stop_services.sh

# Enable and start services with systemd
sudo systemctl daemon-reload
sudo systemctl enable mt5-server.service
sudo systemctl enable mt5-collector.service

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Copy your Python files to: $APP_DIR"
echo "2. Edit the server URL in vps_collector.py if needed"
echo "3. Start services:"
echo "   ./start_services.sh"
echo ""
echo "Or use systemd:"
echo "   sudo systemctl start mt5-server"
echo "   sudo systemctl start mt5-collector"
echo ""
echo "View logs:"
echo "   tail -f server.log"
echo "   tail -f collector.log"
echo ""
echo "Check status:"
echo "   sudo systemctl status mt5-server"
echo "   sudo systemctl status mt5-collector"