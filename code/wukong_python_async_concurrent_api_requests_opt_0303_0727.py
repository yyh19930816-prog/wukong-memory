#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习来源: GitHub仓库 alpacahq/example-scalping
创建日期: 2023-10-25
功能描述: 基于Alpaca API的短线交易算法，使用20分钟移动平均线交叉作为买入信号，
         并在买入后立即挂单平仓，实现快速交易策略（Scalping）。
         支持同时监控多只股票，使用asyncio实现并发处理。
"""

import asyncio
import argparse
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.rest import TimeFrame

class ScalpingAlgo:
    def __init__(self, api_key, secret_key, base_url, symbols, lot_size):
        self.api = tradeapi.REST(api_key, secret_key, base_url)
        self.stream = Stream(api_key, secret_key, base_url)
        self.symbols = symbols
        self.lot_size = lot_size
        # 存储每只股票的状态
        self.stock_data = {symbol: {
            'position': None,
            'buy_order': None,
            'sell_order': None,
            'bars': []
        } for symbol in symbols}

    async def run(self):
        """主运行方法，启动多个协程处理不同股票"""
        # 订阅聚合市场数据和订单更新
        await self.stream.subscribe_trade_updates(self.on_order_update)
        await self.stream.subscribe_bars(self.symbols, self.on_bar_update)
        
        # 启动异步任务
        tasks = [
            asyncio.create_task(self.stream._run_forever()),
            *[self.monitor_symbol(symbol) for symbol in self.symbols]
        ]
        await asyncio.gather(*tasks)

    async def monitor_symbol(self, symbol):
        """监控单个股票的交易信号"""
        while True:
            await asyncio.sleep(60)  # 每分钟检查一次
            
            # 获取最新20分钟K线
            bars = self.api.get_bars(symbol, TimeFrame.Minute, limit=20).df
            if len(bars) < 20:
                continue
            
            # 计算20SMA
            sma = bars['close'].mean()
            last_close = bars['close'].iloc[-1]
            
            # 生成买入信号: 收盘价上穿20SMA
            if last_close > sma and not self.stock_data[symbol]['buy_order']:
                await self.place_buy_order(symbol)

    async def place_buy_order(self, symbol):
        """下达买入订单"""
        qty = int(self.lot_size / self.api.get_latest_trade(symbol).price)
        order = self.api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        self.stock_data[symbol]['buy_order'] = order
        print(f"Placed buy order for {symbol}")

    async def place_sell_order(self, symbol):
        """下达卖出订单"""
        position = self.api.get_position(symbol)
        last_price = self.api.get_latest_trade(symbol).price
        limit_price = max(float(position.avg_entry_price), last_price)
        
        order = self.api.submit_order(
            symbol=symbol,
            qty=position.qty,
            side='sell',
            type='limit',
            time_in_force='gtc',
            limit_price=limit_price
        )
        self.stock_data[symbol]['sell_order'] = order
        print(f"Placed sell order for