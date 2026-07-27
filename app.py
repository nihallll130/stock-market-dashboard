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
                    # Get latest price - handle Series properly
                    latest_close = df['Close'].iloc[-1]
                    
                    # Convert to scalar if it's a Series
                    if hasattr(latest_close, 'item'):
                        price = float(latest_close.item())
                    else:
                        price = float(latest_close)
                    
                    # Check if price is valid
                    if price > 0:
                        st.metric(f"{ticker} Latest Price", f"${price:.2f}")
                        
                        # Candlestick chart
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
                
                except ValueError as e:
                    st.error(f"Value Error: {str(e)}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.error(f"❌ Could not fetch data for {ticker}")
