#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# TradeWiSE Project
#
# This file is part of the TradeWiSE project, an automated trading and financial analysis platform.
# It is licensed under the Mozilla Public License 2.0 (MPL 2.0), which allows for wide use and modification
# while ensuring that enhancements and modifications remain available to the community.
#
# You can find the MPL 2.0 license in the root directory of the project or at https://www.mozilla.org/MPL/2.0/.
#
# Copyright (c) 2023 by wildfootw <wildfootw@wildfoo.tw>
#

import logging
import os

from fastapi import FastAPI
from fugle_marketdata import RestClient


def get_env_or_raise(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise ValueError(f'Environment variable "{name}" not set')
    return value

fugle_marketdata_api_key = get_env_or_raise('FUGLE_MARKET_DATA_API_KEY')

app = FastAPI()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_stock_price(symbol: str):
    client = RestClient(api_key=fugle_marketdata_api_key)
    data = client.stock.intraday.quote(symbol=symbol)

    if not isinstance(data, dict):
        logging.error(f"Unexpected response: {data}")
        return {'error': repr(data)}

    if (status_code := data.get("statusCode")) and status_code != 200:
        logging.error(f"Failed to get stock price: {data.get('message')}")
        return {'error': data.get('message')}

    # Extracting specific data from the response
    price_data = {
        "symbol":        symbol,
        "name":          data['name'],
        "lastPrice":     data['lastPrice'],
        "openPrice":     data['openPrice'],
        "highPrice":     data['highPrice'],
        "lowPrice":      data['lowPrice'],
        "closePrice":    data['closePrice'],
        "change":        data['change'],
        "changePercent": data['changePercent']
    }
    return price_data

@app.get("/price/{symbol}")
async def read_price(symbol: str):
    return get_stock_price(symbol)
