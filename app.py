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

def get_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Fetch stock data from yfinance"""
    try:
        df = yf.download(ticker, period=period, progress=False)
        if df.empty:
            return pd.DataFrame()
        return df
    except Exception as e:
        return pd.DataFrame()

def get_current_price(ticker: str) -> float:
    """Get current stock price"""
    try:
        data = yf.download(ticker, period='5d', progress=False)
        if data.empty:
            return None
        close_val = data['Close'].iloc[-1]
        return float(close_val)
    except:
        return None

if page == "Dashboard":
    st.subheader("📊 View Stocks")
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.selectbox("Select Stock:", POPULAR_STOCKS)
    with col2:
        period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y"])
    
    if st.button("Load Stock Data"):
        with st.spinner(f"Fetching {ticker} data..."):
            df = get_stock_data(ticker, period)
            
            if not df.empty:
                try:
                    latest_close = df['Close'].iloc[-1]
                    
                    if hasattr(latest_close, 'item'):
                        price = float(latest_close.item())
                    else:
                        price = float(latest_close)
                    
                    if price > 0:
                        st.metric(f"{ticker} Latest Price", f"${price:.2f}")
                        
                        fig = go.Figure(data=[go.Candlestick(
                            x=df.index,
                            open=df['Open'],
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close']
                        )])
                        fig.update_layout(
                            title=f"{ticker} - {period}",
                            xaxis_title="Date",
                            yaxis_title="Price ($)",
                            height=500
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        if st.button(f"⭐ Add {ticker} to Watchlist"):
                            if db.add_to_watchlist(ticker, ticker):
                                st.success(f"✅ Added {ticker}!")
                            else:
                                st.info(f"{ticker} already in watchlist")
                    else:
                        st.error("❌ Invalid price data")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.error(f"❌ Could not fetch data for {ticker}")

elif page == "Watchlist":
    st.subheader("⭐ Your Watchlist")
    watchlist = db.get_watchlist()
    
    if watchlist:
        for item in watchlist:
            col1, col2, col3 = st.columns([2, 1, 1])
            ticker = item['ticker']
            price = get_current_price(ticker)
            
            with col1:
                if price:
                    st.write(f"**{ticker}** - ${price:.2f}")
                else:
                    st.write(f"**{ticker}** - Data unavailable")
            
            with col2:
                if st.button("View", key=f"view_{ticker}"):
                    st.info(f"View {ticker} from Dashboard")
            
            with col3:
                if st.button("❌", key=f"remove_{ticker}"):
                    db.remove_from_watchlist(ticker)
                    st.rerun()
    else:
        st.info("No stocks in watchlist. Add from Dashboard!")

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
            st.success(f"✅ {trans} transaction added!")
    
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
                    value = cp * q
                    gain = value - (ac * q)
                    pct = (gain / (ac * q) * 100) if ac * q > 0 else 0
                    
                    st.write(f"**{t}**")
                    st.write(f"Qty: {q:.2f} | Cost: ${ac:.2f}")
                    st.write(f"Value: ${value:.2f} | Gain: ${gain:.2f} ({pct:.1f}%)")
                    st.divider()
        else:
            st.info("No holdings yet!")

elif page == "Settings":
    st.subheader("⚙️ Settings")
    st.info("""
    **Stock Market Dashboard**
    
    ✅ Real-time stock tracking
    ✅ Watchlist management
    ✅ Portfolio tracking
    
    📊 Data: yfinance
    💾 Storage: SQLite
    """)
   
