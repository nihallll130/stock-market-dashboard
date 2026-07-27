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

@st.cache_data(ttl=300)
def get_stock_data(ticker: str, period: str = "1y"):
    """Fetch stock data from yfinance"""
    try:
        df = yf.download(ticker, period=period, progress=False)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def get_current_price(ticker: str):
    """Get current stock price"""
    try:
        data = yf.download(ticker, period='5d', progress=False)
        if data is not None and not data.empty:
            return float(data['Close'].iloc[-1])
        return None
    except:
        return None

if page == "Dashboard":
    st.subheader("📊 View Stocks")
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.selectbox("Select Stock:", POPULAR_STOCKS)
    with col2:
        period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y"])
    
    if st.button("📊 Load Stock Data"):
        with st.spinner(f"Fetching {ticker} data..."):
            df = get_stock_data(ticker, period)
            
            if df is not None and not df.empty:
                try:
                    # Remove NaN values
                    df_clean = df.dropna()
                    
                    if len(df_clean) > 0:
                        # Get latest close price
                        latest_close = df_clean['Close'].iloc[-1]
                        latest_price = float(latest_close)
                        
                        # Display price
                        st.metric(f"💰 {ticker} Price", f"${latest_price:.2f}")
                        
                        # Candlestick chart
                        fig = go.Figure(data=[go.Candlestick(
                            x=df.index,
                            open=df['Open'],
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close'],
                            name=ticker
                        )])
                        fig.update_layout(
                            title=f"{ticker} - {period}",
                            yaxis_title='Price (USD)',
                            xaxis_title='Date',
                            height=500
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Add to watchlist button
                        if st.button(f"⭐ Add {ticker} to Watchlist"):
                            if db.add_to_watchlist(ticker, ticker):
                                st.success(f"✅ Added {ticker}!")
                            else:
                                st.info(f"{ticker} already in watchlist")
                    else:
                        st.error("❌ No valid price data found")
                
                except ValueError as e:
                    st.error(f"❌ Data Error: {e}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.error(f"❌ Could not fetch data for {ticker}")
                st.info("Try selecting a different stock or wait a moment")

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
                    st.write(f"**{ticker}** - N/A")
            
            with col2:
                st.text("")
            
            with col3:
                if st.button("❌", key=f"remove_{ticker}"):
                    db.remove_from_watchlist(ticker)
                    st.rerun()
    else:
        st.info("No stocks in watchlist")

elif page == "Portfolio":
    st.subheader("💼 Portfolio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Add Transaction**")
        ticker = st.text_input("Ticker:", "AAPL").upper()
        qty = st.number_input("Quantity:", min_value=0.01, value=1.0)
        price_input = st.number_input("Price per share:", min_value=0.01, value=150.0)
        trans_type = st.radio("Type:", ["BUY", "SELL"])
        
        if st.button("Add Transaction"):
            db.add_portfolio_transaction(ticker, qty, price_input, trans_type)
            st.success(f"✅ {trans_type} added!")
    
    with col2:
        st.write("**Holdings**")
        portfolio = db.get_portfolio()
        if portfolio:
            for holding in portfolio:
                ticker = holding['ticker']
                qty = float(holding['total_qty'])
                avg_cost = float(holding['avg_cost'])
                current_price = get_current_price(ticker)
                
                if current_price:
                    value = qty * current_price
                    gain_loss = value - (qty * avg_cost)
                    pct = (gain_loss / (qty * avg_cost) * 100) if avg_cost > 0 else 0
                    
                    st.write(f"**{ticker}**")
                    st.write(f"Qty: {qty:.2f} | Value: ${value:.2f}")
                    st.write(f"Gain/Loss: ${gain_loss:.2f} ({pct:.1f}%)")
                    st.divider()
        else:
            st.info("No holdings")

elif page == "Settings":
    st.subheader("⚙️ Settings")
    st.write("""
    **Stock Market Dashboard**
    
    Features:
    - Real-time stock prices
    - Watchlist tracking
    - Portfolio management
    - Interactive charts
    
    Data: yfinance
    """)
