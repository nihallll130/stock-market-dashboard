import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import talib
from config import *
from models import StockDatabase

st.set_page_config(**PAGE_CONFIG)
db = StockDatabase(DB_PATH)

st.title("📈 Stock Market Dashboard")

page = st.sidebar.radio("Menu", ["Dashboard", "Watchlist", "Portfolio", "Alerts", "Settings"])

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
    period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y", "5y"])
    
    df = get_stock_data(ticker, period)
    if not df.empty:
        price = float(df['Close'].iloc[-1])
        st.metric(f"{ticker} Price", f"${price:.2f}")
        
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
    
    ticker = st.text_input("Ticker:", "AAPL").upper()
    qty = st.number_input("Quantity:", min_value=0.01, value=1.0)
    price = st.number_input("Price:", min_value=0.01, value=150.0)
    trans = st.radio("Type:", ["BUY", "SELL"])
    
    if st.button("Add Transaction"):
        db.add_portfolio_transaction(ticker, qty, price, trans)
        st.success(f"✅ Added {trans} transaction!")
    
    portfolio = db.get_portfolio()
    if portfolio:
        for holding in portfolio:
            t = holding['ticker']
            q = float(holding['total_qty'])
            cp = get_current_price(t)
            if cp:
                st.write(f"**{t}**: {q:.2f} shares @ ${cp:.2f}")

elif page == "Alerts":
    st.subheader("🔔 Alerts")
    
    ticker = st.text_input("Ticker:", "AAPL").upper()
    alert_type = st.selectbox("Type:", ALERT_TYPES)
    threshold = st.number_input("Threshold (%):", value=5.0)
    
    if st.button("Create Alert"):
        if db.add_alert(ticker, alert_type, threshold):
            st.success("✅ Alert created!")
    
    alerts = db.get_alerts()
    if alerts:
        for alert in alerts:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{alert['ticker']}** - {alert['alert_type']}")
            with col2:
                if st.button("❌", key=f"del_{alert['id']}"):
                    db.remove_alert(alert['id'])
                    st.rerun()

elif page == "Settings":
    st.subheader("⚙️ Settings")
    st.info("✅ App is running locally. Data saved to SQLite.")
