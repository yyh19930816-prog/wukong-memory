#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concurrent Scalping Algorithm Implementation
Learned from: alpacahq/example-scalping (https://github.com/alpacahq/example-scalping)
Date: 2023-11-15
Description: Implements a concurrent scalping strategy using Alpaca API and Polygon websockets.
             Buys stocks on 20-minute SMA crossover and quickly exits positions for small gains.
"""

import asyncio
import argparse
import logging
from alpaca_trade_api import tradeapi
from alpaca_trade_api.stream import Stream

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScalpingStrategy:
    def __init__(self, api_key, api_secret, symbols, lot_size):
        """Initialize scalping strategy with Alpaca credentials"""
        self.api = tradeapi.REST(api_key, api_secret, base_url='https://paper-api.alpaca.markets')
        self.stream = Stream(api_key, api_secret, base_url='wss://paper-api.alpaca.markets')
        self.symbols = symbols
        self.lot_size = lot_size
        self.sma_windows = 20  # SMA window size in minutes
        self.bars_data = {symbol: [] for symbol in symbols}
        self.positions = {symbol: None for symbol in symbols}

    async def on_minute_bar(self, bar):
        """Handle incoming minute bar data"""
        symbol = bar.symbol
        self.bars_data[symbol].append(bar.close)
        
        # Keep only SMA window size of bars
        if len(self.bars_data[symbol]) > self.sma_windows:
            self.bars_data[symbol] = self.bars_data[symbol][-self.sma_windows:]
            
        # Only trade if we have enough data
        if len(self.bars_data[symbol]) == self.sma_windows:
            await self.check_buy_signal(symbol)

    async def check_buy_signal(self, symbol):
        """Check SMA crossover buy signal"""
        if self.positions[symbol] is not None:
            return  # Already in position
            
        prices = self.bars_data[symbol]
        sma = sum(prices) / len(prices)
        current_price = prices[-1]
        
        # Simple SMA crossover strategy
        if current_price > sma:
            await self.enter_position(symbol, current_price)

    async def enter_position(self, symbol, price):
        """Enter a new position"""
        try:
            # Calculate share quantity based on lot size
            qty = int(self.lot_size / price)
            if qty < 1:
                return
                
            # Place buy order
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='limit',
                limit_price=price,
                time_in_force='gtc'
            )
            
            logger.info(f"Buy order placed for {symbol}: {qty} shares @ {price}")
            self.positions[symbol] = {'entry_price': price, 'order_id': order.id}
            
            # Schedule order cancellation and monitoring
            asyncio.create_task(self.monitor_position(symbol))
            
        except Exception as e:
            logger.error(f"Error entering position for {symbol}: {str(e)}")

    async def monitor_position(self, symbol):
        """Monitor position and attempt to exit"""
        await asyncio.sleep(120)  # Wait 2 minutes