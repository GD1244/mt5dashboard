# Quick Deploy Instructions

## ⚠️ Important: Two Separate Deployments Required

**Vercel only hosts the frontend.** The Python backend must be deployed separately.

---

## Step 1: Deploy Backend (Do This FIRST)

### Option A: Railway (Easiest - 2 minutes)

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub"
4. Select your repo with this code
5. Railway auto-detects `railway.toml`
6. Copy the deployed URL (e.g., `https://mt5-dashboard.up.railway.app`)

### Option B: Render

1. Go to https://render.com
2. Create Web Service
3. Connect your GitHub repo
4. Settings:
   - Build: `pip install -r backend/requirements.txt`
   - Start: `cd backend && python server.py`
   - Env var: `PORT=5000`
5. Deploy and copy the URL

---

## Step 2: Update Frontend Environment

Edit `frontend/.env.production`:

```bash
NEXT_PUBLIC_SOCKET_URL=https://your-backend-url-from-step-1.com
NEXT_PUBLIC_API_URL=https://your-backend-url-from-step-1.com
```

---

## Step 3: Deploy Frontend to Vercel

```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

Or use Git:
1. Push code to GitHub
2. Go to https://vercel.com
3. Import your repo
4. Set environment variables in dashboard
5. Deploy

---

## Step 4: Configure MT5 EA

Once both are deployed:

1. Install `mt5_ea/DashboardConnector.mq5` in MetaTrader 5
2. Set `DashboardURL` to your **backend** URL from Step 1
3. Enable WebRequests in MT5 Options
4. Attach EA to chart

---

## Your Final URLs

| Component | URL Example |
|-----------|-------------|
| Dashboard | `https://mt5-dashboard.vercel.app` |
| Backend API | `https://mt5-backend.railway.app` |
| Socket.io | `wss://mt5-backend.railway.app` |

---

## Test Everything

1. Open dashboard URL in browser
2. Check browser console for Socket.io connection
3. Check EA logs in MT5 (enable LogDebug)
4. Verify account data appears on dashboard

---

## Common Issues

### "Cannot connect to backend"
- Backend must be deployed FIRST
- Check CORS is configured (already done in code)
- Verify WebSocket URL uses `wss://` for HTTPS backends

### "No data showing"
- MT5 EA must be attached and running
- Backend URL in EA settings must match exactly
- Check MT5 → Tools → Options → Expert Advisors → WebRequest

### "Dashboard loads but no real-time updates"
- WebSocket connection failed
- Check browser console for errors
- Some free tiers (Render) spin down - use Railway or VPS