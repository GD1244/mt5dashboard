#!/bin/bash

# Create .env.production file for Vercel deployment
# Usage: ./create-env.sh YOUR_VPS_IP

if [ -z "$1" ]; then
    echo "Usage: ./create-env.sh YOUR_VPS_IP"
    echo "Example: ./create-env.sh 192.168.1.100"
    exit 1
fi

VPS_IP=$1

cat > .env.production << EOF
# Production environment variables for Vercel
# Connected to VPS backend at ${VPS_IP}

NEXT_PUBLIC_SOCKET_URL=http://${VPS_IP}:5000
NEXT_PUBLIC_API_URL=http://${VPS_IP}:5000
EOF

echo "✅ Created .env.production with VPS IP: ${VPS_IP}"
echo ""
echo "Contents:"
cat .env.production