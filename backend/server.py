#!/usr/bin/env python3
"""
Socket.io Server for MetaTrader 5 Dashboard.
Handles real-time data streaming and client connections.
"""

import asyncio
import json
import socketio
from aiohttp import web
from datetime import datetime
from typing import Dict, Any, List
import threading
import time

from database import db, AccountSnapshot
from metrics_engine import metrics_engine, MetricsEngine


# Create Socket.io server with CORS enabled
sio = socketio.AsyncServer(
    async_mode='aiohttp',
    cors_allowed_origins='*',
    ping_timeout=60,
    ping_interval=25
)

# Create aiohttp application
app = web.Application()
sio.attach(app)

# Connected clients tracking
connected_clients: Dict[str, Dict[str, Any]] = {}

# Background task for periodic updates
background_task = None


class DataCollector:
    """Handles data collection and broadcasting."""
    
    def __init__(self):
        self.metrics_engine = metrics_engine
        self.last_broadcast = None
        self.collection_interval = 3600  # 1 hour in seconds
        self.broadcast_interval = 5      # 5 seconds for real-time updates
    
    async def collect_and_broadcast(self):
        """Main loop for collecting and broadcasting data."""
        while True:
            try:
                # Get latest metrics for all accounts
                metrics = self.metrics_engine.calculate_all_metrics()
                
                # Generate leaderboard
                leaderboard = self.metrics_engine.generate_leaderboard('profit_24h')
                
                # Get dashboard summary
                summary = self.metrics_engine.get_dashboard_summary()
                
                # Get heatmap data
                heatmap = self.metrics_engine.calculate_heatmap_data()
                
                # Prepare payload
                payload = {
                    'timestamp': datetime.now().isoformat(),
                    'accounts': [m.to_dict() for m in metrics],
                    'leaderboard': [e.to_dict() for e in leaderboard],
                    'summary': summary,
                    'heatmap': heatmap
                }
                
                # Broadcast to all connected clients
                await sio.emit('dashboard_update', payload)
                self.last_broadcast = datetime.now()
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Broadcasted update to {len(connected_clients)} clients")
                
            except Exception as e:
                print(f"[Error] Broadcasting failed: {e}")
            
            await asyncio.sleep(self.broadcast_interval)
    
    async def save_hourly_snapshot(self, accounts_data: List[Dict[str, Any]]):
        """Save hourly snapshot to database."""
        try:
            snapshots = db.save_snapshots_batch(accounts_data)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Saved {len(snapshots)} hourly snapshots")
            return snapshots
        except Exception as e:
            print(f"[Error] Failed to save snapshots: {e}")
            return []


data_collector = DataCollector()


