# streamlit_app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="US Indices Dashboard", layout="wide")
st.title("Major US Indices – Normalized Performance (2000–Today)")

INDICES = {
    "^DJI": "Dow Jones",
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ Composite",
    "^RUT":  "Russell 2000",
    "^NYA":  "NYSE Composite",
}

@st.cache_data(ttl=3600)  # refresh max once per hour
def get_data():
    dfs = []
    start_date = "2000-01-01"
    
    for symbol, name in INDICES.items():
        # Download data starting from 2000-01-01
        df = yf.Ticker(symbol).history(start=start_date, interval="1d", auto_adjust=True)["Close"]
        df = df.rename(name)
        dfs.append(df)
    
    data = pd.concat(dfs, axis=1)
    data = data.asfreq("B").ffill()  # business days + forward fill
    
    # Normalize: set first available date's price to 10
    # Using .iloc[0] on the filtered data ensures normalization starts from 2000
    norm = (data / data.dropna().iloc[0]) * 10
    return norm

with st.spinner("Downloading data from 2000..."):
    norm = get_data()

# Create the plot
fig = go.Figure()
for col in norm.columns:
    fig.add_trace(go.Scatter(x=norm.index, y=norm[col], mode="lines", name=col))

fig.update_layout(
    height=700,
    hovermode="x unified",
    template="plotly_white",
    title=None,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

st.caption("Data source: Yahoo Finance via yfinance • Auto-updates daily • Data from Jan 1, 2000 to present")
st.download_button(
    label="Download CSV",
    data=norm.to_csv().encode(),
    file_name="us_indices_normalized_2000_present.csv",
    mime="text/csv"
)
