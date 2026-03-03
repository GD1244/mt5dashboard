# Simple Free Deployment Options

## Option 1: Render (Easiest - No Volume Needed)

**Best for:** Simple setup, no command line needed

1. Go to https://render.com
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repo `GD1244/mt5dashboard`
5. Use these settings:
   - **Name**: mt5-dashboard-backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python server.py`
   - **Plan**: Free
6. Add Environment Variable:
   - Key: `PORT`
   - Value: `5000`
7. Click **Create Web Service**

**Note:** Free tier spins down after 15 min idle. First request will wake it up (takes ~30 seconds).

---

## Option 2: Self-Host + Ngrok (Always Works)

**Best for:** Full control, always running while your PC is on

### Step 1: Install ngrok
```bash
brew install ngrok
ngrok config add-authtoken YOUR_TOKEN  # Get token from https://dashboard.ngrok.com
```

### Step 2: Start Backend
```bash
cd /Users/grayfx/Desktop/farmcal/backend
python server.py
```

### Step 3: Expose to Internet (new terminal)
```bash
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Step 4: Update Frontend
Edit `frontend/.env.production`:
```
NEXT_PUBLIC_SOCKET_URL=https://abc123.ngrok.io
NEXT_PUBLIC_API_URL=https://abc123.ngrok.io
```

Deploy to Vercel.

**Note:** URL changes every time you restart ngrok (unless you pay). Good for testing!

---

## Option 3: PythonAnywhere (Always-On Free Tier)

**Best for:** True 24/7 free hosting

1. Go to https://pythonanywhere.com
2. Sign up for free account
3. Open **Bash console**
4. Clone repo:
```bash
git clone https://github.com/GD1244/mt5dashboard.git
cd mt5dashboard/backend
pip install -r requirements.txt
```

5. Go to **Web** tab → Add new web app
6. Select **Manual configuration** → Python 3.11
7. Set working directory: `/home/YOURNAME/mt5dashboard/backend`
8. Set WSGI file (edit it):
```python
import sys
path = '/home/YOURNAME/mt5dashboard/backend'
if path not in sys.path:
    sys.path.append(path)

from server import app as application
```

9. Reload web app

**Note:** WebSocket might not work on PythonAnywhere free tier. Use polling instead.

---

## My Recommendation

**Start with Render** - easiest setup, and if the 15-min sleep is annoying, upgrade to:

**Self-host + ngrok** for testing, then **VPS** ($5/month) for production.

For a real-time trading dashboard, eventually you'll want a VPS that stays online 24/7.