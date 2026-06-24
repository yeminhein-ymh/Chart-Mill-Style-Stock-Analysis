from __future__ import annotations

from datetime import datetime
import textwrap
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    import yfinance as yf
except Exception:  # pragma: no cover
    yf = None


st.set_page_config(
    page_title="ChartMill Style Stocks Analysis",
    page_icon="CM",
    layout="wide",
    initial_sidebar_state="expanded",
)


INDEX_SYMBOLS = ("SPY", "QQQ", "IWM")
WATCHLIST = ["SPY", "QQQ", "IWM", "NVDA", "AMZN", "MU", "PLTR", "GOOGL", "AMD", "AVGO", "TSLA", "TSM", "AAPL", "MSFT"]
POPULAR = ["NVDA", "AMZN", "MU", "PLTR", "GOOGL", "AMD", "SPY", "AVGO", "QQQ", "GOOG", "TSLA", "TSM", "AAPL"]


def cm_html(markup: str, container=st) -> None:
    container.html(textwrap.dedent(markup).strip())


def inject_css() -> None:
    cm_html(
        """
        <style>
        :root {
            --cm-bg: #f3f4f6;
            --cm-sidebar: #ffffff;
            --cm-panel: #ffffff;
            --cm-border: #d8dde6;
            --cm-border-soft: #edf0f4;
            --cm-text: #2b2f36;
            --cm-muted: #6c7280;
            --cm-link: #1f69b3;
            --cm-blue: #2f80c9;
            --cm-green: #14844d;
            --cm-red: #c73737;
            --cm-table-head: #f2f4f7;
            --cm-yellow: #f7c948;
        }

        html, body, .stApp {
            background: var(--cm-bg);
            color: var(--cm-text);
            font-family: Arial, Helvetica, sans-serif;
        }

        .block-container {
            max-width: 1280px;
            padding: 0.75rem 1.15rem 2rem;
        }

        section[data-testid="stSidebar"] {
            width: 292px !important;
            background: var(--cm-sidebar);
            border-right: 1px solid #d5dae3;
        }

        section[data-testid="stSidebar"] > div {
            padding: 0.7rem 0 1.25rem;
        }

        [data-testid="stSidebarNav"],
        div[data-testid="stToolbar"],
        header[data-testid="stHeader"] {
            display: none;
        }

        .cm-side-logo {
            display: flex;
            align-items: center;
            gap: 9px;
            padding: 5px 18px 7px;
            border-bottom: 1px solid var(--cm-border-soft);
            margin-bottom: 8px;
        }

        .cm-logo-mark {
            width: 40px;
            height: 40px;
            border-radius: 4px;
            background: linear-gradient(135deg, #367fb8 0%, #1f5f95 100%);
            color: #fff;
            display: grid;
            place-items: center;
            font-size: 18px;
            font-weight: 800;
            letter-spacing: 0;
        }

        .cm-logo-word {
            font-size: 24px;
            font-weight: 700;
            color: #2e343b;
        }

        .cm-auth {
            padding: 0 18px 12px;
            font-size: 12px;
            color: var(--cm-muted);
        }

        .cm-home {
            display: block;
            padding: 10px 18px;
            color: #3b3f46;
            text-decoration: none;
            font-size: 15px;
            border-top: 1px solid var(--cm-border-soft);
            border-bottom: 1px solid var(--cm-border-soft);
        }

        .cm-nav-block {
            padding: 9px 0 3px;
        }

        .cm-nav-title,
        .cm-section-heading {
            display: flex;
            align-items: center;
            gap: 11px;
            padding: 8px 18px 9px;
            font-size: 20px;
            font-weight: 700;
            color: #2c3036;
        }

        .cm-nav-title svg,
        .cm-section-heading svg {
            width: 29px;
            height: 29px;
            fill: currentColor;
            flex: 0 0 auto;
        }

        .cm-side-link {
            display: block;
            padding: 8px 18px 8px 58px;
            color: #2f333a;
            text-decoration: none;
            font-size: 21px;
            line-height: 1.35;
        }

        .cm-side-link:hover {
            color: var(--cm-link);
            background: #f6f9fc;
        }

        .cm-section-heading {
            justify-content: space-between;
            margin-top: 23px;
        }

        .cm-section-left {
            display: flex;
            align-items: center;
            gap: 11px;
        }

        .cm-side-small {
            display: block;
            padding: 8px 18px 8px 58px;
            font-size: 15px;
            color: #3b3f46;
            text-decoration: none;
        }

        .cm-topbar {
            min-height: 50px;
            background: #ffffff;
            border: 1px solid var(--cm-border);
            border-radius: 3px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 13px 0 16px;
            margin-bottom: 9px;
        }

        .cm-search {
            width: min(430px, 45vw);
            height: 32px;
            border: 1px solid #cfd6df;
            border-radius: 3px;
            background: #f9fafb;
            color: #69717d;
            display: flex;
            align-items: center;
            padding-left: 11px;
            font-size: 13px;
        }

        .cm-top-actions {
            display: flex;
            gap: 7px;
            font-size: 12px;
            color: var(--cm-muted);
        }

        .cm-btn {
            background: #f7f8fa;
            border: 1px solid #ccd3dd;
            border-radius: 3px;
            padding: 5px 9px;
            color: #3d444c;
        }

        .cm-market-strip {
            background: #ffffff;
            border: 1px solid var(--cm-border);
            border-radius: 3px;
            margin-bottom: 13px;
        }

        .cm-index-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            border-bottom: 1px solid var(--cm-border-soft);
        }

        .cm-index-card {
            padding: 10px 14px 8px;
            border-right: 1px solid var(--cm-border-soft);
            min-height: 73px;
        }

        .cm-index-card:last-child {
            border-right: 0;
        }

        .cm-index-symbol {
            color: var(--cm-link);
            font-weight: 700;
            font-size: 18px;
            text-decoration: underline;
            text-underline-offset: 2px;
        }

        .cm-index-price {
            font-size: 21px;
            font-weight: 700;
            margin-top: 3px;
        }

        .cm-after {
            color: var(--cm-muted);
            font-size: 12px;
            margin-top: 2px;
        }

        .cm-strip-bottom {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px 12px;
            flex-wrap: wrap;
            font-size: 13px;
        }

        .cm-open-screener {
            border: 1px solid #b9c7d8;
            background: #eef5fb;
            color: var(--cm-link);
            padding: 5px 9px;
            border-radius: 3px;
            font-weight: 700;
            text-decoration: none;
        }

        .cm-popular span {
            color: var(--cm-link);
            margin-right: 9px;
            text-decoration: underline;
            font-weight: 600;
        }

        .cm-section-title {
            font-size: 24px;
            line-height: 1.2;
            font-weight: 700;
            color: #2c3036;
            margin: 13px 0 9px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .cm-title-icon {
            width: 23px;
            height: 23px;
            border-radius: 3px;
            background: #e7edf4;
            color: var(--cm-link);
            display: inline-grid;
            place-items: center;
            font-size: 14px;
            font-weight: 800;
        }

        .cm-breadth {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            background: #ffffff;
            border: 1px solid var(--cm-border);
            border-radius: 3px;
            margin-bottom: 13px;
        }

        .cm-breadth-item {
            padding: 12px 8px 11px;
            text-align: center;
            border-right: 1px solid var(--cm-border-soft);
        }

        .cm-breadth-item:last-child {
            border-right: 0;
        }

        .cm-breadth-label {
            color: #3c424a;
            font-weight: 700;
            font-size: 15px;
            margin-bottom: 10px;
        }

        .cm-breadth-value {
            font-size: 25px;
            font-weight: 700;
        }

        .cm-grid-3 {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 14px;
        }

        .cm-widget {
            background: #ffffff;
            border: 1px solid var(--cm-border);
            border-radius: 3px;
            overflow: hidden;
        }

        .cm-widget-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            background: #f8fafc;
            border-bottom: 1px solid var(--cm-border);
            padding: 8px 10px;
        }

        .cm-widget-head a {
            color: var(--cm-link);
            font-size: 19px;
            font-weight: 700;
            text-decoration: underline;
            text-underline-offset: 2px;
        }

        .cm-full-list {
            color: var(--cm-link);
            font-size: 12px;
            font-weight: 700;
            text-decoration: underline;
        }

        .cm-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        .cm-table th {
            background: var(--cm-table-head);
            color: #464c55;
            text-align: right;
            padding: 6px 8px;
            border-bottom: 1px solid var(--cm-border-soft);
            font-weight: 700;
        }

        .cm-table th:first-child,
        .cm-table td:first-child {
            text-align: left;
        }

        .cm-table td {
            text-align: right;
            padding: 6px 8px;
            border-bottom: 1px solid var(--cm-border-soft);
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
        }

        .cm-table tr:last-child td {
            border-bottom: 0;
        }

        .cm-symbol-link {
            color: var(--cm-link);
            font-weight: 700;
            text-decoration: underline;
            text-underline-offset: 2px;
        }

        .cm-pos { color: var(--cm-green); font-weight: 700; }
        .cm-neg { color: var(--cm-red); font-weight: 700; }

        .cm-linkbar {
            text-align: center;
            margin: 7px 0 16px;
        }

        .cm-blue-link {
            color: var(--cm-link);
            font-weight: 700;
            text-decoration: underline;
            text-transform: uppercase;
            font-size: 12px;
        }

        .cm-content-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
            gap: 14px;
            align-items: start;
        }

        .cm-news-card {
            background: #ffffff;
            border: 1px solid var(--cm-border);
            border-radius: 3px;
            margin-bottom: 11px;
            display: grid;
            grid-template-columns: 96px minmax(0, 1fr);
            overflow: hidden;
        }

        .cm-news-img {
            background:
                linear-gradient(145deg, rgba(47,128,201,0.75), rgba(26,75,120,0.85)),
                repeating-linear-gradient(135deg, #dfe7f0 0 7px, #cbd7e3 7px 14px);
            min-height: 92px;
        }

        .cm-news-body {
            padding: 9px 11px 10px;
        }

        .cm-meta {
            color: var(--cm-muted);
            font-size: 12px;
            margin-bottom: 4px;
        }

        .cm-news-title {
            color: var(--cm-link);
            font-size: 18px;
            font-weight: 700;
            line-height: 1.22;
            text-decoration: underline;
            text-underline-offset: 2px;
        }

        .cm-ideas {
            background: #ffffff;
            border: 1px solid var(--cm-border);
            border-radius: 3px;
            padding: 15px 15px 13px;
            margin: 12px 0 18px;
        }

        .cm-ideas-copy {
            color: #4d535c;
            font-size: 14px;
            line-height: 1.45;
            margin-bottom: 13px;
        }

        .cm-tabs {
            display: flex;
            gap: 0;
            border-bottom: 1px solid var(--cm-border);
            margin-bottom: 12px;
        }

        .cm-tab {
            padding: 8px 12px;
            border: 1px solid var(--cm-border);
            border-bottom: 0;
            background: #f6f8fa;
            color: #3b424c;
            font-weight: 700;
            font-size: 13px;
            margin-right: 4px;
            border-radius: 3px 3px 0 0;
        }

        .cm-tab.active {
            background: #ffffff;
            color: var(--cm-link);
        }

        .cm-idea-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }

        .cm-idea-card {
            border: 1px solid var(--cm-border);
            border-radius: 3px;
            background: #ffffff;
            overflow: hidden;
        }

        .cm-idea-art {
            height: 82px;
            background:
                linear-gradient(140deg, rgba(255,255,255,0.3), rgba(255,255,255,0) 45%),
                linear-gradient(135deg, #2f80c9, #1e5f95);
            position: relative;
        }

        .cm-idea-art:after {
            content: "";
            position: absolute;
            left: 14px;
            right: 14px;
            bottom: 14px;
            height: 34px;
            border-left: 3px solid #fff;
            border-bottom: 3px solid #fff;
            background: linear-gradient(135deg, transparent 0 35%, rgba(255,255,255,.35) 35% 38%, transparent 38% 56%, rgba(255,255,255,.45) 56% 59%, transparent 59%);
            opacity: .9;
        }

        .cm-idea-title {
            padding: 9px 10px 4px;
            min-height: 49px;
            color: var(--cm-link);
            font-size: 15px;
            font-weight: 700;
            line-height: 1.22;
            text-decoration: underline;
        }

        .cm-more {
            display: inline-block;
            margin: 4px 10px 10px;
            border: 1px solid #b9c7d8;
            color: var(--cm-link);
            background: #eef5fb;
            padding: 4px 8px;
            font-weight: 700;
            font-size: 12px;
            border-radius: 3px;
        }

        div[data-testid="stSelectbox"],
        div[data-testid="stMultiSelect"],
        div[data-testid="stSlider"] {
            margin: 0 18px 10px;
        }

        div[data-testid="stPlotlyChart"] {
            background: #ffffff;
            border: 1px solid var(--cm-border);
            border-radius: 3px;
            padding: 4px;
        }

        @media (max-width: 1050px) {
            .cm-grid-3,
            .cm-content-grid,
            .cm-idea-grid {
                grid-template-columns: 1fr;
            }

            .cm-breadth,
            .cm-index-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 680px) {
            .block-container {
                padding-left: .7rem;
                padding-right: .7rem;
            }

            .cm-topbar,
            .cm-strip-bottom {
                align-items: flex-start;
                flex-direction: column;
            }

            .cm-search {
                width: 100%;
            }

            .cm-breadth,
            .cm-index-grid {
                grid-template-columns: 1fr;
            }

            .cm-side-link {
                font-size: 18px;
            }
        }
        </style>
        """
    )


