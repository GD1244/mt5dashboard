# Deploy to Fly.io (Free Tier Available)

Fly.io offers a free tier that includes:
- 3 shared-cpu-1x VMs (always running)
- 3GB persistent volumes
- No sleep/idle timeout

Perfect for a WebSocket backend!

## Setup

### 1. Install Fly CLI
```bash
# macOS
brew install flyctl

# Or download from https://fly.io/docs/hands-on/install-flyctl/
```

### 2. Sign Up / Login
```bash
fly auth signup  # If new user
fly auth login   # If existing user
```

### 3. Create Fly App
```bash
# From project root
cd backend

# Create app
fly apps create mt5-dashboard-backend

# Create volume for SQLite database
fly volumes create mt5_data --size 1 --region yyz
```

### 4. Deploy
```bash
fly deploy
```

## Configuration

Create `backend/fly.toml`:

```toml
app = "mt5-dashboard-backend"
primary_region = "yyz"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[[mounts]]
  source = "mt5_data"
  destination = "/data"
```

Update `backend/database.py` to use `/data/mt5_dashboard.db` for persistence.

## Get Your URL

After deploy, run:
```bash
fly status
```

Your app will be at: `https://mt5-dashboard-backend.fly.dev`

## Free Tier Limits
- 2340 hours/month of VM time (enough for 1 always-running VM)
- Perfect for this dashboard!

## Connect Frontend

Update `frontend/.env.production`:
```
NEXT_PUBLIC_SOCKET_URL=https://mt5-dashboard-backend.fly.dev
NEXT_PUBLIC_API_URL=https://mt5-dashboard-backend.fly.dev
```

Deploy to Vercel and you're done!