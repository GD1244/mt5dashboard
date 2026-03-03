# VPS Quick Setup (BEST Option!)

Yes! Run backend on your VPS + frontend on Vercel = PERFECT setup!

## Architecture

```
Vercel (Free)          Your VPS ($5/month)
├─ Next.js App    →    ├─ Python Backend
│   (Static)           │   Port 5000
│                      │   Always Running
│                      └─ SQLite Database
│
└─ User Dashboard      MT5 EA (Your Home PC)
    Web Interface           ↓
         ↑                  ↓ HTTP POST
         └──────────────────┘
```

## Step 1: SSH to Your VPS

```bash
ssh user@YOUR_VPS_IP
```

## Step 2: Install Python & Git

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv git -y

# Or CentOS/RHEL
sudo yum install python3 python3-pip git -y
```

## Step 3: Clone & Setup

```bash
cd /opt
sudo git clone https://github.com/GD1244/mt5dashboard.git
cd mt5dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

## Step 4: Start Backend (Test Mode)

```bash
cd backend
python server.py
```

You should see: "Server started on http://0.0.0.0:5000"

**Test it:**
```bash
curl http://YOUR_VPS_IP:5000/api/accounts
```

## Step 5: Keep Backend Running (PM2)

Install Node.js & PM2:
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
sudo npm install -g pm2

# Start backend with PM2
cd /opt/mt5dashboard/backend
pm2 start server.py --name mt5-dashboard --interpreter python3

# Save PM2 config
pm2 save
pm2 startup
```

## Step 6: Open Firewall Port

```bash
# Ubuntu/Debian with UFW
sudo ufw allow 5000/tcp

# Or CentOS with firewalld
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## Step 7: Update Frontend

Edit `frontend/.env.production`:
```
NEXT_PUBLIC_SOCKET_URL=http://YOUR_VPS_IP:5000
NEXT_PUBLIC_API_URL=http://YOUR_VPS_IP:5000
```

**Deploy to Vercel:**
```bash
cd frontend
npm i -g vercel
vercel --prod
```

## Step 8: Configure MT5 EA

In MetaTrader 5:
1. Install `mt5_ea/DashboardConnector.mq5`
2. Set `DashboardURL` to: `http://YOUR_VPS_IP:5000`
3. Enable WebRequests
4. Attach to chart

## Done! 🎉

- Dashboard: `https://your-app.vercel.app`
- Backend: `http://YOUR_VPS_IP:5000`
- Data flows: MT5 EA → VPS Backend → Vercel Frontend

## Optional: Use Domain + SSL

Instead of IP:port, use a domain:

```bash
# Install Nginx
sudo apt install nginx

# Create config
sudo nano /etc/nginx/sites-available/mt5-dashboard
```

Add:
```nginx
server {
    listen 80;
    server_name dashboard.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/mt5-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Then use `https://dashboard.yourdomain.com` in your frontend!