def icon_svg(name: str) -> str:
    icons = {
        "wrench": '<svg viewBox="0 0 24 24"><path d="M22 19.6 13.9 11.5c.7-2.4.1-5.1-1.8-7A7.1 7.1 0 0 0 5 2.8l4.4 4.4-2.9 2.9L2 5.8A7.1 7.1 0 0 0 3.7 13c1.9 1.9 4.6 2.5 7 1.8l8.1 8.1c.4.4 1 .4 1.4 0l1.8-1.8c.4-.5.4-1.1 0-1.5Z"/></svg>',
        "chart": '<svg viewBox="0 0 24 24"><path d="M3 4c.7 0 1.2.5 1.2 1.2v12.5h16.6c.7 0 1.2.5 1.2 1.2s-.5 1.2-1.2 1.2H3c-.7 0-1.2-.5-1.2-1.2V5.2C1.8 4.5 2.3 4 3 4Zm5.2 6.2c.4 0 .8.2 1 .5l2.2 2.6 2.8-5.2c.2-.4.6-.6 1.1-.6s.8.3 1 .7l2.1 5.1h2.4c.7 0 1.2.5 1.2 1.2s-.5 1.2-1.2 1.2h-3.2c-.5 0-.9-.3-1.1-.7l-1.5-3.7-2.5 4.6c-.2.4-.6.6-1 .6s-.8-.2-1-.5l-2.4-2.9-1.6 1.9c-.4.5-1.2.6-1.7.1s-.6-1.2-.1-1.7l2.5-2.9c.2-.2.6-.3 1-.3Z"/></svg>',
    }
    return icons[name]


