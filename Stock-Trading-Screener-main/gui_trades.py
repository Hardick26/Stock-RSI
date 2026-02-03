#!/usr/bin/env python3
"""
Professional Stock Trading Screener Dashboard
Advanced real-time monitoring system for technical analysis signals
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import csv
from pathlib import Path
from datetime import datetime
import threading
import subprocess
import sys
import time
from ticker_info.real_time import real_time_data

class ModernStyle:
    """Professional color scheme and styling"""
    # Modern dark theme with high contrast
    PRIMARY_BG = "#1a1a2e"      # Dark navy - Main background
    SECONDARY_BG = "#16213e"    # Slightly darker navy - Panels
    TERTIARY_BG = "#0f3460"     # Deep blue - Cards and inputs
    TABLE_BG = "#2a3f5f"        # Dark blueish-grey - Table rows (darker)
    
    # Text colors - High contrast
    PRIMARY_TEXT = "#ffffff"    # Pure white - Main text
    SECONDARY_TEXT = "#e0e0e0"  # Light grey - Secondary text
    TERTIARY_TEXT = "#b0b0b0"   # Medium grey - Tertiary text
    
    # Accent colors - Vibrant and visible
    SUCCESS = "#00ff88"         # Bright green - Positive
    WARNING = "#ff6b35"         # Bright orange - Negative
    INFO = "#00d4ff"            # Bright cyan - Information
    DANGER = "#ff0055"          # Bright pink - Danger
    
    # UI Elements
    BUTTON_BG = "#00d4ff"       # Bright cyan button
    BUTTON_HOVER = "#00a8cc"    # Darker cyan on hover
    BORDER_COLOR = "#404060"    # Visible border

class TradeSignalProfessionalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Trading Screener Dashboard - Professional Edition")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)
        
        # Set app icon (optional)
        self.root.configure(bg=ModernStyle.PRIMARY_BG)
        
        # Setup fonts
        self.setup_fonts()
        
        # Threading
        self.running = True
        self.refresh_interval = 5000  # 5 seconds for real-time
        self.screener_running = False
        self.current_trades = []
        self.selected_trade_index = None
        self.all_stocks_data = []
        self.filtered_data = []
        self.search_var = tk.StringVar()
        self.realtime_auto_update = True
        self.realtime_update_thread = None
        
        # Create GUI
        self.create_ui()
        
        # Start auto-refresh
        self.auto_refresh()
        
        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_fonts(self):
        """Setup professional fonts"""
        self.title_font = font.Font(family="Segoe UI", size=20, weight="bold")
        self.subtitle_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.header_font = font.Font(family="Segoe UI", size=11, weight="bold")
        self.normal_font = font.Font(family="Segoe UI", size=10)
        self.small_font = font.Font(family="Segoe UI", size=9)
        self.mono_font = font.Font(family="Courier New", size=9)
    
    def create_ui(self):
        """Create the main UI"""
        # Header
        self.create_header()
        
        # Main content
        main_container = tk.Frame(self.root, bg=ModernStyle.PRIMARY_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Sidebar
        self.create_sidebar(main_container)
        
        # Main content area
        content_container = tk.Frame(main_container, bg=ModernStyle.PRIMARY_BG)
        content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Control panel
        self.create_control_panel(content_container)
        
        # Content area
        self.create_content_area(content_container)
        
        # Footer/Status bar
        self.create_footer()
    
    def create_header(self):
        """Header removed - using full space for content"""
        # Header is now removed
        pass
    
    def create_sidebar(self, parent):
        """Create left sidebar with real-time stock prices"""
        sidebar = tk.Frame(parent, bg=ModernStyle.SECONDARY_BG, width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        sidebar.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = tk.Frame(sidebar, bg=ModernStyle.SECONDARY_BG)
        sidebar_header.pack(fill=tk.X, padx=15, pady=15)
        
        sidebar_title = tk.Label(
            sidebar_header,
            text="� Stock Prices",
            font=self.header_font,
            bg=ModernStyle.SECONDARY_BG,
            fg=ModernStyle.INFO
        )
        sidebar_title.pack(anchor=tk.W)
        
        # Scrollable frame for stocks
        canvas = tk.Canvas(
            sidebar,
            bg=ModernStyle.SECONDARY_BG,
            highlightthickness=0,
            relief=tk.FLAT
        )
        scrollbar = ttk.Scrollbar(sidebar, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernStyle.SECONDARY_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Store reference for updates
        self.sidebar_stocks_frame = scrollable_frame
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create stock cards - will be updated dynamically
        self.sidebar_stock_cards = {}
    
    def update_sidebar_stocks(self):
        """Update sidebar with real-time stock prices"""
        # Get stocks to display
        if self.all_stocks_data:
            signal_stocks = [s.get("Stock Name", "").strip() for s in self.all_stocks_data 
                            if s.get("Trade Signals", "").strip()]
        else:
            from ticker_info.stock_list import nse_stocks
            signal_stocks = nse_stocks[:4]
        
        # Clear existing cards
        for card in self.sidebar_stock_cards.values():
            card.destroy()
        self.sidebar_stock_cards.clear()
        
        # Create new cards with real-time data
        for stock in signal_stocks:
            if stock:
                live_data = real_time_data.get_cached_price(stock)
                if live_data:
                    self.create_sidebar_stock_card(stock, live_data)
    
    def create_sidebar_stock_card(self, stock, live_data):
        """Create a stock card in sidebar"""
        card = tk.Frame(
            self.sidebar_stocks_frame,
            bg=ModernStyle.TERTIARY_BG,
            relief=tk.SUNKEN,
            bd=1
        )
        card.pack(fill=tk.X, pady=8, padx=5)
        
        # Stock name
        name_label = tk.Label(
            card,
            text=stock,
            font=self.header_font,
            bg=ModernStyle.TERTIARY_BG,
            fg=ModernStyle.INFO
        )
        name_label.pack(anchor=tk.W, padx=10, pady=(8, 2))
        
        # Price
        price_label = tk.Label(
            card,
            text=f"Price: {live_data.get('price', 'N/A')}",
            font=self.normal_font,
            bg=ModernStyle.TERTIARY_BG,
            fg=ModernStyle.PRIMARY_TEXT
        )
        price_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Change with color coding
        change_pct = live_data.get('change_pct', '0')
        try:
            change_val = float(change_pct.rstrip('%'))
            color = ModernStyle.SUCCESS if change_val >= 0 else ModernStyle.WARNING
        except:
            color = ModernStyle.PRIMARY_TEXT
        
        change_label = tk.Label(
            card,
            text=f"Change: {live_data.get('change', 'N/A')} ({change_pct})",
            font=self.normal_font,
            bg=ModernStyle.TERTIARY_BG,
            fg=color
        )
        change_label.pack(anchor=tk.W, padx=10, pady=(2, 8))
        
        self.sidebar_stock_cards[stock] = card
    
    def create_control_panel(self, parent):
        """Create control panel"""
        control_panel = tk.Frame(parent, bg=ModernStyle.SECONDARY_BG, height=70)
        control_panel.pack(fill=tk.X)
        control_panel.pack_propagate(False)
        
        control_inner = tk.Frame(control_panel, bg=ModernStyle.SECONDARY_BG)
        control_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # Run button
        run_btn = self.create_button(
            control_inner,
            "🔄 RUN SCREENER",
            self.run_screener_thread,
            ModernStyle.BUTTON_BG,
            width=15
        )
        run_btn.pack(side=tk.LEFT, padx=5)
        self.run_btn = run_btn
        
        # Separator
        sep = tk.Frame(control_inner, bg=ModernStyle.BORDER_COLOR, width=1)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Export button
        export_btn = self.create_button(
            control_inner,
            "📥 EXPORT DATA",
            self.export_data,
            ModernStyle.INFO,
            width=13
        )
        export_btn.pack(side=tk.LEFT, padx=5)
    
    def create_button(self, parent, text, command, bg_color, width=12):
        """Create a professional button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.normal_font,
            bg=bg_color,
            fg=ModernStyle.PRIMARY_BG,
            width=width,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=10,
            pady=6,
            activebackground=bg_color,
            activeforeground=ModernStyle.PRIMARY_BG
        )
        return btn
    
    def create_content_area(self, parent):
        """Create main content area - only real-time prices"""
        content = tk.Frame(parent, bg=ModernStyle.PRIMARY_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Real-time Prices (Full Screen)
        self.create_realtime_view(content)
    
    def create_trades_table(self, parent):
        """Create professional trades table with all stock data"""
        # Header
        header = tk.Label(
            parent,
            text="📋 All Stocks & Trade Signals",
            font=self.header_font,
            bg=ModernStyle.PRIMARY_BG,
            fg=ModernStyle.INFO
        )
        header.pack(anchor=tk.W, pady=(0, 10))
        
        # Table frame
        table_frame = tk.Frame(parent, bg=ModernStyle.SECONDARY_BG, relief=tk.SUNKEN, bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars (both vertical and horizontal)
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure custom style for treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview',
                       background=ModernStyle.TABLE_BG,
                       foreground=ModernStyle.PRIMARY_TEXT,
                       fieldbackground=ModernStyle.TABLE_BG,
                       font=self.small_font,
                       rowheight=30)
        style.configure('Treeview.Heading',
                       background=ModernStyle.SECONDARY_BG,
                       foreground=ModernStyle.INFO,
                       font=self.normal_font)
        style.map('Treeview',
                 background=[('selected', ModernStyle.INFO)],
                 foreground=[('selected', ModernStyle.PRIMARY_BG)])
        
        # Treeview with extended columns
        columns = ("Stock", "Signal", "Price", "1Y", "6M", "1M", "1W", "Avg Move", "10D Move")
        self.trades_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            height=15,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        scrollbar_y.config(command=self.trades_tree.yview)
        scrollbar_x.config(command=self.trades_tree.xview)
        
        # Configure columns with appropriate widths
        self.trades_tree.column("Stock", width=70, anchor=tk.W)
        self.trades_tree.column("Signal", width=200, anchor=tk.W)
        self.trades_tree.column("Price", width=70, anchor=tk.CENTER)
        self.trades_tree.column("1Y", width=65, anchor=tk.CENTER)
        self.trades_tree.column("6M", width=65, anchor=tk.CENTER)
        self.trades_tree.column("1M", width=65, anchor=tk.CENTER)
        self.trades_tree.column("1W", width=65, anchor=tk.CENTER)
        self.trades_tree.column("Avg Move", width=80, anchor=tk.CENTER)
        self.trades_tree.column("10D Move", width=80, anchor=tk.CENTER)
        
        # Headings
        self.trades_tree.heading("Stock", text="Stock")
        self.trades_tree.heading("Signal", text="Trade Signal")
        self.trades_tree.heading("Price", text="Price (₹)")
        self.trades_tree.heading("1Y", text="1Y Return")
        self.trades_tree.heading("6M", text="6M Return")
        self.trades_tree.heading("1M", text="1M Return")
        self.trades_tree.heading("1W", text="1W Return")
        self.trades_tree.heading("Avg Move", text="Avg Move")
        self.trades_tree.heading("10D Move", text="10D Avg Move")
        
        # Bind selection
        self.trades_tree.bind('<<TreeviewSelect>>', self.on_trade_selected)
        
        self.trades_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_details_view(self, parent):
        """Create professional details view"""
        # Header
        header = tk.Label(
            parent,
            text="🔍 Signal Details",
            font=self.header_font,
            bg=ModernStyle.PRIMARY_BG,
            fg=ModernStyle.INFO
        )
        header.pack(anchor=tk.W, pady=(0, 10))
        
        # Details frame
        details_frame = tk.Frame(parent, bg=ModernStyle.SECONDARY_BG, relief=tk.SUNKEN, bd=1)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(details_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        self.details_text = tk.Text(
            details_frame,
            height=25,
            width=45,
            bg=ModernStyle.TERTIARY_BG,
            fg=ModernStyle.PRIMARY_TEXT,
            font=self.mono_font,
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10
        )
        scrollbar.config(command=self.details_text.yview)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.details_text.tag_config("header", foreground=ModernStyle.INFO, font=self.header_font)
        self.details_text.tag_config("label", foreground=ModernStyle.SECONDARY_TEXT)
        self.details_text.tag_config("positive", foreground=ModernStyle.SUCCESS)
        self.details_text.tag_config("negative", foreground=ModernStyle.WARNING)
        self.details_text.tag_config("value", foreground=ModernStyle.PRIMARY_TEXT)
        
        # Placeholder
        self.details_text.insert("1.0", "Select a signal to view details")
        self.details_text.config(state=tk.DISABLED)
    
    def create_all_stocks_view(self, parent):
        """Create view for all stocks data"""
        # Header
        header = tk.Label(
            parent,
            text="📊 Complete Stock Database",
            font=self.header_font,
            bg=ModernStyle.PRIMARY_BG,
            fg=ModernStyle.INFO
        )
        header.pack(anchor=tk.W, padx=15, pady=15)
        
        # Control panel for all stocks view
        control_frame = tk.Frame(parent, bg=ModernStyle.PRIMARY_BG)
        control_frame.pack(fill=tk.X, padx=15, pady=5)
        
        # Search box
        search_label = tk.Label(
            control_frame,
            text="Search Stock:",
            font=self.normal_font,
            bg=ModernStyle.PRIMARY_BG,
            fg=ModernStyle.PRIMARY_TEXT
        )
        search_label.pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_stocks)
        search_entry = tk.Entry(
            control_frame,
            textvariable=self.search_var,
            font=self.normal_font,
            bg=ModernStyle.TERTIARY_BG,
            fg=ModernStyle.PRIMARY_TEXT,
            width=20,
            relief=tk.SUNKEN,
            bd=1
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Statistics label
        self.stats_label = tk.Label(
            control_frame,
            text="Total: 0 stocks",
            font=self.normal_font,
            bg=ModernStyle.PRIMARY_BG,
            fg=ModernStyle.SECONDARY_TEXT
        )
        self.stats_label.pack(side=tk.RIGHT, padx=10)
        
        # Table frame
        table_frame = tk.Frame(parent, bg=ModernStyle.SECONDARY_BG, relief=tk.SUNKEN, bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure style
        style = ttk.Style()
        style.configure('AllStocks.Treeview',
                       background=ModernStyle.TABLE_BG,
                       foreground=ModernStyle.PRIMARY_TEXT,
                       fieldbackground=ModernStyle.TABLE_BG,
                       font=self.small_font,
                       rowheight=25)
        style.configure('AllStocks.Treeview.Heading',
                       background=ModernStyle.SECONDARY_BG,
                       foreground=ModernStyle.INFO,
                       font=self.normal_font)
        style.map('AllStocks.Treeview',
                 background=[('selected', ModernStyle.INFO)],
                 foreground=[('selected', ModernStyle.PRIMARY_BG)])
        
        # Treeview
        columns = ("Stock", "Signal", "Price", "1Y", "6M", "1M", "1W", "Avg Move", "10D Move")
        self.all_stocks_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            height=20,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            style='AllStocks.Treeview'
        )
        scrollbar_y.config(command=self.all_stocks_tree.yview)
        scrollbar_x.config(command=self.all_stocks_tree.xview)
        
        # Configure columns
        self.all_stocks_tree.column("Stock", width=70, anchor=tk.W)
        self.all_stocks_tree.column("Signal", width=200, anchor=tk.W)
        self.all_stocks_tree.column("Price", width=70, anchor=tk.CENTER)
        self.all_stocks_tree.column("1Y", width=65, anchor=tk.CENTER)
        self.all_stocks_tree.column("6M", width=65, anchor=tk.CENTER)
        self.all_stocks_tree.column("1M", width=65, anchor=tk.CENTER)
        self.all_stocks_tree.column("1W", width=65, anchor=tk.CENTER)
        self.all_stocks_tree.column("Avg Move", width=80, anchor=tk.CENTER)
        self.all_stocks_tree.column("10D Move", width=80, anchor=tk.CENTER)
        
        # Headings
        self.all_stocks_tree.heading("Stock", text="Stock")
        self.all_stocks_tree.heading("Signal", text="Trade Signal")
        self.all_stocks_tree.heading("Price", text="Price (₹)")
        self.all_stocks_tree.heading("1Y", text="1Y Return")
        self.all_stocks_tree.heading("6M", text="6M Return")
        self.all_stocks_tree.heading("1M", text="1M Return")
        self.all_stocks_tree.heading("1W", text="1W Return")
        self.all_stocks_tree.heading("Avg Move", text="Avg Move")
        self.all_stocks_tree.heading("10D Move", text="10D Avg Move")
        
        self.all_stocks_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_realtime_view(self, parent):
        """Create real-time stock prices view - fullscreen, auto-updating"""
        # Header
        header_frame = tk.Frame(parent, bg=ModernStyle.PRIMARY_BG)
        header_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Top section with title and controls
        top_section = tk.Frame(header_frame, bg=ModernStyle.PRIMARY_BG)
        top_section.pack(fill=tk.X)
        
        header = tk.Label(
            top_section,
            text="💹 Real-Time Stock Prices",
            font=self.header_font,
            bg=ModernStyle.PRIMARY_BG,
            fg=ModernStyle.INFO
        )
        header.pack(anchor=tk.W, side=tk.LEFT)
        
        # Timer control on the right
        timer_frame = tk.Frame(top_section, bg=ModernStyle.PRIMARY_BG)
        timer_frame.pack(anchor=tk.E, side=tk.RIGHT)
        
        timer_label = tk.Label(
            timer_frame,
            text="Refresh Interval (seconds):",
            font=self.normal_font,
            bg=ModernStyle.PRIMARY_BG,
            fg=ModernStyle.PRIMARY_TEXT
        )
        timer_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entry field for timer
        self.interval_var = tk.StringVar(value="5")
        interval_entry = tk.Entry(
            timer_frame,
            textvariable=self.interval_var,
            font=self.normal_font,
            width=5,
            bg=ModernStyle.TERTIARY_BG,
            fg=ModernStyle.PRIMARY_TEXT,
            insertbackground=ModernStyle.PRIMARY_TEXT
        )
        interval_entry.pack(side=tk.LEFT, padx=(0, 10))
        interval_entry.bind('<Return>', self.update_interval_on_enter)
        
        # Apply button
        apply_btn = tk.Button(
            timer_frame,
            text="⚙ Set",
            font=self.normal_font,
            bg=ModernStyle.BUTTON_BG,
            fg=ModernStyle.PRIMARY_TEXT,
            command=self.update_interval,
            relief=tk.FLAT,
            padx=10,
            pady=5,
            activebackground=ModernStyle.BUTTON_HOVER
        )
        apply_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.interval_status = tk.Label(
            timer_frame,
            text="(Current: 5s)",
            font=self.small_font,
            bg=ModernStyle.PRIMARY_BG,
            fg=ModernStyle.SUCCESS
        )
        self.interval_status.pack(side=tk.LEFT)
        
        # Status info
        status_frame = tk.Frame(parent, bg=ModernStyle.PRIMARY_BG)
        status_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.realtime_status = tk.Label(
            status_frame,
            text="🔄 Auto-updating... | Last Update: Starting...",
            font=self.small_font,
            bg=ModernStyle.PRIMARY_BG,
            fg=ModernStyle.SUCCESS
        )
        self.realtime_status.pack(anchor=tk.W)
        
        # Table frame
        table_frame = tk.Frame(parent, bg=ModernStyle.SECONDARY_BG, relief=tk.SUNKEN, bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure style
        style = ttk.Style()
        style.configure('RealTime.Treeview',
                       background=ModernStyle.TABLE_BG,
                       foreground=ModernStyle.PRIMARY_TEXT,
                       fieldbackground=ModernStyle.TABLE_BG,
                       font=self.small_font,
                       rowheight=28)
        style.configure('RealTime.Treeview.Heading',
                       background=ModernStyle.SECONDARY_BG,
                       foreground=ModernStyle.INFO,
                       font=self.normal_font)
        style.map('RealTime.Treeview',
                 background=[('selected', ModernStyle.INFO)],
                 foreground=[('selected', ModernStyle.PRIMARY_BG)])
        
        # Treeview for real-time data
        columns = ("Stock", "Price", "Change", "Change %", "High", "Low", "Volume", "Last Update")
        self.realtime_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            height=20,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            style='RealTime.Treeview'
        )
        scrollbar_y.config(command=self.realtime_tree.yview)
        scrollbar_x.config(command=self.realtime_tree.xview)
        
        # Configure columns
        self.realtime_tree.column("Stock", width=100, anchor=tk.W)
        self.realtime_tree.column("Price", width=120, anchor=tk.CENTER)
        self.realtime_tree.column("Change", width=120, anchor=tk.CENTER)
        self.realtime_tree.column("Change %", width=120, anchor=tk.CENTER)
        self.realtime_tree.column("High", width=120, anchor=tk.CENTER)
        self.realtime_tree.column("Low", width=120, anchor=tk.CENTER)
        self.realtime_tree.column("Volume", width=140, anchor=tk.CENTER)
        self.realtime_tree.column("Last Update", width=140, anchor=tk.CENTER)
        
        # Headings
        self.realtime_tree.heading("Stock", text="Stock Name")
        self.realtime_tree.heading("Price", text="Current Price (₹)")
        self.realtime_tree.heading("Change", text="Change (₹)")
        self.realtime_tree.heading("Change %", text="Change %")
        self.realtime_tree.heading("High", text="Day High (₹)")
        self.realtime_tree.heading("Low", text="Day Low (₹)")
        self.realtime_tree.heading("Volume", text="Trading Volume")
        self.realtime_tree.heading("Last Update", text="Last Update Time")
        
        self.realtime_tree.pack(fill=tk.BOTH, expand=True)
        self.realtime_update_thread = None
        
        # Load initial data
        self.update_realtime_display()
    
    def populate_trade_signals_tab(self):
        """Populate Trade Signals tab with signals only"""
        # Clear existing items
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
        
        # Filter stocks with signals
        signal_stocks = [s for s in self.all_stocks_data if s.get("Trade Signals", "").strip()]
        
        # Populate tree
        for idx, stock in enumerate(signal_stocks):
            values = (
                stock.get("Stock Name", ""),
                stock.get("Trade Signals", "")[:60] + "...",
                stock.get("CMP", ""),
                stock.get("1Y Return", ""),
                stock.get("6M Return", ""),
                stock.get("1M Return", ""),
                stock.get("1W Return", ""),
                stock.get("Avg Movement", ""),
                stock.get("10D Avg Movement", "")
            )
            self.trades_tree.insert("", "end", iid=f"signal_{idx}", values=values)
    
    def populate_all_stocks_tab(self):
        """Populate All Stocks tab with complete data"""
        # Clear existing items
        for item in self.all_stocks_tree.get_children():
            self.all_stocks_tree.delete(item)
        
        # Populate tree
        for idx, stock in enumerate(self.filtered_data):
            signal_text = stock.get("Trade Signals", "")
            signal_preview = signal_text[:50] + "..." if len(signal_text) > 50 else signal_text
            
            values = (
                stock.get("Stock Name", ""),
                signal_preview,
                stock.get("CMP", ""),
                stock.get("1Y Return", ""),
                stock.get("6M Return", ""),
                stock.get("1M Return", ""),
                stock.get("1W Return", ""),
                stock.get("Avg Movement", ""),
                stock.get("10D Avg Movement", "")
            )
            item_id = self.all_stocks_tree.insert("", "end", values=values)
            
            # Color code returns
            try:
                year_return = float(stock.get("1Y Return", "0").rstrip("%"))
                if year_return < 0:
                    self.all_stocks_tree.item(item_id, tags=('negative',))
                elif year_return > 0:
                    self.all_stocks_tree.item(item_id, tags=('positive',))
            except:
                pass
        
        # Configure tags
        self.all_stocks_tree.tag_configure('positive', foreground=ModernStyle.SUCCESS)
        self.all_stocks_tree.tag_configure('negative', foreground=ModernStyle.WARNING)
        
        # Update stats
        self.stats_label.config(text=f"Total: {len(self.filtered_data)} stocks")
    
    def populate_performance_tab(self):
        """Populate Performance Analysis tab"""
        # This will be populated when analytics tab is created
        pass
    
    def filter_stocks(self, *args):
        """Filter stocks based on search term"""
        search_term = self.search_var.get().upper()
        
        if not search_term:
            self.filtered_data = self.all_stocks_data.copy()
        else:
            self.filtered_data = [
                s for s in self.all_stocks_data
                if search_term in s.get("Stock Name", "").upper() or
                   search_term in s.get("Trade Signals", "").upper()
            ]
        
        self.populate_all_stocks_tab()
    
    def fetch_live_prices(self):
        """Fetch live prices for signal stocks in background"""
        def fetch_in_thread():
            try:
                if not self.all_stocks_data:
                    # Load sample stocks if no data yet
                    from ticker_info.stock_list import nse_stocks
                    signal_stocks = nse_stocks[:4]  # First 4 stocks as example
                else:
                    # Get signal stocks
                    signal_stocks = [s.get("Stock Name", "").strip() for s in self.all_stocks_data 
                                   if s.get("Trade Signals", "").strip()]
                
                # Fetch prices
                for stock in signal_stocks:
                    if stock:
                        real_time_data.get_live_price(stock)
                
                # Update displays
                self.update_realtime_display()
                self.update_sidebar_stocks()
                
                # Update status
                self.realtime_status.config(
                    text=f"🔄 Auto-updating... | Last Update: {datetime.now().strftime('%H:%M:%S')}",
                    fg=ModernStyle.SUCCESS
                )
            except Exception as e:
                self.realtime_status.config(
                    text=f"⚠ Update failed: {str(e)[:40]}",
                    fg=ModernStyle.WARNING
                )
        
        thread = threading.Thread(target=fetch_in_thread, daemon=True)
        thread.start()
    
    def toggle_realtime_update(self):
        """Toggle real-time auto-update"""
        # Not needed - always updating
        pass
    
    def start_realtime_updates(self):
        """Start periodic real-time updates"""
        # Not needed - handled by auto_refresh
        pass
    
    def stop_realtime_updates(self):
        """Stop real-time updates"""
        # Not needed - always updating
        pass
    
    def update_interval_on_enter(self, event=None):
        """Update interval when Enter key is pressed"""
        self.update_interval()
    
    def update_interval(self):
        """Update the refresh interval from user input"""
        try:
            new_interval = int(self.interval_var.get())
            
            # Validate interval (1 to 300 seconds)
            if new_interval < 1:
                new_interval = 1
                self.interval_var.set("1")
            elif new_interval > 300:
                new_interval = 300
                self.interval_var.set("300")
            
            # Convert to milliseconds
            self.refresh_interval = new_interval * 1000
            
            # Update status
            self.interval_status.config(
                text=f"(Current: {new_interval}s)",
                fg=ModernStyle.SUCCESS
            )
            
            self.realtime_status.config(
                text=f"🔄 Interval updated to {new_interval} seconds | Last Update: {datetime.now().strftime('%H:%M:%S')}",
                fg=ModernStyle.SUCCESS
            )
            
        except ValueError:
            # Invalid input
            self.interval_var.set("5")
            self.refresh_interval = 5000
            self.interval_status.config(
                text="(Invalid input - set to 5s)",
                fg=ModernStyle.WARNING
            )
    
    def update_realtime_display(self):
        """Update real-time display table"""
        # Clear existing items
        for item in self.realtime_tree.get_children():
            self.realtime_tree.delete(item)
        
        # Get signal stocks
        if self.all_stocks_data:
            signal_stocks = [s.get("Stock Name", "").strip() for s in self.all_stocks_data 
                            if s.get("Trade Signals", "").strip()]
        else:
            # Use default stocks if no CSV data
            from ticker_info.stock_list import nse_stocks
            signal_stocks = nse_stocks[:4]
        
        # Populate with real-time data
        for stock in signal_stocks:
            if stock:
                live_data = real_time_data.get_cached_price(stock)
                if live_data:
                    values = (
                        stock,
                        live_data.get('price', 'N/A'),
                        live_data.get('change', 'N/A'),
                        live_data.get('change_pct', 'N/A'),
                        live_data.get('high', 'N/A'),
                        live_data.get('low', 'N/A'),
                        live_data.get('volume', 'N/A'),
                        live_data.get('last_update', 'N/A')
                    )
                    
                    item_id = self.realtime_tree.insert("", "end", values=values)
                    
                    # Color code by change
                    try:
                        change_pct = float(live_data.get('change_pct', '0').rstrip('%'))
                        if change_pct < 0:
                            self.realtime_tree.item(item_id, tags=('negative',))
                        elif change_pct > 0:
                            self.realtime_tree.item(item_id, tags=('positive',))
                    except:
                        pass
        
        # Configure tags
        self.realtime_tree.tag_configure('positive', foreground=ModernStyle.SUCCESS)
        self.realtime_tree.tag_configure('negative', foreground=ModernStyle.WARNING)
    
    def create_footer(self):
        """Create professional footer"""
        footer = tk.Frame(self.root, bg=ModernStyle.SECONDARY_BG, height=40)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        # Separator
        sep = tk.Frame(self.root, bg=ModernStyle.BORDER_COLOR, height=1)
        sep.pack(fill=tk.X)
        
        footer_inner = tk.Frame(footer, bg=ModernStyle.SECONDARY_BG)
        footer_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        
        # Left side - timestamp
        self.timestamp_label = tk.Label(
            footer_inner,
            text="Last Update: Never",
            font=self.small_font,
            bg=ModernStyle.SECONDARY_BG,
            fg=ModernStyle.SECONDARY_TEXT
        )
        self.timestamp_label.pack(side=tk.LEFT)
        
        # Center - status message
        self.status_message = tk.Label(
            footer_inner,
            text="Ready",
            font=self.small_font,
            bg=ModernStyle.SECONDARY_BG,
            fg=ModernStyle.SUCCESS
        )
        self.status_message.pack(side=tk.LEFT, padx=20)
        
        # Right side - version
        version_label = tk.Label(
            footer_inner,
            text="v1.0.0 | Professional Edition",
            font=self.small_font,
            bg=ModernStyle.SECONDARY_BG,
            fg=ModernStyle.TERTIARY_TEXT
        )
        version_label.pack(side=tk.RIGHT)
    
    def get_latest_results_file(self):
        """Get latest results CSV file"""
        results_dir = Path('.')
        csv_files = list(results_dir.glob('Stock Trade Signals*.csv'))
        if not csv_files:
            return None
        return sorted(csv_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
    
    def read_trades(self, filepath):
        """Read trades from CSV"""
        trades = []
        if not filepath.exists():
            return trades
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Stock Name') and row.get('Trade Signals'):
                        trades.append(row)
        except Exception as e:
            print(f"Error reading file: {e}")
        
        return trades
    
    def update_trades_display(self):
        """Update trades table with all stock data"""
        # Clear table
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
        
        # Get latest results
        results_file = self.get_latest_results_file()
        if not results_file:
            self.signal_count_label.config(text="0")
            self.positive_count_label.config(text="0")
            self.negative_count_label.config(text="0")
            return
        
        # Read all stock data from CSV
        self.all_stocks_data = []
        self.current_trades = []
        
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.all_stocks_data.append(row)
                    if row.get('Trade Signals', '').strip():
                        self.current_trades.append(row)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return
        
        # Initialize filtered data
        self.filtered_data = self.all_stocks_data.copy()
        
        # Update sidebar stats
        positive_count = sum(1 for t in self.all_stocks_data if '+' in t.get('1Y Return', ''))
        negative_count = sum(1 for t in self.all_stocks_data if '-' in t.get('1Y Return', ''))
        
        self.signal_count_label.config(text=str(len(self.current_trades)))
        self.positive_count_label.config(text=str(positive_count))
        self.negative_count_label.config(text=str(negative_count))
        
        # Populate all tabs
        self.populate_trade_signals_tab()
        self.populate_all_stocks_tab()
        self.populate_performance_tab()
        
        # Update timestamp
        self.timestamp_label.config(
            text=f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.last_update_sidebar.config(
            text=f"Last: {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def on_trade_selected(self, event):
        """Handle trade selection"""
        selection = self.trades_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        # Extract index from item ID (format: "signal_N")
        if isinstance(item, str) and item.startswith("signal_"):
            index = int(item.split("_")[1])
        else:
            index = int(item)
        
        self.selected_trade_index = index
        
        if index < len(self.all_stocks_data):
            # Find the signal stock from all_stocks_data
            signal_stocks = [s for s in self.all_stocks_data if s.get("Trade Signals", "").strip()]
            if index < len(signal_stocks):
                self.display_trade_details(signal_stocks[index])
    
    def display_trade_details(self, trade):
        """Display comprehensive trade information"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        
        stock = trade.get('Stock Name', 'N/A').strip()
        
        # Header
        self.details_text.insert(tk.END, f"\n{stock}\n", "header")
        self.details_text.insert(tk.END, "═" * 45 + "\n\n")
        
        # Price Section
        self.details_text.insert(tk.END, "💰 CURRENT PRICE\n", "label")
        self.details_text.insert(tk.END, f"   ₹ {trade.get('CMP', 'N/A')}\n\n", "value")
        
        # Signal Section
        self.details_text.insert(tk.END, "📊 TRADE SIGNAL\n", "label")
        signal_text = trade.get('Trade Signals', 'N/A').strip()
        self.details_text.insert(tk.END, f"   {signal_text}\n\n", "value")
        
        # Performance Section
        self.details_text.insert(tk.END, "📈 PERFORMANCE RETURNS\n", "label")
        self.details_text.insert(tk.END, "─" * 45 + "\n")
        
        returns = {
            "1 Year   ": trade.get('1Y Return', 'N/A'),
            "6 Months ": trade.get('6M Return', 'N/A'),
            "1 Month  ": trade.get('1M Return', 'N/A'),
            "1 Week   ": trade.get('1W Return', 'N/A')
        }
        
        for label, value in returns.items():
            tag = "positive" if '+' in value else "negative"
            self.details_text.insert(tk.END, f"   {label} ", "label")
            self.details_text.insert(tk.END, f"{value}\n", tag)
        
        # Volatility Section
        self.details_text.insert(tk.END, "\n🎯 VOLATILITY METRICS\n", "label")
        self.details_text.insert(tk.END, "─" * 45 + "\n")
        self.details_text.insert(tk.END, f"   Avg Movement:   {trade.get('Avg Movement', 'N/A')}\n", "value")
        self.details_text.insert(tk.END, f"   10D Avg Move:   {trade.get('10D Avg Movement', 'N/A')}\n", "value")
        
        self.details_text.insert(tk.END, "\n" + "═" * 45 + "\n")
        self.details_text.insert(tk.END, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "label")
        
        self.details_text.config(state=tk.DISABLED)
    
    def run_screener_thread(self):
        """Run screener in background thread"""
        def run():
            self.screener_running = True
            self.run_btn.config(state=tk.DISABLED)
            self.status_indicator_text.config(text="● Running", fg=ModernStyle.WARNING)
            self.status_message.config(text="Executing screener...", fg=ModernStyle.WARNING)
            self.root.update()
            
            try:
                result = subprocess.run(
                    ['python', 'main.py'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                self.screener_running = False
                self.run_btn.config(state=tk.NORMAL)
                
                if result.returncode == 0:
                    self.status_indicator_text.config(text="● Ready", fg=ModernStyle.SUCCESS)
                    self.status_message.config(text="Screener completed successfully", fg=ModernStyle.SUCCESS)
                    self.update_trades_display()
                else:
                    self.status_indicator_text.config(text="● Error", fg=ModernStyle.DANGER)
                    self.status_message.config(text="Screener encountered an error", fg=ModernStyle.DANGER)
                    messagebox.showerror("Error", "Screener failed. Check console for details.")
            
            except subprocess.TimeoutExpired:
                self.screener_running = False
                self.run_btn.config(state=tk.NORMAL)
                self.status_indicator_text.config(text="● Timeout", fg=ModernStyle.DANGER)
                self.status_message.config(text="Screener timed out", fg=ModernStyle.DANGER)
                messagebox.showerror("Error", "Screener timed out (>5 minutes)")
            
            except Exception as e:
                self.screener_running = False
                self.run_btn.config(state=tk.NORMAL)
                self.status_indicator_text.config(text="● Error", fg=ModernStyle.DANGER)
                self.status_message.config(text="Error running screener", fg=ModernStyle.DANGER)
                messagebox.showerror("Error", f"Failed to run screener:\n{str(e)}")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def export_data(self):
        """Export current data"""
        results_file = self.get_latest_results_file()
        if results_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_name = f"Trades_Export_{timestamp}.csv"
            try:
                import shutil
                shutil.copy(results_file, export_name)
                messagebox.showinfo("Success", f"Data exported to:\n{export_name}")
                self.status_message.config(text=f"Exported to {export_name}", fg=ModernStyle.SUCCESS)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export:\n{str(e)}")
        else:
            messagebox.showwarning("Warning", "No data to export")
    
    def auto_refresh(self):
        """Auto-refresh real-time prices with dynamic interval"""
        if self.realtime_auto_update:
            self.fetch_live_prices()
        
        if self.running:
            self.root.after(self.refresh_interval, self.auto_refresh)  # Use dynamic interval
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    app = TradeSignalProfessionalGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
