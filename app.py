import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from config import *
from models import StockDatabase

st.set_page_config(**PAGE_CONFIG)
db = StockDatabase(DB_PATH)

st.title("📈 Stock Market Dashboard")

page = st.sidebar.radio("Menu", ["Dashboard", "Watchlist", "Portfolio", "Settings"])

@st.cache_data(ttl=3600)
def get_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    try:
        return yf.download(ticker, period=period, progress=False)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_current_price(ticker: str) -> float:
    try:
        data = yf.download(ticker, period='1d', progress=False)
        return float(data['Close'].iloc[-1])
    except:
        return None

if page == "Dashboard":
    st.subheader("📊 View Stocks")
    ticker = st.selectbox("Select Stock:", POPULAR_STOCKS)
    period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y"])
    
    df = get_stock_data(ticker, period)
    if not df.empty:
        price = float(df['Close'].iloc[-1])
        st.metric(f"{ticker} Price", f"${price:.2f}")
        
        # Simple candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])
        fig.update_layout(title=f"{ticker} Price Chart", xaxis_title="Date", yaxis_title="Price", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("⭐ Add to Watchlist"):
            if db.add_to_watchlist(ticker, ticker):
                st.success(f"✅ Added {ticker}!")
            else:
                st.info(f"{ticker} already in watchlist")

elif page == "Watchlist":
    st.subheader("⭐ Your Watchlist")
    watchlist = db.get_watchlist()
    
    if watchlist:
        for item in watchlist:
            col1, col2 = st.columns([3, 1])
            ticker = item['ticker']
            price = get_current_price(ticker)
            
            with col1:
                if price:
                    st.write(f"**{ticker}** - ${price:.2f}")
            
            with col2:
                if st.button("❌", key=f"remove_{ticker}"):
                    db.remove_from_watchlist(ticker)
                    st.rerun()
    else:
        st.info("📭 Empty. Add stocks from Dashboard!")

elif page == "Portfolio":
    st.subheader("💼 Portfolio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Add Transaction**")
        ticker = st.text_input("Ticker:", "AAPL").upper()
        qty = st.number_input("Quantity:", min_value=0.01, value=1.0)
        price = st.number_input("Price:", min_value=0.01, value=150.0)
        trans = st.radio("Type:", ["BUY", "SELL"])
        
        if st.button("Add Transaction"):
            db.add_portfolio_transaction(ticker, qty, price, trans)
            st.success(f"✅ Added {trans} transaction!")
    
    with col2:
        st.write("**Your Holdings**")
        portfolio = db.get_portfolio()
        if portfolio:
            for holding in portfolio:
                t = holding['ticker']
                q = float(holding['total_qty'])
                ac = float(holding['avg_cost'])
                cp = get_current_price(t)
                if cp:
                    gain = (cp - ac) * q
                    pct = (gain / (ac * q) * 100) if ac * q > 0 else 0
                    st.write(f"**{t}**: {q:.2f} @ ${ac:.2f}")
                    st.write(f"Value: ${cp * q:.2f} | Gain: ${gain:.2f} ({pct:.1f}%)")
        else:
            st.info("No holdings yet!")

elif page == "Settings":
    st.subheader("⚙️ Settings")
    st.write("""
    **Stock Market Dashboard** - Real-time stock tracking
    
    ✅ Features:
    - Live stock prices
    - Watchlist management
    - Portfolio tracking
    - Buy/Sell transactions
    
    📊 Data source: yfinance
    """)