def render_sidebar() -> None:
    cm_html(
        f"""
        <div class="cm-side-logo">
            <div class="cm-logo-mark">CM</div>
            <div class="cm-logo-word">ChartMill</div>
        </div>
        <div class="cm-auth">Login&nbsp;&nbsp; Register</div>
        <a class="cm-home" href="#home">Home</a>
        <div class="cm-nav-block">
            <div class="cm-nav-title">{icon_svg("wrench")}<span>Trading Tools</span></div>
            <a class="cm-side-link" href="#trading-ideas">Trading Ideas</a>
            <a class="cm-side-link" href="#stock-screener">Stock Screener</a>
            <a class="cm-side-link" href="#stock-charts">Stock Charts</a>
            <a class="cm-side-link" href="#stock-charts">Full Screen Charts</a>
            <a class="cm-side-link" href="#market-monitor">Market Monitor</a>
            <a class="cm-side-link" href="#sector-analyzer">Sector</a>
            <a class="cm-side-link" href="#sector-analyzer">Analyzer</a>
            <a class="cm-side-link" href="#earnings">Earnings</a>
            <a class="cm-side-link" href="#insider-trading">Insider Trading</a>
            <a class="cm-side-link" href="#upgrades">Up- and Downgrades</a>
            <a class="cm-side-link" href="#news">News</a>
        </div>
        <div class="cm-section-heading">
            <div class="cm-section-left">{icon_svg("chart")}<span>Market Data</span></div>
            <span style="font-size:15px;">&#9650;</span>
        </div>
        <a class="cm-side-small" href="#market-monitor">Market Movers</a>
        <a class="cm-side-small" href="#market-news">Market News</a>
        <a class="cm-side-small" href="#stock-screener">Screeners</a>
        <div class="cm-section-heading" style="margin-top:15px;">
            <div class="cm-section-left"><span style="font-size:27px;">$</span><span>Plans & Products</span></div>
        </div>
        <a class="cm-side-small" href="#plans">Subscription</a>
        <a class="cm-side-small" href="#learn">Swing Trading Course</a>
        """,
        container=st.sidebar,
    )
    st.sidebar.selectbox("Universe", ["US Market", "Nasdaq", "NYSE", "AMEX", "ETF"], index=0, label_visibility="collapsed")
    st.sidebar.multiselect("Tickers", WATCHLIST, default=["SPY", "QQQ", "NVDA", "AMZN"], label_visibility="collapsed")


