# -*- coding: utf-8 -*-
"""
Concurrent Scalping Trading Algorithm for Alpaca API
Learn from: alpacahq/example-scalping (https://github.com/alpacahq/example-scalping)
Date: 2023-11-15
Function: Implements concurrent scalping strategy for multiple stocks using SMA crossover signals
          and real-time order updates via Alpaca API and Polygon websockets.
"""

import asyncio
import argparse
from alpaca_trade_api import StreamConn
from alpaca_trade_api.common import URL
from alpaca_trade_api.rest import REST, TimeFrame

class ScalpingAlgo:
    def __init__(self, api_key, api_secret, base_url, symbols, lot_size):
        self.api = REST(api_key, api_secret, base_url, api_version='v2')
        self.conn = StreamConn(api_key, api_secret, base_url)
        self.symbols = symbols
        self.lot_size = lot_size
        self.positions = {}

    async def handle_minute_bar(self, conn, channel, bar):
        """Handle incoming minute bar data and check for SMA crossover"""
        symbol = bar.symbol
        print(f"New bar for {symbol}: {bar.close}")

        # Get historical data for SMA calculation
        historical = self.api.get_bars(symbol, TimeFrame.Minute, limit=20).df
        if len(historical) < 20:
            return

        sma_20 = historical['close'].mean()
        current_price = bar.close

        if current_price > sma_20 and symbol not in self.positions:
            # Buy signal: SMA crossover up
            await self.create_buy_order(symbol, current_price)

    async def create_buy_order(self, symbol, price):
        """Create limit buy order for the given symbol"""
        try:
            # Calculate share quantity based on lot size
            qty = int(self.lot_size / price)
            if qty < 1:
                return
                
            print(f"Buy signal for {symbol} at {price:.2f}")
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='limit',
                limit_price=price,
                time_in_force='day'
            )
            self.positions[symbol] = order.id
            print(f"Buy order submitted for {symbol}: {order.id}")
            
            # Schedule order cancellation if not filled in 2 minutes
            asyncio.create_task(self.cancel_unfilled_order(order.id, symbol, 120))
            
        except Exception as e:
            print(f"Error submitting buy order for {symbol}: {e}")

    async def cancel_unfilled_order(self, order_id, symbol, delay):
        """Cancel order if not filled after delay seconds"""
        await asyncio.sleep(delay)
        try:
            order = self.api.get_order(order_id)
            if order.status != 'filled':
                self.api.cancel_order(order_id)
                print(f"Cancelled unfilled order for {symbol}")
                if symbol in self.positions:
                    del self.positions[symbol]
        except Exception as e:
            print(f"Error cancelling order {order_id}: {e}")

    async def handle_order_update(self, conn, channel, event):
        """Handle order fill events and create sell orders"""
        if event.event == 'fill' and event.order['symbol'] in self.positions:
            symbol = event.order['symbol']
            if event.order['side'] == 'buy':
                # Buy order filled, create sell order
                qty = event.order['filled_qty']
                price = float(event.order['price'])
                try: