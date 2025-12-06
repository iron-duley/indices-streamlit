# streamlit_app.py

# Import necessary libraries
import streamlit as st  # For creating the web dashboard
import yfinance as yf   # For downloading financial data from Yahoo Finance
import pandas as pd     # For data manipulation and analysis
import plotly.graph_objects as go  # For creating interactive charts

# Configure the Streamlit page with a title and wide layout
# Added Open Graph tags for better LinkedIn previews
st.set_page_config(
    page_title="US Indices Dashboard",
    layout="wide",
    page_icon="📈",
    # Add Open Graph tags for better LinkedIn previews
    menu_items={
        'Get Help': 'https://docs.streamlit.io/',
        'Report a bug': "https://github.com/streamlit/streamlit/issues",
        'About': "# US Indices Dashboard\nTrack normalized performance of major US stock indices since 2000"
    }
)

# Add meta tags for social sharing (helps with preview)
# Replace YOUR_STREAMLIT_URL_HERE with your actual Streamlit URL
st.markdown("""
    <meta property="og:title" content="US Indices Dashboard">
    <meta property="og:description" content="Track normalized performance of Dow Jones, S&P 500, NASDAQ, Russell 2000, and NYSE Composite since 2000">
    <meta property="og:image" content="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1200&h=630&q=80">
    <meta property="og:url" content="YOUR_STREAMLIT_URL_HERE">
    <meta name="twitter:card" content="summary_large_image">
""", unsafe_allow_html=True)

# Display the main title at the top of the dashboard
st.title("📈 Major US Indices – Normalized Performance (2000–Today)")

# Define a dictionary of stock market indices we want to track
# Keys: Yahoo Finance ticker symbols
# Values: Display names for the charts
INDICES = {
    "^DJI": "Dow Jones",        # Dow Jones Industrial Average (30 large US companies)
    "^GSPC": "S&P 500",         # S&P 500 Index (500 large US companies)
    "^IXIC": "NASDAQ Composite", # NASDAQ Composite Index (technology-heavy)
    "^RUT":  "Russell 2000",    # Russell 2000 Index (small-cap US companies)
    "^NYA":  "NYSE Composite",  # NYSE Composite Index (all NYSE-listed stocks)
}

# Cache this function to speed up the app - data is stored for 1 hour
# This prevents re-downloading data every time the app reloads
@st.cache_data(ttl=3600)  # ttl = Time To Live in seconds (3600 seconds = 1 hour)
def get_data():
    """
    Downloads stock market data, processes it, and normalizes all indices 
    to start at a value of 10 on their first trading day in 2000.
    """
    # List to store data for each index
    dfs = []
    
    # We only want data starting from January 1, 2000
    start_date = "2000-01-01"
    
    # Loop through each index in our dictionary
    for symbol, name in INDICES.items():
        # Download historical closing prices for this index
        # start=start_date: Only get data from 2000 onward
        # interval="1d": Daily data
        # auto_adjust=True: Adjust for stock splits and dividends
        df = yf.Ticker(symbol).history(start=start_date, interval="1d", auto_adjust=True)["Close"]
        
        # Rename the column to the display name (e.g., "Dow Jones" instead of "^DJI")
        df = df.rename(name)
        
        # Add this index's data to our list
        dfs.append(df)
    
    # Combine all individual index data into one DataFrame
    # axis=1 means combine as columns (side-by-side)
    data = pd.concat(dfs, axis=1)
    
    # Ensure we have data for every business day (Monday-Friday)
    # asfreq("B"): Resample to business day frequency
    # ffill(): Forward fill - if a day is missing, use the last available value
    data = data.asfreq("B").ffill()
    
    # NORMALIZATION: Make all indices comparable
    # data.dropna().iloc[0]: Get the first row with all data available
    # Divide all values by this starting value, then multiply by 10
    # Result: All indices start at 10 on their first day in 2000
    norm = (data / data.dropna().iloc[0]) * 10
    
    # Return the normalized data
    return norm

# Show a loading message while downloading data
with st.spinner("Downloading market data from 2000 to present..."):
    # Call our function to get the normalized data
    norm = get_data()

# Display the date range of our data
# norm.index[-1] gets the last date in our dataset (most recent trading day)
latest_date = norm.index[-1].strftime('%B %d, %Y')  # Format as "Month Day, Year"
st.markdown(f"**Data Range:** January 1, 2000 – {latest_date}")

# Create an interactive chart using Plotly
fig = go.Figure()

# Add a line for each index to the chart
for col in norm.columns:
    fig.add_trace(
        go.Scatter(
            x=norm.index,      # X-axis: Dates
            y=norm[col],       # Y-axis: Normalized values
            mode="lines",      # Display as a line chart
            name=col           # Legend label (index name)
        )
    )

# Customize the chart appearance
fig.update_layout(
    height=700,  # Set chart height
    hovermode="x unified",  # Show all values at same x-position when hovering
    template="plotly_white",  # Use a clean white theme
    title="Normalized Index Performance (Base = 10 on first trading day in 2000)",
    legend=dict(
        orientation="h",      # Horizontal legend (instead of vertical)
        yanchor="bottom",     # Anchor at bottom
        y=1.02,              # Position slightly above chart
        xanchor="right",      # Anchor at right side
        x=1                  # Align to right edge
    ),
    xaxis_title="Date",        # X-axis label
    yaxis_title="Normalized Value (Base = 10)"  # Y-axis label
)

# Display the chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Add a caption at the bottom with data source info
st.caption("Data source: Yahoo Finance via yfinance • Auto-updates daily • Data from Jan 1, 2000 to present")

# Create two columns for our buttons (side by side)
col1, col2 = st.columns(2)

# First column: Download button
with col1:
    st.download_button(
        label="📥 Download CSV",  # Button text with emoji
        data=norm.to_csv().encode(),  # Convert DataFrame to CSV format
        file_name="us_indices_normalized_2000_present.csv",  # Suggested filename
        mime="text/csv"  # File type
    )

# Second column: Refresh button
with col2:
    if st.button("🔄 Refresh Data"):
        # Clear the cache to force re-downloading fresh data
        st.cache_data.clear()
        # Reload the app
        st.rerun()

# Add sharing instructions at the bottom
st.markdown("---")
st.markdown("""
### 📤 Share This Dashboard
            
**For LinkedIn:** 
1. Take a screenshot of the chart above
2. Create a post with the image
3. Copy this link and include it in your post:

`https://indices-app-huqftcnkhfljvemeefgivy.streamlit.app/`

**Hashtags to use:** #DataScience #Python #Finance #StockMarket #DataViz #Investing
""")