@st.cache_data(ttl=600, show_spinner=False)
def load_prices(symbols: tuple[str, ...], period: str = "6mo") -> pd.DataFrame:
    if yf is None:
        return synthetic_prices(symbols)

    frames = []
    for symbol in symbols:
        try:
            history = yf.Ticker(symbol).history(period=period, auto_adjust=True)
            if history.empty:
                continue
            frame = history.reset_index()[["Date", "Close", "Volume"]].copy()
            frame["symbol"] = symbol
            frames.append(frame)
        except Exception:
            continue
    if not frames:
        return synthetic_prices(symbols)
    prices = pd.concat(frames, ignore_index=True)
    prices["Date"] = pd.to_datetime(prices["Date"]).dt.tz_localize(None)
    return prices


def synthetic_prices(symbols: Iterable[str], rows: int = 126) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=rows)
    frames = []
    for index, symbol in enumerate(symbols):
        base = 55 + index * 18
        drift = rng.normal(0.001, 0.018, rows)
        close = base * np.cumprod(1 + drift)
        volume = rng.integers(380_000, 2_200_000_000, rows)
        frames.append(pd.DataFrame({"Date": dates, "Close": close, "Volume": volume, "symbol": symbol}))
    return pd.concat(frames, ignore_index=True)


def latest_table(prices: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for symbol, frame in prices.sort_values("Date").groupby("symbol"):
        tail = frame.tail(2)
        latest = tail.iloc[-1]
        prior = tail.iloc[-2] if len(tail) > 1 else latest
        change = latest["Close"] - prior["Close"]
        pct = change / prior["Close"] * 100 if prior["Close"] else 0
        rows.append({"Symbol": symbol, "Volume": latest["Volume"], "Price": latest["Close"], "% Chg": pct, "Change": change})
    return pd.DataFrame(rows).sort_values("% Chg", ascending=False)


def with_market_rows(latest: pd.DataFrame) -> pd.DataFrame:
    extra = pd.DataFrame(
        [
            ["ROLR", 82_490_000, 18.89, 436.65, 15.37],
            ["IVP", 2_150_000_000, 0.082, 256.52, 0.06],
            ["SEGG", 331_060_000, 0.9267, 79.91, 0.41],
            ["BNAI", 46_840_000, 5.80, 60.66, 2.19],
            ["GELS", 28_040_000, 1.16, 39.24, 0.33],
            ["VCIG", 8_930_000, 1.05, 36.70, 0.28],
            ["CRML", 59_990_000, 17.925, 32.58, 4.40],
            ["CODX", 1_310_000, 2.36, -60.54, -3.62],
            ["PSTV", 95_180_000, 0.2904, -38.23, -0.18],
            ["HUBC", 11_180_000, 0.3495, -34.83, -0.19],
            ["ZJYL", 2_290_000, 0.165, -31.48, -0.08],
            ["MTVA", 277_600, 5.42, -30.06, -2.33],
            ["HYMC", 4_940_000, 34.24, 1.18, 0.40],
            ["CELC", 504_400, 114.48, 9.86, 10.27],
            ["GDXU", 626_700, 339.55, 1.19, 3.99],
            ["AGQ", 12_260_000, 266.56, 15.77, 36.27],
            ["RWM", 23_720_000, 15.34, -0.71, -0.11],
            ["FMS", 1_370_000, 21.39, -6.51, -1.49],
            ["RYAN", 1_120_000, 50.17, -0.61, -0.31],
            ["BOX", 3_920_000, 27.28, -3.23, -0.91],
            ["SOXS", 434_840_000, 2.28, 0.44, 0.01],
            ["ZSL", 275_750_000, 2.82, -14.80, -0.49],
            ["MTEN", 274_310_000, 0.0353, 4.75, 0.0016],
            ["SLV", 177_420_000, 84.56, 7.58, 5.96],
        ],
        columns=["Symbol", "Volume", "Price", "% Chg", "Change"],
    )
    return pd.concat([extra, latest], ignore_index=True)


def compact_volume(value: float) -> str:
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:.0f}"