# Socket.io Event Handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    connected_clients[sid] = {
        'connected_at': datetime.now(),
        'ip': environ.get('REMOTE_ADDR', 'unknown')
    }
    print(f"[Socket.io] Client connected: {sid} from {connected_clients[sid]['ip']}")
    
    # Send initial data immediately
    await send_initial_data(sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    if sid in connected_clients:
        del connected_clients[sid]
    print(f"[Socket.io] Client disconnected: {sid}")


@sio.event
async def request_update(sid, data):
    """Handle explicit update request from client."""
    print(f"[Socket.io] Update requested by {sid}")
    await send_initial_data(sid)


@sio.event
async def request_leaderboard(sid, data):
    """Handle leaderboard request with sorting."""
    sort_by = data.get('sort_by', 'profit_24h')
    leaderboard = metrics_engine.generate_leaderboard(sort_by)
    
    await sio.emit('leaderboard_update', {
        'sort_by': sort_by,
        'leaderboard': [e.to_dict() for e in leaderboard]
    }, room=sid)


@sio.event
async def submit_account_data(sid, data):
    """Receive account data from VPS collector."""
    try:
        accounts = data.get('accounts', [])
        if not accounts:
            await sio.emit('error', {'message': 'No accounts data provided'}, room=sid)
            return
        
        # Save to database
        snapshots = await data_collector.save_hourly_snapshot(accounts)
        
        # Broadcast update immediately
        await broadcast_update()
        
        await sio.emit('data_received', {
            'status': 'success',
            'accounts_processed': len(snapshots)
        }, room=sid)
        
    except Exception as e:
        print(f"[Error] Processing account data: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)


async def send_initial_data(sid):
    """Send initial dashboard data to a client."""
    try:
        metrics = metrics_engine.calculate_all_metrics()
        leaderboard = metrics_engine.generate_leaderboard('profit_24h')
        summary = metrics_engine.get_dashboard_summary()
        heatmap = metrics_engine.calculate_heatmap_data()
        
        await sio.emit('initial_data', {
            'timestamp': datetime.now().isoformat(),
            'accounts': [m.to_dict() for m in metrics],
            'leaderboard': [e.to_dict() for e in leaderboard],
            'summary': summary,
            'heatmap': heatmap
        }, room=sid)
        
    except Exception as e:
        print(f"[Error] Sending initial data: {e}")
        await sio.emit('error', {'message': 'Failed to load initial data'}, room=sid)


async def broadcast_update():
    """Manually trigger a broadcast update."""
    try:
        metrics = metrics_engine.calculate_all_metrics()
        leaderboard = metrics_engine.generate_leaderboard('profit_24h')
        summary = metrics_engine.get_dashboard_summary()
        heatmap = metrics_engine.calculate_heatmap_data()
        
        await sio.emit('dashboard_update', {
            'timestamp': datetime.now().isoformat(),
            'accounts': [m.to_dict() for m in metrics],
            'leaderboard': [e.to_dict() for e in leaderboard],
            'summary': summary,
            'heatmap': heatmap
        })
    except Exception as e:
        print(f"[Error] Manual broadcast failed: {e}")


# HTTP Routes
async def index(request):
    """Health check endpoint."""
    return web.json_response({
        'status': 'running',
        'service': 'MT5 Dashboard Server',
        'connected_clients': len(connected_clients),
        'timestamp': datetime.now().isoformat()
    })


async def api_accounts(request):
    """REST API endpoint for accounts."""
    try:
        accounts = db.get_all_accounts()
        return web.json_response({
            'accounts': accounts,
            'count': len(accounts)
        })
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def api_leaderboard(request):
    """REST API endpoint for leaderboard."""
    try:
        sort_by = request.query.get('sort_by', 'profit_24h')
        leaderboard = metrics_engine.generate_leaderboard(sort_by)
        
        return web.json_response({
            'leaderboard': [e.to_dict() for e in leaderboard],
            'sort_by': sort_by,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def api_summary(request):
    """REST API endpoint for dashboard summary."""
    try:
        summary = metrics_engine.get_dashboard_summary()
        return web.json_response(summary)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


async def api_account_detail(request):
    """REST API endpoint for account details."""
    try:
        account_id = request.match_info.get('account_id')
        hours = int(request.query.get('hours', 24))
        
        history = metrics_engine.get_account_history(account_id, hours)
        metrics = metrics_engine.calculate_account_metrics(account_id)
        
        return web.json_response({
            'account_id': account_id,
            'current_metrics': metrics.to_dict() if metrics else None,
            'history': history
        })
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)


# Setup routes
app.router.add_get('/', index)
app.router.add_get('/api/accounts', api_accounts)
app.router.add_get('/api/leaderboard', api_leaderboard)
app.router.add_get('/api/summary', api_summary)
app.router.add_get('/api/account/{account_id}', api_account_detail)


async def start_background_tasks(app):
    """Start background tasks on app startup."""
    global background_task
    background_task = asyncio.create_task(data_collector.collect_and_broadcast())
    print("[Server] Background tasks started")


async def cleanup_background_tasks(app):
    """Cleanup background tasks on app shutdown."""
    global background_task
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
    print("[Server] Background tasks stopped")


app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)


if __name__ == '__main__':
    print("=" * 60)
    print("MT5 Multi-Account Dashboard Server")
    print("=" * 60)
    print("\nStarting server on http://localhost:5000")
    print("Socket.io endpoint: ws://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    web.run_app(app, host='0.0.0.0', port=5000)