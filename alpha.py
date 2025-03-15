# filepath: f:\gemma and MT5\mt5.py
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.io as pio
from plotly.subplots import make_subplots
import numpy as np
from alpha_vantage.timeseries import TimeSeries # Import the TimeSeries class

# Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = 'BDPVFEYI8YL2VE2B'

def get_symbol_data(symbol, interval, outputsize='compact'):
    ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
    try:
        if interval == 'M5':
            data, meta_data = ts.get_intraday(symbol=symbol, interval='5min', outputsize=outputsize)
        elif interval == 'H1':
            data, meta_data = ts.get_intraday(symbol=symbol, interval='60min', outputsize=outputsize)
        elif interval == 'D1':
            data, meta_data = ts.get_daily(symbol=symbol, outputsize=outputsize)
        else:
            raise ValueError("Invalid interval. Choose from 'M5', 'H1', or 'D1'.")
        
        data.reset_index(inplace=True)
        data.rename(columns={
            'date': 'time',
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close',
            '5. volume': 'volume'
        }, inplace=True)
        return data
    except ValueError as e:
        st.error(f"Error fetching data: {e}")
        return None

def calculate_rsi(data, periods=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def plot_symbol_data(df, symbol, timeframe):
    if df is None:
        st.error("No data to display.")
        return

    # Calculate moving averages and RSI
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    df['RSI'] = calculate_rsi(df)

    # Create subplots with secondary y-axis for RSI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.7, 0.3])

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        ), row=1, col=1
    )

    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df['MA20'],
            line=dict(color='yellow', width=1),
            name='20 MA'
        ), row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df['MA50'],
            line=dict(color='orange', width=1),
            name='50 MA'
        ), row=1, col=1
    )

    # Calculate and add support/resistance
    resistance = df['high'].rolling(window=20).max()
    support = df['low'].rolling(window=20).min()

    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=resistance,
            line=dict(color='red', width=1, dash='dash'),
            name='Resistance'
        ), row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=support,
            line=dict(color='green', width=1, dash='dash'),
            name='Support'
        ), row=1, col=1
    )

    # Add RSI
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df['RSI'],
            line=dict(color='purple', width=1),
            name='RSI'
        ), row=2, col=1
    )

    # Add RSI overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # Update layout
    fig.update_layout(
        title=f'{symbol} Candlestick Chart ({timeframe})',
        yaxis_title='Price',
        yaxis2_title='RSI',
        xaxis_title='Time',
        template='plotly_dark',
        height=800,  # Increased height to accommodate RSI
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.5)"
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Rockwell"
        )
    )

    # Update RSI subplot
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)

    return st.plotly_chart(fig, use_container_width=True)