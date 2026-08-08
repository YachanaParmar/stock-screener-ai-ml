import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def calculate_smma(prices, period):
    """Calculate Smoothed Moving Average (SMMA)"""
    if len(prices) < period:
        return None
    
    smma_values = []
    
    # First SMMA = Simple Moving Average
    first_sma = sum(prices[:period]) / period
    smma_values.append(first_sma)
    
    # Subsequent SMMA values
    for i in range(period, len(prices)):
        smma = (smma_values[-1] * (period - 1) + prices[i]) / period
        smma_values.append(smma)
    
    return smma_values[-1] if smma_values else None

def detect_crossover(prices):
    """Detect SMMA crossover signals"""
    if len(prices) < 121:
        return None, None
    
    # Calculate current and previous SMMA values
    smma20_current = calculate_smma(prices, 20)
    smma120_current = calculate_smma(prices, 120)
    
    smma20_prev = calculate_smma(prices[:-1], 20)
    smma120_prev = calculate_smma(prices[:-1], 120)
    
    if None in [smma20_current, smma120_current, 
                smma20_prev, smma120_prev]:
        return None, None
    
    signal = None
    
    # Buy signal - SMMA20 crosses above SMMA120
    if smma20_prev <= smma120_prev and smma20_current > smma120_current:
        signal = "BUY"
    
    # Sell signal - SMMA20 crosses below SMMA120
    elif smma20_prev >= smma120_prev and smma20_current < smma120_current:
        signal = "SELL"
    
    return signal, {
        "smma20": round(smma20_current, 2),
        "smma120": round(smma120_current, 2)
    }

def calculate_average_price(candle_data, minutes):
    """Calculate average LTP for last N minutes"""
    if not candle_data:
        return 0
    
    df = pd.DataFrame(candle_data, 
                      columns=['timestamp', 'open', 
                               'high', 'low', 
                               'close', 'volume'])
    
    candles_needed = minutes // 5
    recent = df.tail(candles_needed)
    
    if recent.empty:
        return 0
    
    return round(recent['close'].mean(), 2)

def calculate_traded_quantity(candle_data, minutes):
    """Calculate total quantity traded in last N minutes"""
    if not candle_data:
        return 0
    
    df = pd.DataFrame(candle_data,
                      columns=['timestamp', 'open',
                               'high', 'low',
                               'close', 'volume'])
    
    candles_needed = minutes // 5
    recent = df.tail(candles_needed)
    
    if recent.empty:
        return 0
    
    return int(recent['volume'].sum())