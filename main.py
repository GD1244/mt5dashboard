#!/usr/bin/env python3
"""
MetaTrader Farm Calculator Pro
A standalone desktop GUI application for parsing MetaTrader account logs
with Wolf Farm Growth Visualizer - featuring persistent history tracking,
real-time equity curves, and real-world impact metrics.
"""

import re
import json
import os
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Tuple
import customtkinter as ctk
from tkinter import ttk

# Matplotlib imports for the equity curve
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class AccountData:
    """Represents a parsed MetaTrader account."""
    bot_name: str
    account_id: str
    balance: float
    equity: float
    
    @property
    def profit(self) -> float:
        """Calculate profit/loss (Balance - 10000)."""
        return self.balance - 10000.00


@dataclass
class HistoryEntry:
    """Represents a single calculation run."""
    timestamp: str
    total_balance: float
    total_profit: float
    account_count: int
    growth_pct: float = 0.0
    session_id: str = ""


# ============================================================================
# REAL-WORLD IMPACT CALCULATOR
# ============================================================================

class FarmImpactCalculator:
    """Calculates real-world equivalents for profit amounts."""
    
    COSTS = {
        "coffee": 5.00,
        "meal": 15.00,
        "tank_of_gas": 65.00,
        "netflix_month": 15.99,
        "grocery_week": 120.00,
        "dinner_date": 80.00,
        "video_game": 70.00,
        "gym_membership": 50.00,
        "streaming_service": 12.00,
        "phone_bill": 60.00,
        "uber_ride": 25.00,
        "movie_ticket": 15.00,
        "pizza_delivery": 30.00,
        "car_wash": 15.00,
        "spotify_month": 10.99,
    }
    
    @classmethod
    def calculate_impacts(cls, profit_usd: float) -> List[Dict[str, Any]]:
        """Calculate what the profit can buy in real-world terms."""
        if profit_usd <= 0:
            return []
        
        impacts = []
        
        items = [
            ("☕ Premium Coffees", cls.COSTS["coffee"]),
            ("🍕 Pizza Deliveries", cls.COSTS["pizza_delivery"]),
            ("🍽️ Restaurant Meals", cls.COSTS["meal"]),
            ("🎬 Movie Tickets", cls.COSTS["movie_ticket"]),
            ("🎮 Video Games", cls.COSTS["video_game"]),
            ("🎵 Months of Spotify", cls.COSTS["spotify_month"]),
            ("📺 Months of Netflix", cls.COSTS["netflix_month"]),
            ("🏋️ Gym Memberships", cls.COSTS["gym_membership"]),
            ("⛽ Tanks of Gas", cls.COSTS["tank_of_gas"]),
            ("🛒 Weeks of Groceries", cls.COSTS["grocery_week"]),
            ("🌹 Dinner Dates", cls.COSTS["dinner_date"]),
        ]
        
        for name, cost in items:
            quantity = int(profit_usd / cost)
            if quantity >= 1:
                impacts.append({
                    "name": name,
                    "quantity": quantity,
                    "cost": cost
                })
        
        return impacts[:5]


# ============================================================================
# PARSER
# ============================================================================

class MetaTraderParser:
    """Parser for MetaTrader account log data."""
    
    TEN_K_PATTERN = re.compile(r'(1\d{3,4}\.\d{2})')
    DATE_PATTERN = re.compile(r'\d{2}/\d{2}/\d{4}')
    
    def parse(self, raw_text: str) -> List[AccountData]:
        """Parse raw text and extract account data."""
        accounts = []
        blocks = raw_text.split('USC')
        
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
            account = self._parse_block(block)
            if account:
                accounts.append(account)
        
        return accounts
    
    def _parse_block(self, block: str) -> Optional[AccountData]:
        """Parse a single account block."""
        account_id_match = re.search(r'^(\d+)', block)
        if not account_id_match:
            return None
        account_id = account_id_match.group(1)
        
        lines = block.split('\n')
        bot_name = "Unknown"
        for i, line in enumerate(lines):
            if line.strip() == account_id and i + 1 < len(lines):
                bot_name = lines[i + 1].strip()
                break
        
        if bot_name == "Unknown":
            for line in lines[1:]:
                stripped = line.strip()
                if stripped and not stripped.replace('.', '').replace(',', '').isdigit():
                    bot_name = stripped
                    break
        
        data_line = None
        for line in lines:
            if self.DATE_PATTERN.search(line):
                data_line = line
                break
        
        if not data_line:
            return None
        
        ten_k_numbers = self.TEN_K_PATTERN.findall(data_line)
        
        if len(ten_k_numbers) < 2:
            return None
        
        equity = float(ten_k_numbers[-2])
        balance = float(ten_k_numbers[-1])
        
        return AccountData(
            bot_name=bot_name,
            account_id=account_id,
            balance=balance,
            equity=equity
        )
    
    def get_content_hash(self, raw_text: str) -> str:
        """Generate a hash of the content for duplicate detection."""
        # Normalize the text (remove extra whitespace)
        normalized = ' '.join(raw_text.split())
        return hashlib.md5(normalized.encode()).hexdigest()


