#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Concurrent Scalping Trading Algorithm for Alpaca API
Learn from: alpacahq/example-scalping (https://github.com/alpacahq/example-scalping)
Date: CURRENT_DATE
Description: Implements scalping strategy using SMA crossover with concurrency support.
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, List

import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream import Stream

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScalpingAlgo:
    def __init__(self, api_key: str, api_secret: str, base_url: str, symbols: List[str], lot: int = 2000):
        """
        Initialize scalping trading algorithm
        
        Args:
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            base_url: Alpaca API base URL
            symbols: List of symbols to trade
            lot: Dollar amount for each trade
        """
        self.api = tradeapi.REST(api_key, api_secret, base_url)
        self.stream = Stream(api_key, api_secret, base_url)
        self.symbols = symbols
        self.lot = lot
        self.sma_period = 20  # Simple Moving Average period
        self.data = {symbol: {'bars': [], 'last_price': 0} for symbol in symbols}
        self.position_entries = {}

    async def run(self):
        """Main execution method"""
        # Connect to Polygon stream
        await self.stream.connect()
        
        # Subscribe to minute bars and trades
        for symbol in self.symbols:
            self.stream.subscribe_minute_bars(self.on_minute_bar, symbol)
            self.stream.subscribe_trades(self.on_trade, symbol)
        
        # Start processing trades concurrently
        tasks = [self.process_trading(symbol) for symbol in self.symbols]
        await asyncio.gather(*tasks)

    async def on_minute_bar(self, bar):
        """Handle incoming minute bars"""
        symbol = bar.symbol
        self.data[symbol]['bars'].append(bar)
        
        # Keep SMA period worth of bars
        if len(self.data[symbol]['bars']) > self.sma_period:
            self.data[symbol]['bars'].pop(0)

    async def on_trade(self, trade):
        """Handle trade updates"""
        self.data[trade.symbol]['last_price'] = trade.price

    async def calculate_sma(self, symbol: str) -> float:
        """Calculate SMA for given symbol"""
        if len(self.data[symbol]['bars']) < self.sma_period:
            return 0
        
        return sum(bar.close for bar in self.data[symbol]['bars']) / self.sma_period

    async def process_trading(self, symbol: str):
        """Main trading logic for each symbol"""
        while True:
            sma = await self.calculate_sma(symbol)
            current_price = self.data[symbol]['last_price']
            
            if sma > 0 and current_price > sma and symbol not in self.position_entries:
                # Buy signal: SMA crossover occurred
                qty = int(self.lot / current_price)
                await self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='buy',
                    type='limit',
                    time_in_force='gtc',