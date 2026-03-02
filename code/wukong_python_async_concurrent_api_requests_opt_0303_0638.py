#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Concurrent Scalping Trading Algorithm based on Alpaca API
Learned from: https://github.com/alpacahq/example-scalping
Date: 2023-11-15
Description: Implements concurrent scalping strategy using SMA crossover signals
             for multiple stocks, with real-time order updates via Alpaca API.
"""

import asyncio
import logging
import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream import Stream
from datetime import datetime, timedelta
import argparse

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

class Scalper:
    def __init__(self, api, symbol, lot_size):
        """Initialize scalping strategy for a single symbol"""
        self.api = api
        self.symbol = symbol
        self.lot_size = lot_size
        self.position = None
        self.sma_window = 20  # 20-minute SMA window
        self.prices = []  # Track recent prices for SMA calculation
        
    async def on_minute_bar(self, bar):
        """Handle incoming minute bar data"""
        logger.info(f"Received bar for {self.symbol}: {bar}")
        
        # Add latest close price to the window
        self.prices.append(bar.close)
        if len(self.prices) > self.sma_window:
            self.prices.pop(0)
            
        # Only trade if we have enough data points
        if len(self.prices) < self.sma_window:
            return
            
        # Calculate SMA
        sma = sum(self.prices) / len(self.prices)
        logger.info(f"{self.symbol} SMA: {sma:.2f}, Current: {bar.close:.2f}")
        
        # Buy signal: current price crosses above SMA
        if bar.close > sma and not self.position:
            await self.place_buy_order(bar.close)
            
    async def place_buy_order(self, price):
        """Place buy order for the symbol"""
        try:
            # Calculate quantity based on lot size
            quantity = int(self.lot_size / price)
            logger.info(f"Buy signal for {self.symbol}, buying {quantity} @ {price:.2f}")
            
            # Submit limit order
            order = self.api.submit_order(
                symbol=self.symbol,
                qty=quantity,
                side='buy',
                type='limit',
                time_in_force='day',
                limit_price=price
            )
            
            # Track the order
            self.position = {
                'order_id': order.id,
                'entry_price': price,
                'quantity': quantity,
                'expires': datetime.now() + timedelta(minutes=2)
            }
            logger.info(f"Buy order placed for {self.symbol}: {order}")
            
        except Exception as e:
            logger.error(f"Error placing buy order for {self.symbol}: {e}")

async def main():
    """Main async function to handle multiple symbols concurrently"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--lot', type=int, required=True, 
                       help='Lot size in dollar amount per trade')
    parser.add_argument('symbols', nargs='+', help='List of symbols to trade')
    args = parser.parse_args()
    
    # Initialize Alpaca API
    api = tradeapi.REST()
    stream = Stream()
    
    # Create scalper instances for each symbol
    scalpers = [Scalper(api, symbol, args.lot) for symbol in args