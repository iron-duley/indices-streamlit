# streamlit_app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="US Indices Dashboard", layout="wide")
st.title("Major US Indices – Normalized Performance (1928–Today)")

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
    for symbol, name in INDICES.items():
        df = yf.Ticker(symbol).history(period="max", interval="1d", auto_adjust=True)["Close"]
        df = df.rename(name)
        dfs.append(df)
    data = pd.concat(dfs, axis=1)
    data = data.asfreq("B").ffill()  # business days + forward fill
    norm = (data / data.dropna().iloc[0]) * 26
    return norm

with st.spinner("Downloading 20+ years of data..."):
    norm = get_data()

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

st.caption("Data source: Yahoo Finance via yfinance • Auto-updates daily")
st.download_button(
    label="Download CSV",
    data=norm.to_csv().encode(),
    file_name="us_indices_normalized.csv",
    mime="text/csv"
)
