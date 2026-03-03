'use client';

import { useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { useDashboardStore } from '@/store/dashboardStore';

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:5000';

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);
  const {
    setAccounts,
    setLeaderboard,
    setSummary,
    setHeatmap,
    setConnected,
    setLastUpdate,
    setLoading,
    setError,
  } = useDashboardStore();

  const connect = useCallback(() => {
    if (socketRef.current?.connected) return;

    console.log('[Socket] Connecting to:', SOCKET_URL);
    
    const socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socket.on('connect', () => {
      console.log('[Socket] Connected:', socket.id);
      setConnected(true);
      setError(null);
    });

    socket.on('disconnect', (reason) => {
      console.log('[Socket] Disconnected:', reason);
      setConnected(false);
    });

    socket.on('connect_error', (error) => {
      console.error('[Socket] Connection error:', error);
      setConnected(false);
      setError('Failed to connect to server');
    });

    // Initial data load
    socket.on('initial_data', (data) => {
      console.log('[Socket] Received initial data');
      setAccounts(data.accounts || []);
      setLeaderboard(data.leaderboard || []);
      setSummary(data.summary);
      setHeatmap(data.heatmap || []);
      setLastUpdate(data.timestamp);
      setLoading(false);
    });

    // Real-time updates
    socket.on('dashboard_update', (data) => {
      console.log('[Socket] Received update');
      setAccounts(data.accounts || []);
      setLeaderboard(data.leaderboard || []);
      setSummary(data.summary);
      setHeatmap(data.heatmap || []);
      setLastUpdate(data.timestamp);
    });

    // Leaderboard updates
    socket.on('leaderboard_update', (data) => {
      console.log('[Socket] Received leaderboard update');
      setLeaderboard(data.leaderboard || []);
    });

    // Error handling
    socket.on('error', (error) => {
      console.error('[Socket] Server error:', error);
      setError(error.message || 'Server error');
    });

    socketRef.current = socket;
  }, [setAccounts, setLeaderboard, setSummary, setHeatmap, setConnected, setLastUpdate, setLoading, setError]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
      setConnected(false);
    }
  }, [setConnected]);

  const requestUpdate = useCallback(() => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('request_update', {});
    }
  }, []);

  const requestLeaderboard = useCallback((sortBy: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('request_leaderboard', { sort_by: sortBy });
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    socket: socketRef.current,
    connect,
    disconnect,
    requestUpdate,
    requestLeaderboard,
  };
}