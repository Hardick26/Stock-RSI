"""
Real-time Stock Data Fetcher
Fetches live stock prices and updates from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import threading
import time

class RealTimeStockData:
    """Manages real-time stock data fetching and caching"""
    
    def __init__(self):
        self.cache = {}
        self.update_lock = threading.Lock()
        self.is_fetching = False
        self.last_update = {}
    
    def get_live_price(self, stock_symbol, retries=2):
        """
        Get current live price for a stock
        
        Args:
            stock_symbol: Stock ticker (e.g., 'TCS')
            retries: Number of retry attempts
            
        Returns:
            dict with keys: price, change, change_pct, last_update
        """
        try:
            ticker = yf.Ticker(f"{stock_symbol}.NS")
            data = ticker.history(period='1d')
            
            if data.empty:
                return {
                    'price': 'N/A',
                    'change': 'N/A',
                    'change_pct': 'N/A',
                    'volume': 'N/A',
                    'high': 'N/A',
                    'low': 'N/A',
                    'last_update': datetime.now().strftime('%H:%M:%S')
                }
            
            # Get current and previous close
            current = data['Close'].iloc[-1]
            
            # Get previous day data if available
            history = ticker.history(period='5d')
            if len(history) >= 2:
                previous_close = history['Close'].iloc[-2]
                change = current - previous_close
                change_pct = (change / previous_close) * 100 if previous_close != 0 else 0
            else:
                change = 0
                change_pct = 0
            
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            volume = data['Volume'].iloc[-1] if 'Volume' in data.columns else 0
            
            with self.update_lock:
                self.cache[stock_symbol] = {
                    'price': f"₹{current:.2f}",
                    'change': f"{change:+.2f}",
                    'change_pct': f"{change_pct:+.2f}%",
                    'high': f"₹{high:.2f}",
                    'low': f"₹{low:.2f}",
                    'volume': f"{volume/1e6:.1f}M" if volume > 0 else "N/A",
                    'last_update': datetime.now().strftime('%H:%M:%S')
                }
            
            return self.cache[stock_symbol]
        
        except Exception as e:
            print(f"Error fetching data for {stock_symbol}: {e}")
            return {
                'price': 'Error',
                'change': 'N/A',
                'change_pct': 'N/A',
                'volume': 'N/A',
                'high': 'N/A',
                'low': 'N/A',
                'last_update': datetime.now().strftime('%H:%M:%S')
            }
    
    def get_cached_price(self, stock_symbol):
        """Get cached price without fetching"""
        with self.update_lock:
            return self.cache.get(stock_symbol, {})
    
    def batch_fetch(self, stock_symbols, callback=None):
        """
        Fetch data for multiple stocks
        
        Args:
            stock_symbols: List of stock tickers
            callback: Function to call with progress (stock, index, total)
        """
        total = len(stock_symbols)
        for idx, symbol in enumerate(stock_symbols):
            self.get_live_price(symbol)
            if callback:
                callback(symbol, idx + 1, total)
            time.sleep(0.2)  # Rate limiting to avoid overwhelming API
    
    def start_background_fetch(self, stock_symbols, interval=30):
        """
        Start background thread for continuous price updates
        
        Args:
            stock_symbols: List of stock tickers to monitor
            interval: Update interval in seconds
        """
        def background_fetch():
            while self.is_fetching:
                self.batch_fetch(stock_symbols)
                time.sleep(interval)
        
        self.is_fetching = True
        thread = threading.Thread(target=background_fetch, daemon=True)
        thread.start()
    
    def stop_background_fetch(self):
        """Stop background fetching"""
        self.is_fetching = False

# Global instance
real_time_data = RealTimeStockData()
