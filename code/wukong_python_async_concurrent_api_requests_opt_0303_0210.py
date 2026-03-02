#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concurrent Scalping Trading Algorithm
学习来源: GitHub仓库 alpacahq/example-scalping
实现日期: 2023-10-30
功能描述: 基于Alpaca API的多股票并发短线交易策略，使用20分钟均线作为买入信号，快速进场出场
"""

import asyncio
import argparse
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.rest import TimeFrame

class ScalpingAlgo:
    def __init__(self, api, symbols, lot_size):
        self.api = api
        self.symbols = symbols
        self.lot_size = lot_size  # 每笔交易金额
        self.positions = {}  # 跟踪各股票的持仓状态
        self.stream = Stream(api.key_id, api.secret_key, base_url=api._base_url)
    
    async def run(self):
        # 启动流数据监听
        await self.stream.connect()
        
        # 订阅分钟K线和订单更新
        for symbol in self.symbols:
            self.positions[symbol] = {
                'holding': False, 
                'buy_order_id': None,
                'entry_price': None
            }
            await self.stream.subscribe_bars([symbol], self.on_minute_bar)
            await self.stream.subscribe_trade_updates(self.on_order_update)
        
        # 主循环保持运行
        while True:
            await asyncio.sleep(1)
    
    async def on_minute_bar(self, bar):
        """处理分钟K线数据，生成交易信号"""
        symbol = bar.symbol
        if self.positions[symbol]['holding']:
            return  # 已有持仓则忽略
        
        # 获取最近20分钟K线计算SMA
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=20)
        bars = self.api.get_bars(symbol, TimeFrame.Minute, start_time.isoformat(), end_time.isoformat())
        
        if len(bars) < 20:
            return  # 数据不足
            
        closes = [bar.c for bar in bars]
        sma = sum(closes) / len(closes)
        
        # 当前价格高于SMA时买入
        if bar.close > sma and not self.positions[symbol]['holding']:
            await self.place_buy_order(symbol, bar.close)
    
    async def place_buy_order(self, symbol, price):
        """下达买入订单"""
        qty = int(self.lot_size / price)  # 计算购买数量
        order = self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='limit',
            time_in_force='gtc',
            limit_price=price
        )
        
        self.positions[symbol]['buy_order_id'] = order.id
        print(f"买入订单提交: {symbol} {qty}股 @ {price}")
        
        # 2分钟后取消未成交订单
        asyncio.create_task(self.cancel_order_after_delay(order.id, symbol, 120))
    
    async def cancel_order_after_delay(self, order_id, symbol, delay):
        """延迟取消订单"""
        await asyncio.sleep(delay)
        try:
            order = self.api.get_order(order_id)
            if order.status == 'new' or order.status == 'partially_filled':
                self.api.cancel_order(order_id)
                print(f"取消未成交订单: {symbol}")
        except Exception as e:
            print(f"取消订单