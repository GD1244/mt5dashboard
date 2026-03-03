# MT5 Multi-Account Dashboard

A real-time MetaTrader 5 performance analytics dashboard with competitive leaderboard functionality.

## Features

- **Real-time Updates**: WebSocket-powered live data streaming
- **40+ Account Support**: Handle large account farms efficiently
- **Performance Analytics**:
  - 24-hour profit tracking
  - Hourly rate calculations
  - Floating PnL monitoring
- **Leaderboard Mode**: Rank accounts by performance with gold/silver/bronze badges
- **Heatmap Visualization**: Color-coded accounts based on performance
- **Dual View Modes**: Grid view for cards, Table view for compact data
- **JetBrains Mono Font**: Monospace figures for perfect financial alignment

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS, Zustand
- **Backend**: Python, Socket.io, aiohttp, SQLite
- **Real-time**: Socket.io for bidirectional communication

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python server.py
```

The server will start on `http://localhost:5000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Generate Test Data

To simulate 40+ accounts with realistic performance data:

```bash
cd backend
python collector.py --generate-only
```

## Architecture

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   Next.js       │◄──────────────────►│  Python Server  │
│   Dashboard     │                    │  (Socket.io)    │
│                 │                    │                 │
│  - Zustand      │                    │  - SQLite DB    │
│  - Tailwind     │                    │  - Metrics      │
│  - Real-time UI │                    │  - REST API     │
└─────────────────┘                    └─────────────────┘
                                              │
                                              ▼
                                       ┌─────────────────┐
                                       │   SQLite DB     │
                                       │  (Snapshots)    │
                                       └─────────────────┘
```

## API Endpoints

- `GET /api/accounts` - List all accounts
- `GET /api/leaderboard?sort_by=profit_24h` - Get leaderboard
- `GET /api/summary` - Dashboard summary statistics
- `GET /api/account/:id` - Account details with history
- `WS /socket.io/` - Real-time updates

## Environment Variables

Create `.env.local` in the frontend directory:

```
NEXT_PUBLIC_SOCKET_URL=http://localhost:5000
```

## License

MIT