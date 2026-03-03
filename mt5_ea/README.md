# MT5 Expert Advisor - Dashboard Connector

This MQL5 Expert Advisor (EA) runs inside MetaTrader 5 and sends account data directly to your dashboard backend.

## Why Use an EA?

- **No Python required** on the VPS
- **Runs inside MT5** - always has access to account data
- **Real-time updates** - sends data immediately on trade events
- **Multiple accounts** - attach to each MT5 terminal
- **Reliable** - restart MT5 and EA auto-starts

## Installation

### 1. Copy Files to MT5

1. Open MetaTrader 5
2. Go to **File → Open Data Folder**
3. Navigate to `MQL5/Experts/`
4. Create a folder named `DashboardConnector`
5. Copy `DashboardConnector.mq5` into this folder

### 2. Compile the EA

1. In MT5, press **F4** to open MetaEditor
2. Navigate to `Experts/DashboardConnector/DashboardConnector.mq5`
3. Press **F7** to compile
4. Check the "Errors" tab - should show 0 errors

### 3. Attach to Chart

1. Back in MT5, open a chart (any symbol)
2. In Navigator panel, find `DashboardConnector`
3. Drag it onto the chart
4. Configure settings:
   - **DashboardURL**: Your backend URL (e.g., `http://localhost:5000`)
   - **UpdateInterval**: How often to send data (default 60 seconds)
   - **AccountNickname**: Optional friendly name
   - **LogDebug**: Enable for troubleshooting
5. Click **OK**

### 4. Allow WebRequests

1. Go to **Tools → Options → Expert Advisors**
2. Check **Allow WebRequest for listed URL:**
3. Add your dashboard URL (e.g., `http://localhost:5000`)
4. Click **OK**

## Running on Multiple Accounts

Repeat the above steps for each MT5 terminal:

1. Open each MT5 instance
2. Attach the EA to a chart
3. Each EA will report its account to the dashboard

## Auto-Start with MT5

To make the EA start automatically when MT5 opens:

1. Save the chart with EA attached as a template:
   - Right-click chart → **Template → Save Template**
   - Name it `dashboard.tpl`
2. Set as default template:
   - Right-click chart → **Template → Set as Default**
3. Now when MT5 starts, the EA auto-attaches

## Troubleshooting

### "Error sending data"
- Check DashboardURL is correct
- Verify WebRequest is allowed in Options
- Check backend server is running

### EA not compiling
- Make sure you're using MT5 build 1930 or later
- Check for syntax errors in the code

### No data in dashboard
- Check EA is attached to chart (should see smiley face icon)
- Check `Experts` tab in Terminal for error messages
- Enable LogDebug to see detailed output

## Security

- Only allow WebRequest to your trusted backend URL
- Use firewall to restrict access to backend port
- Consider adding API key authentication for production