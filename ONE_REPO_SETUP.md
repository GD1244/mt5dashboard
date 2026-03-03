# Single Repo Deployment Setup

This guide shows how to deploy both frontend and backend from ONE GitHub repository.

## Repository Structure

```
mt5-dashboard/           ← Your GitHub repo root
├── backend/             ← Railway deploys from here
│   ├── server.py
│   ├── requirements.txt
│   └── database.py
├── frontend/            ← Vercel deploys from here
│   ├── app/
│   ├── package.json
│   └── next.config.js
├── mt5_ea/              ← MT5 Expert Advisor
│   └── DashboardConnector.mq5
├── railway.toml         ← Railway config (root level)
└── DEPLOY_NOW.md        ← This guide
```

## Deployment Steps

### 1. Push to GitHub

```bash
# From your project root
git init
git add .
git commit -m "Initial MT5 Dashboard"
git remote add origin https://github.com/YOUR_USERNAME/mt5-dashboard.git
git push -u origin main
```

### 2. Deploy Backend to Railway

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select `mt5-dashboard`
5. Click **"Add Variables"**:
   - Add `RAILWAY_DOCKERFILE_PATH=backend/Dockerfile` (if using Docker)
   - Or Railway will auto-detect from `railway.toml`
6. **Important**: Set **Root Directory** = `backend`
   - Go to Settings → Root Directory → Enter `backend`
7. Deploy!
8. Copy the deployed URL (e.g., `https://mt5-dashboard.up.railway.app`)

### 3. Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Import GitHub repo `mt5-dashboard`
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - Build Command: `next build` (auto-detected)
   - Output Directory: `dist` (auto-detected)
4. Add Environment Variables:
   ```
   NEXT_PUBLIC_SOCKET_URL=https://your-railway-url.up.railway.app
   NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
   ```
5. Deploy!

### 4. Update Environment Variables

After both deploy:

1. In Vercel dashboard → Project Settings → Environment Variables
2. Update `NEXT_PUBLIC_SOCKET_URL` with your Railway URL
3. Redeploy frontend (Vercel → Deployments → Redeploy)

## Verifying Deployment

### Test Backend
```bash
curl https://your-railway-url.up.railway.app/api/accounts
```

### Test Frontend
Open `https://your-vercel-url.vercel.app` in browser

## Updating Code

When you push new code to GitHub:

```bash
git add .
git commit -m "Updated dashboard"
git push
```

Both Railway and Vercel will **auto-deploy** the changes!

## Troubleshooting

### Railway says "No Dockerfile found"
- Make sure Root Directory is set to `backend`
- Or use `railway.toml` config (already provided)

### Vercel builds but shows 404
- Check Root Directory is set to `frontend`
- Verify `next.config.js` has `output: 'export'`

### Environment variables not working
- Vercel requires `NEXT_PUBLIC_` prefix for client-side vars
- Redeploy after changing environment variables