# ============================================================================
# WOLF FARM HISTORY MANAGER
# ============================================================================

class WolfFarmHistoryManager:
    """
    Advanced history manager with duplicate detection,
    growth tracking, and equity curve data.
    """
    
    HISTORY_FILE = "farm_history.json"
    DUPLICATE_WINDOW_MINUTES = 5
    
    def __init__(self):
        self.history: List[HistoryEntry] = []
        self.content_hashes: Dict[str, datetime] = {}
        self._load()
    
    def _load(self):
        """Load history from JSON file."""
        if os.path.exists(self.HISTORY_FILE):
            try:
                with open(self.HISTORY_FILE, 'r') as f:
                    data = json.load(f)
                    self.history = [
                        HistoryEntry(
                            timestamp=item['timestamp'],
                            total_balance=item['total_balance'],
                            total_profit=item['total_profit'],
                            account_count=item['account_count'],
                            growth_pct=item.get('growth_pct', 0.0),
                            session_id=item.get('session_id', '')
                        )
                        for item in data.get('entries', [])
                    ]
                    self.content_hashes = {
                        k: datetime.fromisoformat(v)
                        for k, v in data.get('content_hashes', {}).items()
                    }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading history: {e}")
                self.history = []
                self.content_hashes = {}
    
    def save(self):
        """Save history to JSON file."""
        data = {
            'entries': [
                {
                    'timestamp': entry.timestamp,
                    'total_balance': entry.total_balance,
                    'total_profit': entry.total_profit,
                    'account_count': entry.account_count,
                    'growth_pct': entry.growth_pct,
                    'session_id': entry.session_id
                }
                for entry in self.history
            ],
            'content_hashes': {
                k: v.isoformat()
                for k, v in self.content_hashes.items()
            }
        }
        with open(self.HISTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def is_duplicate(self, content_hash: str) -> bool:
        """Check if this content was recently processed."""
        if content_hash not in self.content_hashes:
            return False
        
        last_time = self.content_hashes[content_hash]
        time_diff = datetime.now() - last_time
        
        return time_diff < timedelta(minutes=self.DUPLICATE_WINDOW_MINUTES)
    
    def add_entry(self, total_balance: float, total_profit: float, 
                  account_count: int, content_hash: str = "") -> HistoryEntry:
        """Add a new history entry with growth calculation."""
        
        # Calculate growth % from previous entry
        growth_pct = 0.0
        if self.history:
            prev_balance = self.history[-1].total_balance
            if prev_balance > 0:
                growth_pct = ((total_balance - prev_balance) / prev_balance) * 100
        
        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(),
            total_balance=total_balance,
            total_profit=total_profit,
            account_count=account_count,
            growth_pct=growth_pct,
            session_id=content_hash[:8] if content_hash else ""
        )
        
        self.history.append(entry)
        
        # Track content hash
        if content_hash:
            self.content_hashes[content_hash] = datetime.now()
        
        self.save()
        return entry
    
    def get_equity_curve_data(self) -> Tuple[List[datetime], List[float]]:
        """Get data for plotting the equity curve."""
        if not self.history:
            return [], []
        
        dates = [datetime.fromisoformat(e.timestamp) for e in self.history]
        # Convert cents to USD
        balances = [e.total_balance / 100 for e in self.history]
        
        return dates, balances
    
    @property
    def first_run(self) -> Optional[datetime]:
        """Get the timestamp of the first run."""
        if self.history:
            return datetime.fromisoformat(self.history[0].timestamp)
        return None
    
    @property
    def last_entry(self) -> Optional[HistoryEntry]:
        """Get the most recent history entry."""
        if self.history:
            return self.history[-1]
        return None
    
    def calculate_growth_metrics(self, current_balance: float) -> Dict[str, Any]:
        """Calculate growth metrics compared to history."""
        metrics = {
            'overall_growth_pct': 0.0,
            'delta_pct': 0.0,
            'days_active': 0,
            'daily_avg_growth': 0.0
        }
        
        if not self.history:
            return metrics
        
        # Overall growth since first run
        first_balance = self.history[0].total_balance
        if first_balance > 0:
            metrics['overall_growth_pct'] = ((current_balance - first_balance) / first_balance) * 100
        
        # Delta since last run
        if len(self.history) >= 1:
            last_balance = self.history[-1].total_balance
            if last_balance > 0:
                metrics['delta_pct'] = ((current_balance - last_balance) / last_balance) * 100
        
        # Days active
        first_run = self.first_run
        if first_run:
            metrics['days_active'] = (datetime.now() - first_run).days
            
            # Daily average growth
            if metrics['days_active'] > 0:
                total_growth = current_balance - first_balance
                metrics['daily_avg_growth'] = total_growth / metrics['days_active']
        
        return metrics


