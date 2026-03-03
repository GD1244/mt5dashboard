# Deploy to Koyeb (Free Forever Tier)

Koyeb offers a truly free tier with:
- 1 always-on web service (NEVER sleeps)
- 2GB RAM, 1 vCPU
- WebSocket support
- Custom domains
- No credit card required

## Step 1: Sign Up
1. Go to https://www.koyeb.com
2. Sign up with GitHub
3. No credit card needed

## Step 2: Create App
1. Click **"Create App"**
2. Choose **"GitHub"** as source
3. Select repository: `GD1244/mt5dashboard`
4. Branch: `main`

## Step 3: Configure Service
- **Service Name**: mt5-dashboard-backend
- **Region**: Choose closest to you
- **Instance Type**: Free (1 vCPU, 2GB RAM)

## Step 4: Build Settings
- **Builder**: Dockerfile
- **Dockerfile Path**: `./Dockerfile`

## Step 5: Environment Variables
Add:
```
PORT=8080
```

## Step 6: Expose Port
- **Port**: 8080
- **Protocol**: HTTP

## Step 7: Deploy
Click **"Deploy"**

Your app will be live at:
```
https://mt5-dashboard-backend-YOURNAME.koyeb.app
```

## Update Frontend

Edit `frontend/.env.production`:
```
NEXT_PUBLIC_SOCKET_URL=https://mt5-dashboard-backend-YOURNAME.koyeb.app
NEXT_PUBLIC_API_URL=https://mt5-dashboard-backend-YOURNAME.koyeb.app
```

Deploy to Vercel and you're done!

## Why Koyeb?

✅ **Always on** - No sleep/idle timeout  
✅ **Truly free** - No credit card required  
✅ **WebSocket support** - Perfect for real-time dashboard  
✅ **Easy deploy** - Just connect GitHub  
✅ **Custom domains** - Use your own domain for free

## Alternative: VPS (Most Reliable)

For production trading, consider a $5/month VPS:
- DigitalOcean Droplet
- Linode Nanode
- Vultr Cloud Compute

See VPS_DEPLOYMENT.md for setup instructions.