def pct_html(value: float) -> str:
    cls = "cm-pos" if value >= 0 else "cm-neg"
    return f'<span class="{cls}">{value:.2f}%</span>'


def market_table_html(title: str, data: pd.DataFrame) -> str:
    rows = []
    for _, row in data.head(7).iterrows():
        rows.append(
            f"""
            <tr>
                <td><span class="cm-symbol-link">{row['Symbol']}</span></td>
                <td>{compact_volume(row['Volume'])}</td>
                <td>{row['Price']:.4g}</td>
                <td>{pct_html(row['% Chg'])}</td>
            </tr>
            """
        )
    return f"""
    <div class="cm-widget">
        <div class="cm-widget-head"><a>{title}</a><span class="cm-full-list">Full List</span></div>
        <table class="cm-table">
            <thead><tr><th>Symbol</th><th>Volume</th><th>Price</th><th>% Chg</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
        </table>
    </div>
    """


def render_topbar() -> None:
    cm_html(
        """
        <span id="home"></span>
        <div class="cm-topbar">
            <div class="cm-search">Search stocks, screeners, news or market data</div>
            <div class="cm-top-actions">
                <span class="cm-btn">Stock Screener</span>
                <span class="cm-btn">Charts</span>
                <span class="cm-btn">Alerts</span>
            </div>
        </div>
        """
    )


