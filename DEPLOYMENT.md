# Deployment Guide for Vercel

## Frontend Deployment (Vercel)

### 1. Prepare Your Frontend

The frontend is already configured for static export in `next.config.js`:

```javascript
output: 'export',
distDir: 'dist',
```

### 2. Deploy to Vercel

#### Option A: Vercel CLI

```bash
cd frontend
npm install -g vercel
vercel login
vercel
```

#### Option B: GitHub Integration (Recommended)

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "Add New Project"
4. Import your GitHub repository
5. Set root directory to `frontend`
6. Deploy!

### 3. Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables:

```
NEXT_PUBLIC_SOCKET_URL=wss://your-vps-server.com
```

Replace `your-vps-server.com` with your actual VPS/server URL.

### 4. Important Configuration

The `vercel.json` file handles:
- CORS headers for Socket.io
- Static export configuration
- Build commands

## Backend Deployment

Your Python backend needs to run on a VPS/server:

```bash
# On your VPS
cd backend
pip install -r requirements.txt
python server.py
```

Make sure port 5000 is open and accessible.

## Connecting Frontend to Backend

1. Update `NEXT_PUBLIC_SOCKET_URL` in Vercel with your backend URL
2. Ensure your backend server has CORS enabled (already configured in server.py)
3. Use WebSocket Secure (wss://) for production

## Architecture After Deployment

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   Vercel        │◄──────────────────►│  VPS/Railway    │
│   (Next.js)     │                    │  (Python)       │
│   Static Export │                    │  Socket.io      │
└─────────────────┘                    └─────────────────┘
                                              │
                                              ▼
                                       ┌─────────────────┐
                                       │   SQLite        │
                                       │   (on VPS)      │
                                       └─────────────────┘
```

## Quick Deploy Steps

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy Frontend:**
   - Go to vercel.com
   - Import your repo
   - Root directory: `frontend`
   - Add env var: `NEXT_PUBLIC_SOCKET_URL`
   - Deploy

3. **Deploy Backend:**
   - SSH into your VPS
   - Clone the repo
   - Run `python backend/server.py`

4. **Update DNS:**
   - Point your domain to Vercel
   - Configure backend CORS with your domain

## Troubleshooting

### Socket Connection Issues

1. Check CORS configuration on backend
2. Verify WebSocket URL is correct in environment variables
3. Ensure backend server is running and accessible

### Build Failures

1. Check that all dependencies are in `package.json`
2. Verify TypeScript types are correct
3. Run `npm run build` locally first to catch errors