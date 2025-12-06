# streamlit_app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="US Indices Dashboard", layout="wide")
st.title("Major US Indices – Normalized Performance (1928–Today)")

# Fixed names (no spaces, Plotly-safe)
INDICES = {
    "^DJI":  "Dow Jones",
    "^GSPC": "S&P 500",
    "^IXIC": "NASDAQ",
    "^RUT":  "Russell 2000",
    "^NYA":  "NYSE Composite",
}

# Date picker
start_date = st.date_input(
    "Start date",
    value=pd.to_datetime("1928-01-01"),
    min_value=pd.to_datetime("1928-01-01"),
    max_value=datetime.today()
)

@st.cache_data(ttl=3600, show_spinner=False)
def get_data(start: str):
    dfs = []
    for symbol, pretty_name in INDICES.items():
        df = yf.download(
            symbol,
            start=start,
            interval="1d",
            auto_adjust=True,
            progress=False
        )[["Close"]]
        df = df.rename(columns={"Close": pretty_name})
        dfs.append(df)
    
    data = pd.concat(dfs, axis=1)
    data = data.asfreq("B").ffill()
    norm = (data / data.dropna().iloc[0]) * 100
    return norm

# Load data
with st.spinner(f"Loading data from {start_date} onward..."):
    normalized = get_data(str(start_date))

# Plot
fig = go.Figure()
for col in normalized.columns:
    fig.add_trace(go.Scatter(
        x=normalized.index,
        y=normalized[col],
        mode="lines",
        name=col,                    # now safe (no spaces)
        hovertemplate="%{y:.1f}%"
    ))

fig.update_layout(
    height=700,
    hovermode="x unified",
    template="plotly_white",
    xaxis_rangeslider_visible=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=40, b=20)
)

st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

st.caption("Data: Yahoo Finance via yfinance • Interactive zoom & pan • Auto-updates daily")
st.download_button(
    "Download visible data as CSV",
    data=normalized.to_csv().encode(),
    file_name=f"us_indices_from_{start_date}.csv",
    mime="text/csv"
)