def render_market_strip(latest: pd.DataFrame) -> None:
    index_rows = latest.set_index("Symbol").reindex(INDEX_SYMBOLS).dropna(how="all").reset_index()
    cards = []
    for _, row in index_rows.iterrows():
        price = float(row["Price"])
        change = float(row["Change"])
        pct = float(row["% Chg"])
        after_change = change * 0.18
        after_pct = pct * 0.18
        cls = "cm-pos" if pct >= 0 else "cm-neg"
        cards.append(
            f"""
            <div class="cm-index-card">
                <div class="cm-index-symbol">{row['Symbol']}</div>
                <div class="cm-index-price">{price:.2f}&nbsp;&nbsp; <span class="{cls}">{change:+.2f} ({pct:+.2f}%)</span></div>
                <div class="cm-after">After market: {price + after_change:.2f}&nbsp; <span class="{cls}">{after_change:+.2f} ({after_pct:+.2f}%)</span></div>
            </div>
            """
        )
    popular_links = "".join(f"<span>{symbol}</span>" for symbol in POPULAR)
    cm_html(
        f"""
        <div class="cm-market-strip">
            <div class="cm-index-grid">{''.join(cards)}</div>
            <div class="cm-strip-bottom">
                <a class="cm-open-screener" href="#stock-screener">Open Stock Screener</a>
                <div class="cm-popular"><strong>Popular:</strong> {popular_links}</div>
            </div>
        </div>
        """
    )


def render_market_today(latest: pd.DataFrame) -> None:
    advancing = (latest["% Chg"] > 0).mean() * 100
    values = [
        ("Advancing", advancing),
        ("Above SMA(20)", 71.6),
        ("Above SMA(50)", 69.7),
        ("Above SMA(100)", 59.0),
        ("Above SMA(200)", 63.0),
        ("New High Vs Low", 86.7),
    ]
    items = "".join(
        f"""
        <div class="cm-breadth-item">
            <div class="cm-breadth-label">{label}</div>
            <div class="cm-breadth-value">{value:g}</div>
        </div>
        """
        for label, value in values
    )
    cm_html('<span id="market-monitor"></span><div class="cm-section-title"><span class="cm-title-icon">▦</span>Market Today</div>')
    cm_html(f'<div class="cm-breadth">{items}</div>')


