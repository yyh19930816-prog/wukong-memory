#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concurrent Scalping Trading Algorithm

学习来源：github.com/alpacahq/example-scalping
实现日期：2023-04-01
功能描述：基于Alpaca API的多股票并发头皮交易策略，使用20分钟均线交叉作为买入信号，
         快速进出头寸，适用于流动性好的股票。

注意：需要25,000美元以上账户资金（PDT规则），并且市场开盘21分钟后才开始交易。
"""

import asyncio
import argparse
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream import Stream

class ScalpingAlgo:
    def __init__(self, api, symbols, lot_size):
        self.api = api
        self.symbols = symbols
        self.lot_size = lot_size
        self.position_data = {symbol: {'bars': [], 'order': None} 
                             for symbol in symbols}
        self.stream = Stream(api.key, api.secret, base_url=api.base_url, 
                            data_stream='polygon')

    async def run(self):
        """启动算法主循环"""
        # 订阅实时分钟Bar数据
        await self.stream.subscribe_bars(self.on_minute_bar, *self.symbols)
        
        # 订阅订单更新
        await self.stream.subscribe_trade_updates(self.on_order_update)

        print(f"Started scalping algo for {self.symbols} with lot ${self.lot_size}")
        await self.stream.run()

    async def on_minute_bar(self, bar):
        """每分钟Bar数据回调"""
        symbol = bar.symbol
        data = self.position_data[symbol]
        data['bars'].append(bar.close)
        
        # 只保留最近20分钟的Bar数据
        if len(data['bars']) > 20:
            data['bars'].pop(0)
        
        # 检查是否满足交易条件（至少20个数据点）
        if len(data['bars']) == 20:
            await self.check_signal(symbol)

    async def check_signal(self, symbol):
        """检查20分钟均线信号"""
        closes = self.position_data[symbol]['bars']
        ma = sum(closes) / len(closes)
        last_close = closes[-1]
        
        # 当前价格上穿20分钟均线且没有挂单时买入
        if last_close > ma and not self.position_data[symbol]['order']:
            await self.submit_buy_order(symbol, last_close)

    async def submit_buy_order(self, symbol, price):
        """提交买入订单"""
        try:
            # 计算购买的股票数量(以lot_size美元为单位)
            qty = int(self.lot_size // price)
            if qty < 1:
                return
                
            print(f"Submitting buy order for {symbol} at {price}")
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='limit',
                time_in_force='gtc',
                limit_price=price
            )
            self.position_data[symbol]['order'] = order
            
            # 2分钟后取消未成交的订单
            await asyncio.sleep(120)
            if not order.filled_at:
                self.api.cancel_order(order.id)
                print(f"Cancelled unfilled order for {symbol}")
                self.position_data[symbol]['order'] = None
                
        except Exception as e:
            print(f"Error submitting buy order for {symbol}: {e}")

    async def on_order_update(self, order):
        """订单状态更新回调"""
        symbol = order.symbol
        if order.event == 'fill