# ============================================================================
# EQUITY CURVE WIDGET
# ============================================================================

class EquityCurveWidget(ctk.CTkFrame):
    """Matplotlib-based equity curve widget."""
    
    def __init__(self, parent, colors: Dict[str, str], **kwargs):
        super().__init__(parent, **kwargs)
        
        self.colors = colors
        
        # Create figure with dark theme
        self.fig = Figure(figsize=(8, 4), dpi=100, facecolor=colors['bg_card'])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(colors['bg_card'])
        
        # Style the plot
        self.ax.tick_params(colors=colors['text_secondary'])
        self.ax.spines['bottom'].set_color(colors['border'])
        self.ax.spines['top'].set_color(colors['border'])
        self.ax.spines['left'].set_color(colors['border'])
        self.ax.spines['right'].set_color(colors['border'])
        self.ax.xaxis.label.set_color(colors['text_secondary'])
        self.ax.yaxis.label.set_color(colors['text_secondary'])
        self.ax.title.set_color(colors['accent_gold'])
        
        # Grid
        self.ax.grid(True, alpha=0.3, color=colors['border'])
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update_curve(self, dates: List[datetime], balances: List[float]):
        """Update the equity curve with new data."""
        self.ax.clear()
        
        # Re-apply styling
        self.ax.set_facecolor(self.colors['bg_card'])
        self.ax.tick_params(colors=self.colors['text_secondary'])
        for spine in self.ax.spines.values():
            spine.set_color(self.colors['border'])
        self.ax.grid(True, alpha=0.3, color=self.colors['border'])
        
        if not dates or not balances:
            self.ax.text(0.5, 0.5, 'No data available\nRun calculation to see equity curve',
                        ha='center', va='center', transform=self.ax.transAxes,
                        color=self.colors['text_secondary'], fontsize=12)
            self.canvas.draw()
            return
        
        # Plot the equity curve
        self.ax.plot(dates, balances, color=self.colors['accent_emerald'], 
                    linewidth=2, marker='o', markersize=4, 
                    markerfacecolor=self.colors['accent_gold'],
                    markeredgecolor=self.colors['accent_gold'])
        
        # Fill area under curve
        self.ax.fill_between(dates, balances, alpha=0.2, color=self.colors['accent_emerald'])
        
        # Formatting
        self.ax.set_title('Wolf Farm Equity Curve', fontsize=14, fontweight='bold', 
                         color=self.colors['accent_gold'], pad=15)
        self.ax.set_xlabel('Date', fontsize=10, color=self.colors['text_secondary'])
        self.ax.set_ylabel('Balance (USD)', fontsize=10, color=self.colors['text_secondary'])
        
        # Format x-axis dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//5)))
        self.fig.autofmt_xdate()
        
        # Add balance labels on points
        for date, balance in zip(dates, balances):
            self.ax.annotate(f'${balance:,.0f}', 
                           xy=(date, balance),
                           xytext=(0, 10), textcoords='offset points',
                           ha='center', fontsize=8,
                           color=self.colors['text_secondary'])
        
        self.fig.tight_layout()
        self.canvas.draw()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class FarmCalculatorApp(ctk.CTk):
    """Main application window for the Farm Calculator Pro."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("MetaTrader Farm Calculator Pro - Wolf Farm Edition")
        self.geometry("1600x1000")
        self.minsize(1400, 900)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Custom color scheme
        self.colors = {
            "bg_dark": "#0d1117",
            "bg_card": "#161b22",
            "bg_input": "#0d1117",
            "border": "#30363d",
            "text_primary": "#e6edf3",
            "text_secondary": "#8b949e",
            "accent_emerald": "#10b981",
            "accent_gold": "#fbbf24",
            "accent_gold_hover": "#f59e0b",
            "profit_green": "#34d399",
            "loss_red": "#f87171",
            "accent_blue": "#60a5fa",
            "accent_purple": "#a78bfa",
            "warning": "#fbbf24",
        }
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Main content
        self.grid_rowconfigure(2, weight=0)  # Footer
        
        # Parser and History instances
        self.parser = MetaTraderParser()
        self.history = WolfFarmHistoryManager()
        
        # Display mode (cents or standard)
        self.display_in_cents = ctk.BooleanVar(value=False)
        
        # Store parsed accounts
        self.accounts: List[AccountData] = []
        
        # Current metrics
        self.current_total_balance = 0.0
        self.current_total_profit = 0.0
        
        # Build UI
        self._create_header()
        self._create_main_content()
        self._create_footer()
        
        # Load initial summary from history if available
        if self.history.last_entry:
            self._load_last_history()
    
    def _scale_amount(self, amount_cents: float) -> float:
        """Convert cent amount to standard currency."""
        if self.display_in_cents.get():
            return amount_cents
        return amount_cents / 100.0
    
    def _format_currency(self, amount: float) -> str:
        """Format amount as currency string."""
        scaled = self._scale_amount(amount)
        return f"${scaled:,.2f}"
    
    def _create_header(self):
        """Create the header section with title and summary."""
        header = ctk.CTkFrame(self, fg_color=self.colors["bg_card"], corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(1, weight=1)
        
        # Left side - Title and Farm Age
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=30, pady=20, sticky="w")
        
        # Title
        title = ctk.CTkLabel(
            left_frame,
            text="🐺 Wolf Farm Calculator Pro",
            font=ctk.CTkFont(family="SF Pro Display", size=24, weight="bold"),
            text_color=self.colors["accent_gold"]
        )
        title.pack(anchor="w")
        
        # Farm Age
        self.farm_age_label = ctk.CTkLabel(
            left_frame,
            text=self._get_farm_age_text(),
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=self.colors["text_secondary"]
        )
        self.farm_age_label.pack(anchor="w", pady=(5, 0))
        
        # Right side - Summary Stats
        summary_frame = ctk.CTkFrame(header, fg_color="transparent")
        summary_frame.grid(row=0, column=1, padx=30, pady=10, sticky="e")
        
        # Total Profit Card
        self.total_profit_label = ctk.CTkLabel(
            summary_frame,
            text="Total Farm Profit: $0.00",
            font=ctk.CTkFont(family="SF Mono", size=16, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        self.total_profit_label.pack(side="left", padx=20)
        
        # Account Count Card
        self.account_count_label = ctk.CTkLabel(
            summary_frame,
            text="Accounts: 0",
            font=ctk.CTkFont(family="SF Mono", size=16, weight="bold"),
            text_color=self.colors["accent_gold"]
        )
        self.account_count_label.pack(side="left", padx=20)
        
        # Delta % Card
        self.delta_label = ctk.CTkLabel(
            summary_frame,
            text="Δ 0.00%",
            font=ctk.CTkFont(family="SF Mono", size=16, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        self.delta_label.pack(side="left", padx=20)
    
    def _get_farm_age_text(self) -> str:
        """Get the farm age display text."""
        first_run = self.history.first_run
        if first_run:
            days = (datetime.now() - first_run).days
            return f"⏱️ Farm Active: {days} days since {first_run.strftime('%Y-%m-%d')}"
        return "⏱️ Farm Active: First run pending..."
    
    def _create_main_content(self):
        """Create the main content area with tabbed interface."""
        # Create tab view
        self.tab_view = ctk.CTkTabview(
            self,
            fg_color=self.colors["bg_dark"],
            segmented_button_fg_color=self.colors["bg_card"],
            segmented_button_selected_color=self.colors["accent_gold"],
            segmented_button_selected_hover_color=self.colors["accent_gold_hover"],
            segmented_button_unselected_color=self.colors["bg_card"],
            segmented_button_unselected_hover_color=self.colors["border"],
            text_color=self.colors["text_primary"],
        )
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Add tabs
        self.tab_view.add("📊 Dashboard")
        self.tab_view.add("📈 Growth Trends")
        self.tab_view.add("📜 History")
        
        # Create Dashboard Tab
        self._create_dashboard_tab()
        
        # Create Growth Trends Tab
        self._create_growth_trends_tab()
        
        # Create History Tab
        self._create_history_tab()
    
    def _create_dashboard_tab(self):
        """Create the main dashboard tab."""
        tab = self.tab_view.tab("📊 Dashboard")
        tab.grid_columnconfigure((0, 1), weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Left panel - Input and Table
        self._create_left_panel(tab)
        
        # Right panel - Stats and Impact
        self._create_right_panel(tab)
    
    def _create_growth_trends_tab(self):
        """Create the growth trends tab with equity curve."""
        tab = self.tab_view.tab("📈 Growth Trends")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Main container
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(container, fg_color=self.colors["bg_card"], corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="🐺 Wolf Farm Growth Visualizer",
            font=ctk.CTkFont(family="SF Pro Display", size=20, weight="bold"),
            text_color=self.colors["accent_emerald"]
        ).pack(side="left", padx=20, pady=15)
        
        # Refresh button
        ctk.CTkButton(
            header_frame,
            text="🔄 Refresh Chart",
            font=ctk.CTkFont(family="SF Pro Display", size=12),
            fg_color=self.colors["accent_gold"],
            hover_color=self.colors["accent_gold_hover"],
            text_color="#000000",
            command=self._refresh_equity_curve
        ).pack(side="right", padx=20, pady=15)
        
        # Equity Curve Widget
        self.equity_widget = EquityCurveWidget(
            container,
            self.colors,
            fg_color=self.colors["bg_card"],
            corner_radius=12
        )
        self.equity_widget.grid(row=1, column=0, sticky="nsew")
        
        # Initial chart update
        self._refresh_equity_curve()
    
    def _create_history_tab(self):
        """Create the history tab with past runs."""
        tab = self.tab_view.tab("📜 History")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Container
        container = ctk.CTkFrame(tab, fg_color=self.colors["bg_card"], corner_radius=12)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # Header
        ctk.CTkLabel(
            container,
            text="📜 Calculation History",
            font=ctk.CTkFont(family="SF Pro Display", size=18, weight="bold"),
            text_color=self.colors["accent_gold"]
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # History Treeview
        table_frame = ctk.CTkFrame(container, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        style = ttk.Style()
        style.configure(
            "History.Treeview",
            background=self.colors["bg_input"],
            foreground=self.colors["text_primary"],
            fieldbackground=self.colors["bg_input"],
            rowheight=30
        )
        style.configure(
            "History.Treeview.Heading",
            background=self.colors["bg_card"],
            foreground=self.colors["accent_gold"],
            font=("SF Pro Display", 11, "bold"),
            relief="flat"
        )
        
        columns = ("timestamp", "balance", "profit", "growth", "accounts")
        self.history_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="History.Treeview"
        )
        
        self.history_tree.heading("timestamp", text="Timestamp")
        self.history_tree.heading("balance", text="Balance (USD)")
        self.history_tree.heading("profit", text="Profit (USD)")
        self.history_tree.heading("growth", text="Growth %")
        self.history_tree.heading("accounts", text="Accounts")
        
        self.history_tree.column("timestamp", width=180, anchor="w")
        self.history_tree.column("balance", width=120, anchor="e")
        self.history_tree.column("profit", width=120, anchor="e")
        self.history_tree.column("growth", width=100, anchor="e")
        self.history_tree.column("accounts", width=80, anchor="center")
        
        scrollbar = ctk.CTkScrollbar(
            table_frame,
            orientation="vertical",
            command=self.history_tree.yview,
            fg_color=self.colors["bg_input"],
            button_color=self.colors["border"],
            button_hover_color=self.colors["accent_gold"]
        )
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Update history display
        self._update_history_tab()
    
    def _update_history_tab(self):
        """Update the history tab with current data."""
        # Clear existing
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add entries
        for entry in reversed(self.history.history):
            timestamp = datetime.fromisoformat(entry.timestamp).strftime("%Y-%m-%d %H:%M")
            balance_usd = entry.total_balance / 100
            profit_usd = entry.total_profit / 100
            
            tag = "profit" if entry.growth_pct >= 0 else "loss"
            
            self.history_tree.insert(
                "",
                "end",
                values=(
                    timestamp,
                    f"${balance_usd:,.2f}",
                    f"${profit_usd:,.2f}",
                    f"{entry.growth_pct:+.2f}%",
                    entry.account_count
                ),
                tags=(tag,)
            )
        
        self.history_tree.tag_configure("profit", foreground=self.colors["profit_green"])
        self.history_tree.tag_configure("loss", foreground=self.colors["loss_red"])
    
    def _refresh_equity_curve(self):
        """Refresh the equity curve chart."""
        dates, balances = self.history.get_equity_curve_data()
        self.equity_widget.update_curve(dates, balances)
    
    def _create_left_panel(self, parent):
        """Create the left panel with input and table."""
        panel = ctk.CTkFrame(parent, fg_color="transparent")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        
        # Input Section
        self._create_input_section(panel)
        
        # Table Section
        self._create_table_section(panel)
    
    def _create_input_section(self, parent):
        """Create the input text area section."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.colors["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"]
        )
        panel.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        
        # Header with Toggle
        header_frame = ctk.CTkFrame(panel, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        header = ctk.CTkLabel(
            header_frame,
            text="📋 Paste Terminal Data",
            font=ctk.CTkFont(family="SF Pro Display", size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        header.grid(row=0, column=0, sticky="w")
        
        # Cent/Standard Toggle
        toggle_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        toggle_frame.grid(row=0, column=1, sticky="e")
        
        toggle_label = ctk.CTkLabel(
            toggle_frame,
            text="Show in Cents",
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=self.colors["text_secondary"]
        )
        toggle_label.pack(side="left", padx=(0, 10))
        
        self.cent_toggle = ctk.CTkSwitch(
            toggle_frame,
            text="",
            variable=self.display_in_cents,
            onvalue=True,
            offvalue=False,
            command=self._on_toggle_changed,
            progress_color=self.colors["accent_emerald"]
        )
        self.cent_toggle.pack(side="left")
        
        # Text Input
        self.input_text = ctk.CTkTextbox(
            panel,
            fg_color=self.colors["bg_input"],
            text_color=self.colors["text_primary"],
            font=ctk.CTkFont(family="SF Mono", size=12),
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
            wrap="word",
            height=180
        )
        self.input_text.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Placeholder text
        placeholder = """Paste your MetaTrader terminal data here...

Example format:
USC
369214589
10K MT4 #9LIVE
LX-ELITE TRADING
Self TradingMT41:200037.36327.830.0010365.1910327.8328/02/2026
08:16:18 PM"""
        
        self.input_text.insert("1.0", placeholder)
        self.input_text.configure(text_color=self.colors["text_secondary"])
        
        self.input_text.bind("<FocusIn>", self._on_input_focus_in)
        self.input_text.bind("<FocusOut>", self._on_input_focus_out)
        
        # Calculate Button
        self.calc_button = ctk.CTkButton(
            panel,
            text="🚀 Calculate Farm Performance",
            font=ctk.CTkFont(family="SF Pro Display", size=14, weight="bold"),
            fg_color=self.colors["accent_gold"],
            hover_color=self.colors["accent_gold_hover"],
            text_color="#000000",
            corner_radius=8,
            height=45,
            command=self._calculate_performance
        )
        self.calc_button.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
    
    def _create_table_section(self, parent):
        """Create the output table section."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.colors["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"]
        )
        panel.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        
        # Panel Header
        header = ctk.CTkLabel(
            panel,
            text="📈 Account Performance",
            font=ctk.CTkFont(family="SF Pro Display", size=16, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        header.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Table Frame
        table_frame = ctk.CTkFrame(panel, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview styling
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background=self.colors["bg_input"],
            foreground=self.colors["text_primary"],
            fieldbackground=self.colors["bg_input"],
            rowheight=35
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=self.colors["bg_card"],
            foreground=self.colors["accent_gold"],
            font=("SF Pro Display", 11, "bold"),
            relief="flat"
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", self.colors["border"])],
            foreground=[("selected", self.colors["text_primary"])]
        )
        
        columns = ("bot_name", "account_id", "balance", "profit")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )
        
        self.tree.heading("bot_name", text="Bot Name")
        self.tree.heading("account_id", text="Account ID")
        self.tree.heading("balance", text="Balance")
        self.tree.heading("profit", text="Profit/Loss")
        
        self.tree.column("bot_name", width=200, anchor="w")
        self.tree.column("account_id", width=100, anchor="center")
        self.tree.column("balance", width=120, anchor="e")
        self.tree.column("profit", width=120, anchor="e")
        
        scrollbar = ctk.CTkScrollbar(
            table_frame,
            orientation="vertical",
            command=self.tree.yview,
            fg_color=self.colors["bg_input"],
            button_color=self.colors["border"],
            button_hover_color=self.colors["accent_gold"]
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.empty_label = ctk.CTkLabel(
            table_frame,
            text="No data to display\nPaste terminal data and click Calculate",
            font=ctk.CTkFont(family="SF Mono", size=12),
            text_color=self.colors["text_secondary"]
        )
        self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _create_right_panel(self, parent):
        """Create the right panel with stats and impact."""
        panel = ctk.CTkFrame(parent, fg_color="transparent")
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=0)
        panel.grid_rowconfigure(1, weight=0)
        panel.grid_rowconfigure(2, weight=1)
        
        # Growth Stats Section
        self._create_growth_stats_section(panel)
        
        # Farm Impact Section
        self._create_farm_impact_section(panel)
    
    def _create_growth_stats_section(self, parent):
        """Create the growth statistics section."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.colors["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"]
        )
        panel.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        panel.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            panel,
            text="📊 Growth Metrics",
            font=ctk.CTkFont(family="SF Pro Display", size=16, weight="bold"),
            text_color=self.colors["accent_gold"]
        )
        header.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Stats Grid
        stats_frame = ctk.CTkFrame(panel, fg_color="transparent")
        stats_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        stats_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Overall Growth
        ctk.CTkLabel(
            stats_frame,
            text="Overall Growth",
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=0, sticky="w")
        
        self.overall_growth_label = ctk.CTkLabel(
            stats_frame,
            text="0.00%",
            font=ctk.CTkFont(family="SF Mono", size=20, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        self.overall_growth_label.grid(row=1, column=0, sticky="w", pady=(5, 15))
        
        # Daily Average
        ctk.CTkLabel(
            stats_frame,
            text="Daily Avg Growth",
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=self.colors["text_secondary"]
        ).grid(row=0, column=1, sticky="w")
        
        self.daily_avg_label = ctk.CTkLabel(
            stats_frame,
            text="$0.00",
            font=ctk.CTkFont(family="SF Mono", size=20, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        self.daily_avg_label.grid(row=1, column=1, sticky="w", pady=(5, 15))
        
        # Total Balance
        ctk.CTkLabel(
            stats_frame,
            text="Total Balance",
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=self.colors["text_secondary"]
        ).grid(row=2, column=0, sticky="w")
        
        self.total_balance_label = ctk.CTkLabel(
            stats_frame,
            text="$0.00 (¢0)",
            font=ctk.CTkFont(family="SF Mono", size=14, weight="bold"),
            text_color=self.colors["accent_blue"]
        )
        self.total_balance_label.grid(row=3, column=0, sticky="w", pady=(5, 0))
        
        # Previous Run
        ctk.CTkLabel(
            stats_frame,
            text="Last Run",
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=self.colors["text_secondary"]
        ).grid(row=2, column=1, sticky="w")
        
        self.last_run_label = ctk.CTkLabel(
            stats_frame,
            text="Never",
            font=ctk.CTkFont(family="SF Mono", size=14, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        self.last_run_label.grid(row=3, column=1, sticky="w", pady=(5, 0))
    
    def _create_farm_impact_section(self, parent):
        """Create the farm impact section."""
        self.impact_panel = ctk.CTkFrame(
            parent,
            fg_color=self.colors["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.impact_panel.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.impact_panel.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            self.impact_panel,
            text="🌍 Farm Impact",
            font=ctk.CTkFont(family="SF Pro Display", size=16, weight="bold"),
            text_color=self.colors["accent_emerald"]
        )
        header.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Profit Amount Display
        self.impact_profit_label = ctk.CTkLabel(
            self.impact_panel,
            text="Profit: $0.00 USD",
            font=ctk.CTkFont(family="SF Mono", size=14, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        self.impact_profit_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Separator
        separator = ctk.CTkFrame(self.impact_panel, fg_color=self.colors["border"], height=1)
        separator.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # Impact Items Container
        self.impact_items_frame = ctk.CTkFrame(self.impact_panel, fg_color="transparent")
        self.impact_items_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Default message
        self.impact_default_label = ctk.CTkLabel(
            self.impact_items_frame,
            text="Calculate performance to see real-world impact",
            font=ctk.CTkFont(family="SF Mono", size=11),
            text_color=self.colors["text_secondary"]
        )
        self.impact_default_label.pack()
    
    def _create_footer(self):
        """Create the footer section."""
        footer = ctk.CTkFrame(self, fg_color=self.colors["bg_card"], corner_radius=0, height=40)
        footer.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        
        footer_text = ctk.CTkLabel(
            footer,
            text="🐺 Wolf Farm Calculator Pro v3.0 • Built with CustomTkinter & Matplotlib • Auto-Logging Enabled",
            font=ctk.CTkFont(family="SF Pro Display", size=11),
            text_color=self.colors["text_secondary"]
        )
        footer_text.pack(pady=10)
    
    def _on_input_focus_in(self, event):
        """Handle input textbox focus in."""
        current_text = self.input_text.get("1.0", "end-1c")
        if "Paste your MetaTrader" in current_text:
            self.input_text.delete("1.0", "end")
            self.input_text.configure(text_color=self.colors["text_primary"])
    
    def _on_input_focus_out(self, event):
        """Handle input textbox focus out."""
        current_text = self.input_text.get("1.0", "end-1c").strip()
        if not current_text:
            placeholder = """Paste your MetaTrader terminal data here...

Example format:
USC
369214589
10K MT4 #9LIVE
LX-ELITE TRADING
Self TradingMT41:200037.36327.830.0010365.1910327.8328/02/2026
08:16:18 PM"""
            self.input_text.insert("1.0", placeholder)
            self.input_text.configure(text_color=self.colors["text_secondary"])
    
    def _on_toggle_changed(self):
        """Handle cent/standard toggle change."""
        self._update_display()
    
    def _calculate_performance(self):
        """Parse input and calculate farm performance."""
        raw_text = self.input_text.get("1.0", "end-1c")
        
        if not raw_text or "Paste your MetaTrader" in raw_text:
            return
        
        # Check for duplicates
        content_hash = self.parser.get_content_hash(raw_text)
        if self.history.is_duplicate(content_hash):
            # Show warning but continue
            self._show_duplicate_warning()
            return
        
        # Parse accounts
        self.accounts = self.parser.parse(raw_text)
        
        if not self.accounts:
            return
        
        # Calculate totals
        self.current_total_balance = sum(acc.balance for acc in self.accounts)
        self.current_total_profit = sum(acc.profit for acc in self.accounts)
        account_count = len(self.accounts)
        
        # Save to history (with duplicate detection)
        entry = self.history.add_entry(
            total_balance=self.current_total_balance,
            total_profit=self.current_total_profit,
            account_count=account_count,
            content_hash=content_hash
        )
        
        # Update UI
        self._update_display()
        self._update_farm_age()
        self._update_history_tab()
        self._refresh_equity_curve()
    
    def _show_duplicate_warning(self):
        """Show a warning about duplicate entry."""
        import tkinter.messagebox as messagebox
        messagebox.showwarning(
            "Duplicate Entry",
            "This data was already processed within the last 5 minutes.\n"
            "The entry has been skipped to keep your equity curve clean."
        )
    
    def _load_last_history(self):
        """Load and display the last history entry."""
        last = self.history.last_entry
        if last:
            self.current_total_balance = last.total_balance
            self.current_total_profit = last.total_profit
            self.accounts = []
            self._update_display()
            self._update_farm_age()
    
    def _update_display(self):
        """Update all UI displays."""
        self._update_table()
        self._update_summary()
        self._update_growth_metrics()
        self._update_farm_impact()
    
    def _update_table(self):
        """Update the output table with parsed data."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.accounts:
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")
            return
        
        self.empty_label.place_forget()
        
        for account in self.accounts:
            profit = account.profit
            tag = "profit" if profit >= 0 else "loss"
            
            self.tree.insert(
                "",
                "end",
                values=(
                    account.bot_name,
                    account.account_id,
                    self._format_currency(account.balance),
                    self._format_currency(profit)
                ),
                tags=(tag,)
            )
        
        self.tree.tag_configure("profit", foreground=self.colors["profit_green"])
        self.tree.tag_configure("loss", foreground=self.colors["loss_red"])
    
    def _update_summary(self):
        """Update the summary dashboard."""
        account_count = len(self.accounts) if self.accounts else 0
        
        if self.accounts:
            total_profit = self.current_total_profit
        elif self.history.last_entry:
            total_profit = self.history.last_entry.total_profit
            account_count = self.history.last_entry.account_count
        else:
            total_profit = 0
        
        color = self.colors["profit_green"] if total_profit >= 0 else self.colors["loss_red"]
        
        self.total_profit_label.configure(
            text=f"Total Farm Profit: {self._format_currency(total_profit)}",
            text_color=color
        )
        self.account_count_label.configure(
            text=f"Accounts: {account_count}",
            text_color=self.colors["accent_gold"]
        )
    
    def _update_growth_metrics(self):
        """Update growth metrics display."""
        metrics = self.history.calculate_growth_metrics(self.current_total_balance)
        
        # Overall Growth
        overall_color = self.colors["profit_green"] if metrics['overall_growth_pct'] >= 0 else self.colors["loss_red"]
        self.overall_growth_label.configure(
            text=f"{metrics['overall_growth_pct']:+.2f}%",
            text_color=overall_color
        )
        
        # Delta
        delta_color = self.colors["profit_green"] if metrics['delta_pct'] >= 0 else self.colors["loss_red"]
        delta_text = f"{metrics['delta_pct']:+.2f}%"
        self.delta_label.configure(text=f"Δ {delta_text}", text_color=delta_color)
        
        # Daily Average
        daily_scaled = self._scale_amount(metrics['daily_avg_growth'])
        self.daily_avg_label.configure(
            text=f"${daily_scaled:,.2f}",
            text_color=self.colors["accent_blue"]
        )
        
        # Total Balance
        standard_balance = self.current_total_balance / 100
        self.total_balance_label.configure(
            text=f"${standard_balance:,.2f} (¢{self.current_total_balance:,.0f})",
            text_color=self.colors["accent_blue"]
        )
        
        # Last Run
        if self.history.last_entry:
            last_time = datetime.fromisoformat(self.history.last_entry.timestamp)
            self.last_run_label.configure(text=last_time.strftime("%Y-%m-%d %H:%M"))
    
    def _update_farm_impact(self):
        """Update the farm impact section."""
        for widget in self.impact_items_frame.winfo_children():
            widget.destroy()
        
        profit_usd = self.current_total_profit / 100
        
        self.impact_profit_label.configure(
            text=f"Profit: ${profit_usd:,.2f} USD",
            text_color=self.colors["profit_green"] if profit_usd >= 0 else self.colors["loss_red"]
        )
        
        if profit_usd <= 0:
            ctk.CTkLabel(
                self.impact_items_frame,
                text="No positive profit to measure impact",
                font=ctk.CTkFont(family="SF Mono", size=11),
                text_color=self.colors["text_secondary"]
            ).pack()
            return
        
        impacts = FarmImpactCalculator.calculate_impacts(profit_usd)
        
        if not impacts:
            ctk.CTkLabel(
                self.impact_items_frame,
                text="Profit too small for meaningful comparisons",
                font=ctk.CTkFont(family="SF Mono", size=11),
                text_color=self.colors["text_secondary"]
            ).pack()
            return
        
        for impact in impacts:
            item_frame = ctk.CTkFrame(self.impact_items_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=3)
            
            ctk.CTkLabel(
                item_frame,
                text=f"{impact['quantity']}x",
                font=ctk.CTkFont(family="SF Mono", size=18, weight="bold"),
                text_color=self.colors["accent_gold"]
            ).pack(side="left")
            
            ctk.CTkLabel(
                item_frame,
                text=f" {impact['name']}",
                font=ctk.CTkFont(family="SF Mono", size=12),
                text_color=self.colors["text_primary"]
            ).pack(side="left", padx=(5, 0))
    
    def _update_farm_age(self):
        """Update the farm age display."""
        self.farm_age_label.configure(text=self._get_farm_age_text())


def main():
    """Main entry point."""
    app = FarmCalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