def render_movers(market_rows: pd.DataFrame) -> None:
    gainers = market_rows.sort_values("% Chg", ascending=False)
    losers = market_rows.sort_values("% Chg")
    highs = market_rows[market_rows["% Chg"] > 0].sort_values("Price", ascending=False)
    lows = market_rows.sort_values("Price")
    gap_up = market_rows[market_rows["% Chg"] > 4].sort_values("% Chg", ascending=False)
    active = market_rows.sort_values("Volume", ascending=False)
    widgets = [
        market_table_html("Top Gainers", gainers),
        market_table_html("Top Losers", losers),
        market_table_html("New 52 Week High", highs),
        market_table_html("New 52 Week Low", lows),
        market_table_html("Gap Up Stocks", gap_up),
        market_table_html("Most Active", active),
    ]
    cm_html(f'<div class="cm-grid-3">{"".join(widgets)}</div>')
    cm_html('<div class="cm-linkbar"><a class="cm-blue-link" href="#market-monitor">TO MARKET MONITOR</a></div>')


def chart_for_symbol(prices: pd.DataFrame, symbol: str) -> go.Figure:
    frame = prices[prices["symbol"] == symbol].sort_values("Date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=frame["Date"], y=frame["Close"], name=symbol, mode="lines", line={"color": "#1f69b3", "width": 2.2}))
    fig.add_trace(go.Scatter(x=frame["Date"], y=frame["Close"].rolling(20).mean(), name="SMA 20", mode="lines", line={"color": "#14844d", "width": 1.5}))
    fig.add_trace(go.Scatter(x=frame["Date"], y=frame["Close"].rolling(50).mean(), name="SMA 50", mode="lines", line={"color": "#c73737", "width": 1.5}))
    fig.update_layout(
        height=330,
        margin={"l": 16, "r": 16, "t": 22, "b": 18},
        legend={"orientation": "h", "y": 1.1, "x": 0},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        hovermode="x unified",
    )
    fig.update_yaxes(gridcolor="#edf0f4", title="")
    fig.update_xaxes(gridcolor="#f5f7f9", title="")
    return fig


def render_news() -> None:
    cm_html('<span id="market-news"></span><div class="cm-section-title"><span class="cm-title-icon">▣</span>Market Monitor</div>')
    market_monitor = [
        ("21 hours ago - By: ChartMill - Mentions: IWM QQQ SPY", "Breadth Cools at the Highs, But the Uptrend Stays Intact"),
        ("a day ago - By: ChartMill - Mentions: CVX COP XOM JPM", "Oil Threats Lift Energy While Wall Street Keeps Watching Breadth"),
    ]
    for meta, title in market_monitor:
        cm_html(news_card(meta, title))

    cm_html('<span id="news"></span><div class="cm-section-title"><span class="cm-title-icon">▤</span>Market News</div>')
    news_items = [
        ("38 minutes ago - By: Bloomberg - Mentions: F", "Why This $170,000 F.P. Journe Is the Watch of the Century"),
        ("39 minutes ago - By: Bloomberg", "India's Russia Oil Trade May Dip Again, Stranding Cargoes at Sea"),
        ("37 minutes ago - By: Bloomberg", "Korea Cuts Naver and NCSoft Units From Intense Sovereign AI Race"),
        ("34 minutes ago - By: CNBC", "European markets head for higher open as traders track global headlines"),
        ("8 hours ago - By: ChartMill - Mentions: FUL", "H.B. Fuller Reports Strong Profit Growth Despite Revenue Miss"),
    ]
    for meta, title in news_items:
        cm_html(news_card(meta, title))
    cm_html('<div class="cm-linkbar"><a class="cm-blue-link" href="#news">ALL NEWS</a></div>')


def news_card(meta: str, title: str) -> str:
    return f"""
    <div class="cm-news-card">
        <div class="cm-news-img"></div>
        <div class="cm-news-body">
            <div class="cm-meta">{meta}</div>
            <div class="cm-news-title">{title}</div>
        </div>
    </div>
    """


def render_ideas() -> None:
    ideas = [
        "O'Neill CANSLIM High Growth screen",
        "Mark Minervini - Trend Template + FA Screen 6",
        "High Growth Momentum + Trend Template",
        "High Growth Momentum Breakout Setups",
        "Martin Zweig: Growth at Reasonable Price",
        "Strong Growth Stocks with good Technical Setup Ratings",
    ]
    cards = "".join(
        f"""
        <div class="cm-idea-card">
            <div class="cm-idea-art"></div>
            <div class="cm-idea-title">{title}</div>
            <span class="cm-more">MORE INFO</span>
        </div>
        """
        for title in ideas
    )
    cm_html(
        f"""
        <span id="trading-ideas"></span>
        <div class="cm-section-title"><span class="cm-title-icon">▧</span>Discover: ChartMill Trading and Investment Ideas</div>
        <div class="cm-ideas">
            <div class="cm-ideas-copy">
                Get a head start with our library of pre-configured screens. Combine Technical and Fundamental Analysis for position trading,
                swing trading based on technical analysis, or long-term Growth, Value and Quality investments.
            </div>
            <div class="cm-tabs">
                <span class="cm-tab active">Technical and Fundamental</span>
                <span class="cm-tab">Pure Technical</span>
                <span class="cm-tab">Pure Fundamental</span>
            </div>
            <div class="cm-idea-grid">{cards}</div>
            <div class="cm-linkbar" style="margin-bottom:0;"><a class="cm-blue-link">Explore Trading Ideas</a></div>
        </div>
        """
    )


def render_screener(market_rows: pd.DataFrame) -> None:
    cm_html('<span id="stock-screener"></span><div class="cm-section-title"><span class="cm-title-icon">⌕</span>Stock Screener</div>')
    min_change, max_change = st.slider("% change range", -75.0, 450.0, (-10.0, 100.0), 5.0)
    screened = market_rows[(market_rows["% Chg"] >= min_change) & (market_rows["% Chg"] <= max_change)].sort_values("% Chg", ascending=False)
    st.dataframe(
        screened[["Symbol", "Volume", "Price", "% Chg"]].style.format({"Volume": "{:,.0f}", "Price": "{:.4g}", "% Chg": "{:+.2f}%"}),
        use_container_width=True,
        hide_index=True,
        height=285,
    )


def render_secondary_tools(prices: pd.DataFrame, market_rows: pd.DataFrame, selected_symbol: str) -> None:
    cm_html('<span id="stock-charts"></span><div class="cm-section-title"><span class="cm-title-icon">⌁</span>Stock Charts</div>')
    st.plotly_chart(chart_for_symbol(prices, selected_symbol), use_container_width=True)

    cm_html('<span id="sector-analyzer"></span><div class="cm-section-title"><span class="cm-title-icon">◫</span>Sector Analyzer</div>')
    sectors = pd.DataFrame(
        {"Sector": ["Technology", "Communication", "Consumer Cyclical", "Financials", "Healthcare", "Industrials"], "Score": [91, 84, 77, 69, 62, 58]}
    )
    fig = go.Figure(go.Bar(x=sectors["Score"], y=sectors["Sector"], orientation="h", marker_color="#2f80c9"))
    fig.update_layout(height=290, margin={"l": 10, "r": 10, "t": 12, "b": 18}, paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
    fig.update_xaxes(range=[0, 100], gridcolor="#edf0f4", title="")
    fig.update_yaxes(autorange="reversed", title="")
    st.plotly_chart(fig, use_container_width=True)

    cm_html('<span id="earnings"></span><span id="insider-trading"></span><span id="upgrades"></span>')
    render_screener(market_rows)


def main() -> None:
    inject_css()
    render_sidebar()
    render_topbar()

    selected_symbol = st.sidebar.selectbox("Chart symbol", WATCHLIST, index=0, label_visibility="collapsed")
    symbols = tuple(dict.fromkeys(WATCHLIST + [selected_symbol]))
    prices = load_prices(symbols)
    latest = latest_table(prices)
    market_rows = with_market_rows(latest)

    render_market_strip(latest)
    render_market_today(latest)
    render_movers(market_rows)

    left, right = st.columns([1.45, 0.72], gap="medium")
    with left:
        render_news()
        render_ideas()
    with right:
        render_secondary_tools(prices, market_rows, selected_symbol)

    source = "Yahoo Finance via yfinance" if yf is not None else "offline synthetic fallback"
    freshness = prices["Date"].max()
    st.caption(f"Data source: {source}. Last price date shown: {freshness:%b %d, %Y}. Refreshed: {datetime.now():%b %d, %Y %H:%M}.")


if __name__ == "__main__":
    main()
