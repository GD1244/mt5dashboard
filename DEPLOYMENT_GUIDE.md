# MT5 Dashboard Deployment Guide

## Overview

The MT5 Dashboard has two components that need separate deployment:
1. **Frontend** (Next.js) → Deploy to **Vercel**
2. **Backend** (Python/Socket.io) → Deploy to **VPS/Railway/Render**

---

## Option 1: Deploy Frontend to Vercel (Easiest)

### Step 1: Prepare Frontend

```bash
cd frontend

# Make sure you have a Vercel account
# Install Vercel CLI if not already installed
npm i -g vercel

# Login to Vercel
vercel login
```

### Step 2: Set Environment Variables

Before deploying, update `frontend/.env.production`:

```bash
# Replace with your backend URL (see backend deployment options below)
NEXT_PUBLIC_SOCKET_URL=https://your-backend-url.com
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Step 3: Deploy

```bash
# Deploy to Vercel
vercel --prod
```

Or use Git integration:
1. Push code to GitHub
2. Connect repo to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy

---

## Option 2: Deploy Backend (Choose One)

### A. VPS/Server (Recommended for Production)

**Best for:** Full control, lowest latency, persistent WebSocket connections

#### Requirements
- Linux VPS (Ubuntu 20.04+)
- Python 3.9+
- Domain name (optional but recommended)

#### Deployment Steps

```bash
# 1. SSH into your VPS
ssh user@your-vps-ip

# 2. Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx

# 3. Clone/upload your code
git clone <your-repo> /opt/mt5-dashboard
cd /opt/mt5-dashboard

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 5. Run the server
# Option A: Direct (for testing)
cd backend && python server.py

# Option B: With PM2 (for production)
npm install -g pm2
pm2 start backend/server.py --name mt5-dashboard --interpreter python3
pm2 save
pm2 startup

# 6. Set up Nginx reverse proxy (optional but recommended)
sudo nano /etc/nginx/sites-available/mt5-dashboard
```

Add this Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/mt5-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 7. Set up SSL (optional but recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### B. Railway (Easiest)

**Best for:** Quick setup, auto-deploy from GitHub

#### Steps
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway will auto-detect `railway.toml` and deploy
6. Once deployed, copy the service URL
7. Update `NEXT_PUBLIC_SOCKET_URL` in Vercel with this URL

**Cost:** Free tier available (500 hours/month)

### C. Render

**Best for:** Free tier, simple setup

#### Steps
1. Go to [render.com](https://render.com)
2. Create Web Service
3. Connect your GitHub repo
4. Use these settings:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && python server.py`
5. Add environment variable: `PORT=5000`
6. Deploy

**Note:** Render free tier spins down after 15 min inactivity (not ideal for real-time dashboard)

---

## Complete Deployment Workflow

### Recommended Setup for Production

```
┌─────────────────┐     ┌──────────────────┐
│  Vercel (Free)  │────→│  Your Domain     │
│  Next.js App    │     │  (SSL-enabled)   │
└─────────────────┘     └──────────────────┘
                               │
                               │ WebSocket
                               │
                        ┌──────▼──────┐
                        │   VPS       │
                        │  (Python)   │
                        │  Port 5000  │
                        └──────┬──────┘
                               │
                        ┌──────▼──────┐
                        │  EA (MT5)   │
                        │  Home PC    │
                        └─────────────┘
```

### Deployment Checklist

#### Frontend (Vercel)
- [ ] Push code to GitHub
- [ ] Connect repo to Vercel
- [ ] Set `NEXT_PUBLIC_SOCKET_URL` environment variable
- [ ] Deploy and verify

#### Backend (VPS/Railway/Render)
- [ ] Choose hosting provider
- [ ] Deploy backend
- [ ] Note the backend URL
- [ ] Open firewall port 5000 (if using VPS)
- [ ] Test `/api/accounts` endpoint

#### MT5 EA (Home PC)
- [ ] Install DashboardConnector.mq5 in MT5
- [ ] Set `DashboardURL` to backend URL
- [ ] Enable WebRequests in MT5
- [ ] Attach EA to chart
- [ ] Verify data is being received

---

## Post-Deployment Verification

### Test Backend
```bash
curl https://your-backend-url.com/api/accounts
```

### Test WebSocket
Use [websocketking.com](https://websocketking.com) or similar tool to connect to:
```
wss://your-backend-url.com/socket.io/?EIO=4&transport=websocket
```

### Test Full Flow
1. Open dashboard in browser
2. Check browser console for Socket.io connection
3. Verify account data appears
4. Check that 24h profit and hourly rate calculate correctly

---

## Troubleshooting

### "Connection refused" errors
- Check firewall settings on VPS
- Verify backend is running: `pm2 status` or `ps aux | grep python`
- Check port is correct in environment variables

### CORS errors
- Backend CORS is configured to allow all origins
- If issues persist, check `backend/server.py` CORS settings

### No data appearing
- Check MT5 EA is sending data (enable LogDebug)
- Verify backend receives POST requests
- Check browser network tab for WebSocket messages

### WebSocket disconnects
- Use VPS instead of free tiers for production
- Check if backend is configured for long-running connections
- Verify no proxy timeouts in Nginx

---

## Next Steps After Deployment

1. **Set up monitoring** - Use UptimeRobot or similar to monitor backend
2. **Configure backups** - Backup SQLite database regularly
3. **Add authentication** - Implement API keys for production
4. **Scale if needed** - Add load balancer for multiple backend instances
5. **Mobile app** - Consider React Native app using same backend