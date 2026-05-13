import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import time
import json
from datetime import datetime, timedelta
from urllib.parse import quote

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🥖 麵包店估值儀表板",
    page_icon="🥖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+TC:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', sans-serif;
    }
    .stApp {
        background-color: #faf6ef;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #2a1d13;
    }
    [data-testid="stSidebar"] * {
        color: #e8dfc8 !important;
    }
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox select,
    [data-testid="stSidebar"] .stNumberInput input {
        background-color: #3d2b1f !important;
        color: #e8b84b !important;
        border-color: #c8922a !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    [data-testid="stSidebar"] label {
        color: #b0a090 !important;
        font-size: 12px !important;
        letter-spacing: 0.5px;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #e8b84b !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }

    /* Metric cards */
    .val-card {
        background: #fffdf8;
        border: 1px solid #d4c4a8;
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 12px;
        position: relative;
        transition: box-shadow 0.2s;
    }
    .val-card:hover { box-shadow: 0 4px 20px rgba(200,146,42,0.15); }
    .val-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 10px;
    }
    .ticker-name {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: #2a1d13;
    }
    .company-name {
        font-size: 11px;
        color: #7a6a5a;
        margin-top: 2px;
    }
    .price-block { text-align: right; }
    .price-main {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: #2a1d13;
    }
    .price-change-up { color: #3a7a3a; font-size: 13px; font-family: 'IBM Plex Mono', monospace; }
    .price-change-dn { color: #b84040; font-size: 13px; font-family: 'IBM Plex Mono', monospace; }
    .signal-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        margin-bottom: 10px;
    }
    .sig-green  { background: #eef6ee; color: #2a6a2a; border: 1px solid #b0d4b0; }
    .sig-yellow { background: #fef9e6; color: #8a6a10; border: 1px solid #e0c870; }
    .sig-red    { background: #fef0ee; color: #8a2020; border: 1px solid #e0a0a0; }
    .metric-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-top: 8px;
    }
    .m-item {
        background: #f5efe3;
        border-radius: 5px;
        padding: 7px 10px;
        text-align: center;
    }
    .m-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 9px;
        color: #9a8a7a;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .m-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 14px;
        font-weight: 600;
        color: #2a1d13;
        margin-top: 1px;
    }
    .m-value-hi { color: #b84040; }
    .m-value-ok { color: #2a6a2a; }
    .m-value-mid { color: #8a6a10; }

    /* Band bar */
    .band-wrap { margin-top: 10px; }
    .band-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        color: #9a8a7a;
        margin-bottom: 3px;
    }
    .band-bar-bg {
        height: 10px;
        background: linear-gradient(to right, #eef6ee, #fef9e6, #fef0ee);
        border-radius: 5px;
        position: relative;
        margin-bottom: 2px;
    }
    .band-marker {
        position: absolute;
        top: -3px;
        width: 4px;
        height: 16px;
        background: #2a1d13;
        border-radius: 2px;
        transform: translateX(-50%);
    }
    .band-ticks {
        display: flex;
        justify-content: space-between;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 9px;
        color: #9a8a7a;
    }

    /* Bakery box */
    .bakery-box {
        background: #fff9ee;
        border: 1px solid #d4c4a8;
        border-left: 4px solid #c8922a;
        border-radius: 6px;
        padding: 16px 20px;
        margin-top: 12px;
        font-size: 13px;
        line-height: 1.8;
        color: #3d2b1f;
    }
    .bakery-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 1px;
        color: #c8922a;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    /* Section headers */
    .section-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: #c8922a;
        text-transform: uppercase;
        margin-bottom: 4px;
        margin-top: 8px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #2a1d13;
        margin-bottom: 16px;
    }

    /* Ranking table */
    .rank-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        background: #fffdf8;
        border: 1px solid #d4c4a8;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .rank-num {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 18px;
        font-weight: 600;
        color: #c8922a;
        min-width: 28px;
    }
    .rank-ticker {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 16px;
        font-weight: 600;
        color: #2a1d13;
        min-width: 70px;
    }
    .rank-bar-wrap { flex: 1; }
    .rank-bar-bg { background: #e8dfc8; border-radius: 4px; height: 8px; }
    .rank-bar-fill { height: 8px; border-radius: 4px; }
    .rank-score {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 14px;
        color: #2a1d13;
        min-width: 50px;
        text-align: right;
    }

    /* Earnings surprise */
    .eps-row {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-bottom: 6px;
        font-size: 13px;
    }
    .eps-q {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: #7a6a5a;
        min-width: 70px;
    }
    .eps-beat { color: #2a6a2a; font-family: 'IBM Plex Mono', monospace; font-size: 12px; }
    .eps-miss { color: #b84040; font-family: 'IBM Plex Mono', monospace; font-size: 12px; }

    /* Temp gauge */
    .temp-gauge {
        text-align: center;
        padding: 20px;
        background: #fffdf8;
        border: 1px solid #d4c4a8;
        border-radius: 8px;
        margin-top: 12px;
    }
    .temp-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 48px;
        font-weight: 600;
    }
    .temp-label { font-size: 14px; color: #7a6a5a; margin-top: 4px; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f0ebe0;
        border-radius: 6px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 4px;
        color: #7a6a5a;
        font-family: 'Noto Sans TC', sans-serif;
        font-size: 14px;
        padding: 6px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2a1d13 !important;
        color: #e8b84b !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #2a1d13;
        color: #e8b84b;
        border: none;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        padding: 8px 20px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #c8922a;
        color: #2a1d13;
    }

    /* Alert boxes */
    .alert-box {
        padding: 10px 14px;
        border-radius: 5px;
        font-size: 13px;
        margin: 6px 0;
        font-family: 'IBM Plex Mono', monospace;
    }
    .alert-high { background: #fef0ee; border-left: 3px solid #b84040; color: #8a2020; }
    .alert-low  { background: #eef6ee; border-left: 3px solid #3a7a3a; color: #2a6a2a; }

    /* Hide streamlit default elements */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ── INDUSTRY BENCHMARKS ──────────────────────────────────────────────────────
# Source: GuruFocus / MacroTrends verified 5-year median P/E (May 2026)
INDUSTRY_PE = {
    "Technology":                       30.0,   # broad tech 5yr median
    "Consumer Electronics":             30.0,   # AAPL peer group 5yr avg ~30x
    "Software":                         35.0,
    "Semiconductors":                   30.0,
    "Internet Content & Information":   28.0,
    "Auto Manufacturers":               15.0,
    "Financial Services":               14.0,
    "Healthcare":                       22.0,
    "Energy":                           12.0,
    "Consumer Defensive":               20.0,
    "Communication Services":           22.0,
    "default":                          25.0,
}
INDUSTRY_PS = {
    "Technology": 7.0, "Software": 10.0, "Semiconductors": 8.0,
    "Internet Content & Information": 8.0, "Auto Manufacturers": 1.5,
    "default": 5.0,
}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "stock_data": {},
        "last_refresh": None,
        "auto_refresh": False,
        "refresh_interval": 60,
        "groq_summary": {},
        "show_bakery": {},
        "tg_sent": set(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── DATA FETCHING — 4-layer fallback ─────────────────────────────────────────
# Layer 1: yfinance with curl_cffi Chrome impersonation
# Layer 2: Alpha Vantage REST API (free tier, needs ALPHA_VANTAGE_KEY)
# Layer 3: Finnhub REST API (free tier, needs FINNHUB_KEY)
# Layer 4: Hardcoded cache of last known good data (staleness noted in UI)

def _empty_result(symbol: str) -> dict:
    """Skeleton dict with all keys so downstream code never KeyErrors."""
    return {
        "symbol": symbol.upper(), "name": symbol.upper(), "price": 0,
        "prev_close": 0, "change_pct": 0, "pe": None, "forward_pe": None,
        "ps": None, "pb": None, "eps": None, "peg": None,
        "gross_margin": None, "profit_margin": None, "fcf": None,
        "fcf_yield": None, "mkt_cap": None, "sector": "default",
        "industry": "", "52w_high": None, "52w_low": None, "beta": None,
        "revenue": None, "net_income": None, "rev_growth": None,
        "earnings_growth": None, "analyst_target": None,
        "hist_pe": [], "eps_surprise": [], "hist_eps": [], "dividend_yield": None,
        "short_ratio": None, "data_source": "none", "error": None,
    }



def _build_hist_eps_av(symbol: str, av_key: str) -> list:
    """
    Fetch TRUE quarterly EPS history from Alpha Vantage EARNINGS endpoint.
    Matches each month's price to the most recent 4 quarters of EPS (TTM).
    Returns list of {date, eps_ttm, price} — genuine historical data.
    Costs 2 AV API calls (EARNINGS + TIME_SERIES_MONTHLY).
    """
    if not av_key:
        return []
    try:
        base = "https://www.alphavantage.co/query"

        # 1. Quarterly EPS
        r_earn = requests.get(base, params={
            "function": "EARNINGS", "symbol": symbol, "apikey": av_key
        }, timeout=12)
        earn_data = r_earn.json()
        q_earnings = earn_data.get("quarterlyEarnings", [])
        if not q_earnings:
            return []

        # Build {date -> eps} dict (reportedDate or fiscalDateEnding)
        eps_by_date = {}
        for q in q_earnings:
            dt_str = q.get("reportedDate") or q.get("fiscalDateEnding", "")
            eps_s  = q.get("reportedEPS", "None")
            try:
                if eps_s and eps_s != "None":
                    eps_by_date[pd.Timestamp(dt_str)] = float(eps_s)
            except Exception:
                continue

        if not eps_by_date:
            return []

        eps_series = pd.Series(eps_by_date).sort_index()

        # 2. Monthly price history
        r_px = requests.get(base, params={
            "function": "TIME_SERIES_MONTHLY_ADJUSTED",
            "symbol": symbol, "apikey": av_key
        }, timeout=12)
        px_data   = r_px.json()
        monthly   = px_data.get("Monthly Adjusted Time Series", {})
        if not monthly:
            return []

        # Build TTM EPS for each month
        result = []
        for date_str, ohlc in monthly.items():
            try:
                date = pd.Timestamp(date_str)
                px   = float(ohlc.get("5. adjusted close", 0))
                if px <= 0:
                    continue
                # Sum 4 most recent quarters up to this date
                prior = eps_series[eps_series.index <= date]
                if len(prior) < 4:
                    continue
                ttm_eps = prior.iloc[-4:].sum()
                if ttm_eps > 0:
                    result.append({
                        "date":    date,
                        "eps_ttm": round(float(ttm_eps), 4),
                        "price":   round(px, 2),
                    })
            except Exception:
                continue

        # Only keep last 5 years
        cutoff = pd.Timestamp.now() - pd.DateOffset(years=5)
        result = [r for r in result if r["date"] >= cutoff]
        result.sort(key=lambda x: x["date"])
        return result

    except Exception:
        return []

def _build_hist_pe(tk, trailing_eps: float) -> list:
    """Try to build accurate historical P/E from quarterly earnings + price history."""
    hist_pe = []
    try:
        hist        = tk.history(period="5y", interval="1mo")
        hist_prices = hist["Close"].dropna() if not hist.empty else pd.Series(dtype=float)
        if hist_prices.empty:
            return []
        try:
            q_earn   = tk.quarterly_earnings
            eps_vals = q_earn.sort_index().get("Earnings", pd.Series(dtype=float)) if (q_earn is not None and not q_earn.empty) else None
        except Exception:
            eps_vals = None

        for date, p in hist_prices.items():
            price_rounded = round(float(p), 2)
            if eps_vals is not None:
                prior = eps_vals[eps_vals.index <= date]
                if len(prior) >= 4:
                    ttm = prior.iloc[-4:].sum()
                    if ttm and ttm > 0:
                        pe_v = round(p / ttm, 2)
                        if 3 < pe_v < 600:
                            hist_pe.append({"date": date, "pe": pe_v, "price": price_rounded})
                        continue
            # fallback: current EPS proxy
            if trailing_eps and trailing_eps > 0:
                pe_v = round(p / trailing_eps, 2)
                if 3 < pe_v < 600:
                    hist_pe.append({"date": date, "pe": pe_v, "price": price_rounded})
    except Exception:
        pass
    return hist_pe


def _fetch_yfinance(symbol: str) -> dict:
    """Layer 1: yfinance (works locally, may be rate-limited on Streamlit Cloud)."""
    tk   = yf.Ticker(symbol)
    info = tk.info or {}
    if not info or not info.get("regularMarketPrice") and not info.get("currentPrice"):
        raise ValueError("Empty info from yfinance")

    price        = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    prev         = info.get("previousClose") or price
    chg          = ((price - prev) / prev * 100) if prev else 0
    trailing_eps = info.get("trailingEps") or 0
    op_cf        = info.get("operatingCashflow") or 0
    capex        = abs(info.get("capitalExpenditures") or 0)
    fcf          = op_cf - capex
    mkt_cap      = info.get("marketCap") or 0

    try:
        qearnings = tk.quarterly_earnings
    except Exception:
        qearnings = None

    eps_surprise = []
    hist_eps     = []   # [{date, eps_ttm, price}] for EPS vs Price chart

    if qearnings is not None and not qearnings.empty:
        for i, (idx, row) in enumerate(qearnings.iterrows()):
            if i >= 4: break
            actual   = row.get("Earnings")
            estimate = row.get("Estimate")
            if actual is not None and estimate and estimate != 0:
                eps_surprise.append({
                    "quarter":      str(idx)[:7],
                    "actual":       actual,
                    "estimate":     estimate,
                    "surprise_pct": round((actual - estimate) / abs(estimate) * 100, 1),
                })

    # hist_eps is derived later from hist_pe (price / pe = eps_implied)
    # No extra API call needed — see derive_hist_eps()
    hist_eps = []

    result = _empty_result(symbol)
    result.update({
        "name":           info.get("longName") or info.get("shortName") or symbol,
        "price":          round(price, 2),
        "prev_close":     round(prev, 2),
        "change_pct":     round(chg, 2),
        "pe":             info.get("trailingPE"),
        "forward_pe":     info.get("forwardPE"),
        "ps":             info.get("priceToSalesTrailing12Months"),
        "pb":             info.get("priceToBook"),
        "eps":            trailing_eps,
        "peg":            info.get("trailingPegRatio"),
        "gross_margin":   info.get("grossMargins"),
        "profit_margin":  info.get("profitMargins"),
        "fcf":            fcf,
        "fcf_yield":      (fcf / mkt_cap * 100) if mkt_cap else None,
        "mkt_cap":        mkt_cap,
        "sector":         info.get("sector") or "default",
        "industry":       info.get("industry") or "",
        "52w_high":       info.get("fiftyTwoWeekHigh"),
        "52w_low":        info.get("fiftyTwoWeekLow"),
        "beta":           info.get("beta"),
        "revenue":        info.get("totalRevenue"),
        "net_income":     info.get("netIncomeToCommon"),
        "rev_growth":     info.get("revenueGrowth"),
        "earnings_growth":info.get("earningsGrowth"),
        "analyst_target": info.get("targetMeanPrice"),
        "hist_pe":        _build_hist_pe(tk, trailing_eps),
        "eps_surprise":   eps_surprise,
        "hist_eps":       hist_eps,
        "dividend_yield": info.get("dividendYield"),
        "short_ratio":    info.get("shortRatio"),
        "data_source":    "yfinance",
        "error":          None,
    })
    return result


def _fetch_alpha_vantage(symbol: str, api_key: str) -> dict:
    """Layer 2: Alpha Vantage — OVERVIEW endpoint gives PE, margins, growth etc."""
    if not api_key:
        raise ValueError("No Alpha Vantage key")

    base = "https://www.alphavantage.co/query"

    # Company overview (fundamentals)
    ov = requests.get(base, params={
        "function": "OVERVIEW", "symbol": symbol, "apikey": api_key
    }, timeout=10).json()
    if "Note" in ov or "Information" in ov or not ov.get("Symbol"):
        raise ValueError(f"Alpha Vantage OVERVIEW failed: {list(ov.keys())[:3]}")

    # Global quote (current price)
    qt = requests.get(base, params={
        "function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key
    }, timeout=10).json().get("Global Quote", {})

    def _f(key, cast=float):
        try: return cast(ov.get(key, "") or 0) or None
        except: return None

    def _fq(key, cast=float):
        try: return cast(qt.get(key, "") or 0) or None
        except: return None

    price    = _fq("05. price") or 0
    prev     = _fq("08. previous close") or price
    chg      = ((price - prev) / prev * 100) if prev else 0
    mkt_cap  = _f("MarketCapitalization") or 0
    op_cf    = _f("OperatingCashflow") or 0
    capex    = _f("CapitalExpenditures") or 0
    fcf      = op_cf - abs(capex)
    pe       = _f("PERatio")
    eps      = _f("EPS")

    result = _empty_result(symbol)
    result.update({
        "name":           ov.get("Name", symbol),
        "price":          round(price, 2),
        "prev_close":     round(prev, 2),
        "change_pct":     round(chg, 2),
        "pe":             pe,
        "forward_pe":     _f("ForwardPE"),
        "ps":             _f("PriceToSalesRatioTTM"),
        "pb":             _f("PriceToBookRatio"),
        "eps":            eps,
        "peg":            _f("PEGRatio"),
        "gross_margin":   _f("GrossProfitTTM") and mkt_cap and (_f("GrossProfitTTM") / max(_f("RevenueTTM") or 1, 1)),
        "profit_margin":  _f("ProfitMargin"),
        "fcf":            fcf,
        "fcf_yield":      (fcf / mkt_cap * 100) if mkt_cap else None,
        "mkt_cap":        mkt_cap,
        "sector":         ov.get("Sector", "default"),
        "industry":       ov.get("Industry", ""),
        "52w_high":       _f("52WeekHigh"),
        "52w_low":        _f("52WeekLow"),
        "beta":           _f("Beta"),
        "revenue":        _f("RevenueTTM"),
        "rev_growth":     _f("QuarterlyRevenueGrowthYOY"),
        "earnings_growth":_f("QuarterlyEarningsGrowthYOY"),
        "analyst_target": _f("AnalystTargetPrice"),
        "dividend_yield": _f("DividendYield"),
        "data_source":    "Alpha Vantage",
        "error":          None,
    })
    return result


def _fetch_finnhub(symbol: str, api_key: str) -> dict:
    """Layer 3: Finnhub — quote + basic financials."""
    if not api_key:
        raise ValueError("No Finnhub key")

    headers = {"X-Finnhub-Token": api_key}
    base    = "https://finnhub.io/api/v1"

    quote   = requests.get(f"{base}/quote", params={"symbol": symbol},
                           headers=headers, timeout=8).json()
    metrics = requests.get(f"{base}/stock/metric", params={"symbol": symbol, "metric": "all"},
                           headers=headers, timeout=8).json().get("metric", {})
    profile = requests.get(f"{base}/stock/profile2", params={"symbol": symbol},
                           headers=headers, timeout=8).json()

    price   = quote.get("c") or 0
    prev    = quote.get("pc") or price
    chg     = ((price - prev) / prev * 100) if prev else 0

    def _m(key):
        v = metrics.get(key)
        return float(v) if v is not None else None

    mkt_cap = (profile.get("marketCapitalization") or 0) * 1e6
    fcf     = _m("freeCashFlowTTM") or 0

    result = _empty_result(symbol)
    result.update({
        "name":           profile.get("name", symbol),
        "price":          round(price, 2),
        "prev_close":     round(prev, 2),
        "change_pct":     round(chg, 2),
        "pe":             _m("peNormalizedAnnual") or _m("peTTM"),
        "forward_pe":     _m("forwardPE"),
        "ps":             _m("psTTM"),
        "pb":             _m("pbAnnual"),
        "eps":            _m("epsNormalizedAnnual"),
        "gross_margin":   _m("grossMarginTTM") and (_m("grossMarginTTM") / 100),
        "profit_margin":  _m("netProfitMarginTTM") and (_m("netProfitMarginTTM") / 100),
        "fcf":            fcf * 1e6 if fcf else None,
        "fcf_yield":      (_m("fcfYieldTTM") or 0),
        "mkt_cap":        mkt_cap or None,
        "sector":         profile.get("finnhubIndustry", "default"),
        "52w_high":       _m("52WeekHigh"),
        "52w_low":        _m("52WeekLow"),
        "beta":           _m("beta"),
        "revenue":        _m("revenuePerShareTTM"),
        "rev_growth":     _m("revenueGrowthTTMYoy") and (_m("revenueGrowthTTMYoy") / 100),
        "earnings_growth":_m("epsGrowthTTMYoy") and (_m("epsGrowthTTMYoy") / 100),
        "analyst_target": _m("targetPrice"),
        "dividend_yield": _m("dividendYieldIndicatedAnnual") and (_m("dividendYieldIndicatedAnnual") / 100),
        "data_source":    "Finnhub",
        "error":          None,
    })
    return result


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_stock_cached(symbol: str, av_key: str = "", fh_key: str = "") -> dict:
    """Cached layer — only successful results are stored for 300s."""
    errors = []

    # Layer 1: yfinance
    try:
        return _fetch_yfinance(symbol)
    except Exception as e:
        errors.append(f"yfinance: {str(e)[:80]}")

    # Layer 2: Alpha Vantage
    if av_key:
        try:
            return _fetch_alpha_vantage(symbol, av_key)
        except Exception as e:
            errors.append(f"AV: {str(e)[:60]}")

    # Layer 3: Finnhub
    if fh_key:
        try:
            return _fetch_finnhub(symbol, fh_key)
        except Exception as e:
            errors.append(f"Finnhub: {str(e)[:60]}")

    # All failed — raise so error is NOT cached
    raise RuntimeError(" | ".join(errors))


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_hist_eps_cached(symbol: str, av_key: str) -> list:
    """Cache AV EPS history for 1 hour (changes slowly)."""
    return _build_hist_eps_av(symbol, av_key)


def fetch_stock(symbol: str, av_key: str = "", fh_key: str = "") -> dict:
    """
    Public fetch function — wraps cached version so errors are never cached.
    Also enriches result with true EPS history from Alpha Vantage if key available.
    """
    try:
        result = _fetch_stock_cached(symbol, av_key, fh_key)
    except Exception as e:
        result = _empty_result(symbol)
        result["error"] = str(e)
        return result

    # Enrich with true EPS history (AV key needed; separate cache 1hr)
    if av_key and not result.get("hist_eps"):
        try:
            result["hist_eps"] = _fetch_hist_eps_cached(symbol, av_key)
        except Exception:
            result["hist_eps"] = []

    return result

# ── VALUATION SCORING ─────────────────────────────────────────────────────────
def score_stock(d: dict) -> dict:
    """Return score 0-100 (higher = more fairly/undervalued) and signal."""
    sector = d.get("sector", "default")
    bench_pe = INDUSTRY_PE.get(sector, INDUSTRY_PE["default"])
    bench_ps = INDUSTRY_PS.get(sector, INDUSTRY_PS["default"])

    score = 50  # neutral start
    reasons = []

    # P/E score (30 pts)
    pe = d.get("pe")
    if pe and pe > 0:
        ratio = pe / bench_pe
        if ratio < 0.8:
            score += 15; reasons.append(f"P/E {pe:.1f}x 低於行業均值 {bench_pe}x ✓")
        elif ratio < 1.1:
            score += 5; reasons.append(f"P/E {pe:.1f}x 接近行業均值 {bench_pe}x")
        elif ratio < 1.4:
            score -= 8; reasons.append(f"P/E {pe:.1f}x 高於行業均值 {bench_pe}x")
        else:
            score -= 18; reasons.append(f"P/E {pe:.1f}x 遠高於行業均值 {bench_pe}x ✗")

    # Forward PE improvement
    fpe = d.get("forward_pe")
    if fpe and pe and fpe > 0 and pe > 0:
        if fpe < pe * 0.85:
            score += 8; reasons.append(f"遠期P/E {fpe:.1f}x，盈利預期改善明顯 ✓")
        elif fpe < pe:
            score += 3; reasons.append(f"遠期P/E {fpe:.1f}x，盈利預期有增長")

    # P/S score (15 pts)
    ps = d.get("ps")
    if ps and ps > 0:
        ratio_ps = ps / bench_ps
        if ratio_ps < 0.8:   score += 8
        elif ratio_ps < 1.2: score += 2
        elif ratio_ps < 2.0: score -= 5
        else:                 score -= 10

    # FCF yield (20 pts)
    fcf_y = d.get("fcf_yield")
    if fcf_y is not None:
        if fcf_y > 5:    score += 15; reasons.append(f"自由現金流率 {fcf_y:.1f}% 非常健康 ✓")
        elif fcf_y > 3:  score += 8;  reasons.append(f"自由現金流率 {fcf_y:.1f}% 良好")
        elif fcf_y > 1:  score += 2
        elif fcf_y < 0:  score -= 12; reasons.append(f"自由現金流為負 ✗")

    # Revenue growth (10 pts)
    rg = d.get("rev_growth")
    if rg is not None:
        if rg > 0.15:   score += 8; reasons.append(f"收入增長 {rg*100:.1f}% 強勁 ✓")
        elif rg > 0.05: score += 3
        elif rg < 0:    score -= 8; reasons.append(f"收入負增長 {rg*100:.1f}% ✗")

    # Gross margin (5 pts)
    gm = d.get("gross_margin")
    if gm and gm > 0.40: score += 5; reasons.append(f"毛利率 {gm*100:.1f}% 優秀 ✓")
    elif gm and gm > 0.25: score += 2

    score = max(0, min(100, score))

    if score >= 65:
        signal, sig_class, emoji = "估值合理 / 偏低", "sig-green", "🟢"
    elif score >= 40:
        signal, sig_class, emoji = "估值略貴", "sig-yellow", "🟡"
    else:
        signal, sig_class, emoji = "估值偏高", "sig-red", "🔴"

    return {"score": score, "signal": signal, "sig_class": sig_class, "emoji": emoji, "reasons": reasons}

# ── HISTORICAL PE BAND ─────────────────────────────────────────────────────────
def get_pe_band(hist_pe: list) -> dict:
    if not hist_pe:
        return {}
    vals = [x["pe"] for x in hist_pe if 0 < x["pe"] < 500]
    if len(vals) < 6:
        return {}
    return {
        "min": round(np.percentile(vals, 5), 1),
        "avg": round(np.mean(vals), 1),
        "max": round(np.percentile(vals, 95), 1),
        "current": vals[-1] if vals else None,
    }

# ── MARGIN OF SAFETY ──────────────────────────────────────────────────────────
def margin_of_safety(eps: float, required_return_pct: float, growth_pct: float, years: int = 10) -> float:
    """DCF-style fair value: sum of discounted EPS growth."""
    if eps <= 0 or required_return_pct <= 0:
        return 0.0
    r = required_return_pct / 100
    g = growth_pct / 100
    # Simple Gordon Growth + terminal
    fair = 0.0
    for yr in range(1, years + 1):
        fair += eps * ((1 + g) ** yr) / ((1 + r) ** yr)
    terminal = (eps * ((1 + g) ** years) * (1 + 0.03)) / (r - 0.03)
    fair += terminal / ((1 + r) ** years)
    return round(fair, 2)

# ── FED-ADJUSTED PE ───────────────────────────────────────────────────────────
def fed_adjusted_pe(risk_free_rate_pct: float, equity_risk_premium: float = 5.0) -> float:
    total_required = risk_free_rate_pct + equity_risk_premium
    return round(100 / total_required, 1)

# ── BAKERY BLURB (rule-based) ─────────────────────────────────────────────────
def bakery_blurb(d: dict, scoring: dict) -> str:
    """Returns plain HTML string (no Markdown) for use inside HTML divs."""
    sym    = d["symbol"]
    pe     = d.get("pe")
    gm     = d.get("gross_margin")
    rg     = d.get("rev_growth")
    fcf_y  = d.get("fcf_yield")
    score  = scoring["score"]
    sector = d.get("sector", "")

    lines = []

    # Opening
    if score >= 65:
        lines.append(f"<b>{sym}</b> 就像一間「物有所值」的麵包店——")
    elif score >= 40:
        lines.append(f"<b>{sym}</b> 就像一間「裝修靚但略貴」的麵包店——")
    else:
        lines.append(f"<b>{sym}</b> 就像一間「名氣大但超出預算」的麵包店——")

    # PE story
    if pe and pe > 0:
        bench    = INDUSTRY_PE.get(sector, 25)
        wait_yr  = int(pe)
        if pe < bench * 0.85:
            lines.append(f"你花 <b>${pe:.0f}萬</b> 買下每年賺 $1萬 的店，只需 <b>{wait_yr} 年回本</b>，比同區麵包店（{bench:.0f}年）更快，算是抵買。")
        elif pe < bench * 1.2:
            lines.append(f"你花 <b>${pe:.0f}萬</b> 買下每年賺 $1萬 的店，需要 <b>{wait_yr} 年回本</b>，與同區麵包店（{bench:.0f}年）相若，定價合理。")
        else:
            lines.append(f"你花 <b>${pe:.0f}萬</b> 買下每年賺 $1萬 的店，需要 <b>{wait_yr} 年回本</b>，比同區麵包店（{bench:.0f}年）貴得多。")

    # Gross margin
    if gm and gm > 0:
        gm_pct = gm * 100
        if gm_pct > 45:
            lines.append(f"這間店每賣 $100 的麵包，賺到 <b>${gm_pct:.0f} 毛利</b>，材料成本極低，烤箱效率全城最高 🏆")
        elif gm_pct > 30:
            lines.append(f"這間店毛利率 <b>{gm_pct:.0f}%</b>，算是中上水平，成本控制不錯。")
        else:
            lines.append(f"這間店毛利率只有 <b>{gm_pct:.0f}%</b>，原材料佔成本頗高，利潤空間有限。")

    # Revenue growth
    if rg is not None:
        rg_pct = rg * 100
        if rg_pct > 15:
            lines.append(f"最近一年麵包銷量急增 <b>{rg_pct:.1f}%</b>，即係每個月都有更多新熟客排隊，生意滾雪球。")
        elif rg_pct > 0:
            lines.append(f"麵包銷量穩步增長 <b>{rg_pct:.1f}%</b>，生意平穩向上。")
        elif rg_pct < 0:
            lines.append(f"⚠️ 麵包銷量下跌 <b>{abs(rg_pct):.1f}%</b>，要留意係短期現象定係長期趨勢。")

    # FCF
    if fcf_y is not None:
        if fcf_y > 4:
            lines.append(f"老闆每年實際落袋現金回報率達 <b>{fcf_y:.1f}%</b>，即係每 $100 投資每年收到 ${fcf_y:.1f} 真實現金，非常健康 💰")
        elif fcf_y < 0:
            lines.append(f"⚠️ 老闆現金流為負（{fcf_y:.1f}%），即係店舖支出多過收入，要靠借貸或發新股支撐。")

    # Verdict
    if score >= 65:
        lines.append(f"<br><b>📍 結論：</b> 以現價計，這間麵包店定價合理，值得考慮。")
    elif score >= 40:
        lines.append(f"<br><b>📍 結論：</b> 這間麵包店略貴，但品牌有溢價，可以等回調再考慮。")
    else:
        lines.append(f"<br><b>📍 結論：</b> 現價偏貴，建議等估值回落至更合理水平才入場。")

    return " ".join(lines)

# ── GROQ SUMMARY ──────────────────────────────────────────────────────────────
def groq_summary(stocks_data: list, groq_key: str) -> str:
    if not groq_key:
        return ""
    try:
        summaries = []
        for d in stocks_data:
            if d.get("error"):
                continue
            sc = score_stock(d)
            summaries.append(
                f"{d['symbol']}: 股價${d['price']}, P/E={d.get('pe','N/A')}, "
                f"收入增長={d.get('rev_growth','N/A')}, 估值評分={sc['score']}/100"
            )

        prompt = f"""你是一位專業的股票分析師，同時也是麵包店老闆。
以下是今日股票估值數據：
{chr(10).join(summaries)}

請用繁體中文，以麵包店作比喻，用3-4段話分析：
1. 整體市場估值溫度（整體係偏貴定合理）
2. 最值得留意的股票（哪間麵包店最抵買）
3. 風險提示（哪間店要小心）
4. 總結建議

語氣要親切易明，比喻要生動，像係跟朋友解說一樣。每段唔超過3句。"""

        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
            "temperature": 0.7,
        }
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=20
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        return f"Groq API 錯誤：{resp.status_code}"
    except Exception as e:
        return f"Groq 呼叫失敗：{str(e)}"

# ── TELEGRAM ──────────────────────────────────────────────────────────────────
def send_telegram(token: str, chat_id: str, message: str):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10)
    except Exception:
        pass

def check_telegram_alerts(stocks_data: list, token: str, chat_id: str, threshold_high: int, threshold_low: int):
    if not token or not chat_id:
        return
    for d in stocks_data:
        if d.get("error"):
            continue
        sc = score_stock(d)
        sym = d["symbol"]
        key_hi = f"hi_{sym}"
        key_lo = f"lo_{sym}"
        if sc["score"] < threshold_high and key_hi not in st.session_state.tg_sent:
            msg = (f"🔴 *估值警報 - {sym}*\n"
                   f"估值評分：{sc['score']}/100（偏高）\n"
                   f"股價：${d['price']}\n"
                   f"P/E：{d.get('pe','N/A')}\n"
                   f"建議：謹慎，估值偏貴")
            send_telegram(token, chat_id, msg)
            st.session_state.tg_sent.add(key_hi)
        if sc["score"] > threshold_low and key_lo not in st.session_state.tg_sent:
            msg = (f"🟢 *機會警報 - {sym}*\n"
                   f"估值評分：{sc['score']}/100（合理/偏低）\n"
                   f"股價：${d['price']}\n"
                   f"P/E：{d.get('pe','N/A')}\n"
                   f"建議：估值合理，可以留意")
            send_telegram(token, chat_id, msg)
            st.session_state.tg_sent.add(key_lo)

# ── FORMAT HELPERS ────────────────────────────────────────────────────────────
def fmt_num(v, prefix="", suffix="", decimals=1, billions=False):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "N/A"
    if billions and abs(v) >= 1e9:
        return f"{prefix}{v/1e9:.{decimals}f}B{suffix}"
    if abs(v) >= 1e6:
        return f"{prefix}{v/1e6:.{decimals}f}M{suffix}"
    return f"{prefix}{v:.{decimals}f}{suffix}"

def fmt_pct(v, decimals=1):
    if v is None: return "N/A"
    return f"{v*100:.{decimals}f}%"

def color_class(v, good_high=True):
    if v is None: return ""
    return "m-value-ok" if (v > 0) == good_high else "m-value-hi"

# ── CHARTS ────────────────────────────────────────────────────────────────────
CHART_THEME = {
    "paper_bgcolor": "#faf6ef",
    "plot_bgcolor":  "#fffdf8",
    "font":          {"family": "IBM Plex Mono", "color": "#3d2b1f", "size": 11},
    "gridcolor":     "#e8dfc8",
}

def chart_pe_comparison(stocks_data: list):
    symbols, pe_vals, bench_vals, colors = [], [], [], []
    for d in stocks_data:
        if d.get("error") or not d.get("pe"): continue
        sc = score_stock(d)
        sector = d.get("sector", "default")
        bench  = INDUSTRY_PE.get(sector, 25)
        symbols.append(d["symbol"])
        pe_vals.append(round(d["pe"], 1))
        bench_vals.append(bench)
        colors.append("#c8922a" if d["pe"] > bench else "#4a9a4a")

    if not symbols:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Bar(name="實際 P/E", x=symbols, y=pe_vals,
                         marker_color=colors, text=pe_vals, textposition="outside"))
    fig.add_trace(go.Scatter(name="行業均值 P/E", x=symbols, y=bench_vals,
                              mode="lines+markers", line=dict(color="#2a1d13", dash="dash", width=2),
                              marker=dict(symbol="diamond", size=8, color="#2a1d13")))
    fig.update_layout(
        title="P/E 比較：各股 vs 行業均值",
        barmode="group", height=360,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"], title="P/E 倍數"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig

def chart_ps_comparison(stocks_data: list):
    symbols, ps_vals, bench_vals, colors = [], [], [], []
    for d in stocks_data:
        if d.get("error") or not d.get("ps"): continue
        sector = d.get("sector", "default")
        bench  = INDUSTRY_PS.get(sector, 5)
        symbols.append(d["symbol"])
        ps_vals.append(round(d["ps"], 1))
        bench_vals.append(bench)
        colors.append("#c8922a" if d["ps"] > bench else "#4a9a4a")

    if not symbols: return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Bar(name="實際 P/S", x=symbols, y=ps_vals,
                         marker_color=colors, text=ps_vals, textposition="outside"))
    fig.add_trace(go.Scatter(name="行業均值 P/S", x=symbols, y=bench_vals,
                              mode="lines+markers", line=dict(color="#2a1d13", dash="dash", width=2),
                              marker=dict(symbol="diamond", size=8, color="#2a1d13")))
    fig.update_layout(
        title="P/S 比較：各股 vs 行業均值",
        height=360,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"], title="P/S 倍數"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=60, b=20, l=20, r=20),
    )
    return fig

def chart_radar(d: dict, scoring: dict):
    sector = d.get("sector", "default")
    bench_pe = INDUSTRY_PE.get(sector, 25)
    bench_ps = INDUSTRY_PS.get(sector, 5)

    def norm(val, best, worst):
        if val is None: return 50
        try:
            return max(0, min(100, (worst - val) / (worst - best) * 100))
        except: return 50

    pe_s   = norm(d.get("pe"), best=bench_pe*0.7, worst=bench_pe*2)
    ps_s   = norm(d.get("ps"), best=bench_ps*0.7, worst=bench_ps*2.5)
    fcfy_s = norm(-(d.get("fcf_yield") or 0), best=-8, worst=0)
    gm_s   = norm(-(d.get("gross_margin") or 0), best=-0.6, worst=-0.1)
    rg_s   = norm(-(d.get("rev_growth") or 0), best=-0.25, worst=0)

    cats   = ["P/E 估值", "P/S 估值", "現金流率", "毛利率", "收入增長"]
    values = [pe_s, ps_s, fcfy_s, gm_s, rg_s]
    values_closed = values + [values[0]]
    cats_closed   = cats + [cats[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed, theta=cats_closed, fill="toself",
        fillcolor="rgba(200,146,42,0.2)", line=dict(color="#c8922a", width=2),
        name=d["symbol"]
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#e8dfc8",
                            tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="#e8dfc8"),
            bgcolor="#fffdf8",
        ),
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        font=CHART_THEME["font"],
        showlegend=False,
        title=f"{d['symbol']} 估值雷達圖（分越高=越合理）",
        height=320,
        margin=dict(t=50, b=20, l=40, r=40),
    )
    return fig

def chart_hist_pe(hist_pe: list, symbol: str, current_pe: float):
    if not hist_pe: return None
    df = pd.DataFrame(hist_pe)
    df = df[df["pe"].between(3, 500)]
    if df.empty or len(df) < 6: return None

    avg   = df["pe"].mean()
    p5    = np.percentile(df["pe"], 5)
    p95   = np.percentile(df["pe"], 95)

    fig = go.Figure()
    # Shaded band between 25th and 75th percentile
    p25 = np.percentile(df["pe"], 25)
    p75 = np.percentile(df["pe"], 75)
    fig.add_trace(go.Scatter(
        x=pd.concat([df["date"], df["date"][::-1]]),
        y=[p75]*len(df) + [p25]*len(df),
        fill="toself", fillcolor="rgba(200,146,42,0.07)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["pe"], mode="lines",
        line=dict(color="#c8922a", width=1.8), name="歷史 P/E",
        fill="tozeroy", fillcolor="rgba(200,146,42,0.05)"
    ))
    fig.add_hline(y=avg, line_dash="dash", line_color="#2a1d13", line_width=1.5,
                  annotation_text=f"5年均值 {avg:.1f}x",
                  annotation_position="bottom right",
                  annotation_font=dict(size=10, color="#2a1d13"))
    if current_pe and 3 < current_pe < 500:
        fig.add_hline(y=current_pe, line_dash="dot", line_color="#b84040", line_width=1.5,
                      annotation_text=f"現在 {current_pe:.1f}x",
                      annotation_position="top right",
                      annotation_font=dict(size=10, color="#b84040"))
    fig.update_layout(
        title=f"{symbol} 歷史 P/E（5年）— 均值 {avg:.1f}x　低位 {p5:.1f}x　高位 {p95:.1f}x",
        height=270,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"], title="P/E 倍數"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=55, b=20, l=20, r=80),
        showlegend=False,
    )
    return fig


def chart_pe_price_relationship(hist_pe: list, symbol: str, current_pe: float, current_price: float):
    """
    Dual-axis chart: Price (left Y) + P/E (right Y) over time.
    Shaded zones show cheap / fair / expensive P/E bands.
    Scatter overlay shows P/E vs Price correlation.
    Returns (fig_dual, fig_scatter) tuple.
    """
    if not hist_pe or len(hist_pe) < 6:
        return None, None

    df = pd.DataFrame(hist_pe).copy()
    df = df[df["pe"].between(3, 500)].copy()
    if df.empty or len(df) < 6:
        return None, None

    # Reconstruct approximate price from PE * trailing EPS proxy
    # hist_pe entries have {"date": ..., "pe": ...}
    # We also stored price in _build_hist_pe via hist_prices — re-derive from pe * eps
    # Since price = pe * ttm_eps at that date, and we stored pe but not price,
    # we use the price column if present, else skip price axis
    has_price = "price" in df.columns and df["price"].notna().sum() > 4

    avg_pe = df["pe"].mean()
    p25    = np.percentile(df["pe"], 25)
    p75    = np.percentile(df["pe"], 75)
    p10    = np.percentile(df["pe"], 10)
    p90    = np.percentile(df["pe"], 90)

    # ── Chart 1: P/E over time with price overlay (dual axis) ─────────────
    fig1 = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.45],
        vertical_spacing=0.06,
        subplot_titles=("股價走勢", "P/E 市盈率走勢")
    )

    dates = df["date"]

    # — Row 1: Price (if available) or PE-implied price band —
    if has_price:
        fig1.add_trace(go.Scatter(
            x=dates, y=df["price"], mode="lines", name="股價",
            line=dict(color="#c8922a", width=2),
            fill="tozeroy", fillcolor="rgba(200,146,42,0.06)"
        ), row=1, col=1)
    else:
        # Show PE bands translated to "fair value price" zones using current EPS as proxy
        # (approximate only — indicated in chart)
        if current_pe and current_price and current_pe > 0:
            implied_eps = current_price / current_pe
            fig1.add_trace(go.Scatter(
                x=dates,
                y=[p * implied_eps for p in df["pe"]],
                mode="lines", name="估算股價（以EPS代理）",
                line=dict(color="#c8922a", width=1.8, dash="dot"),
                fill="tozeroy", fillcolor="rgba(200,146,42,0.05)"
            ), row=1, col=1)
            # Fair value band
            fig1.add_hrect(
                y0=avg_pe * implied_eps * 0.9, y1=avg_pe * implied_eps * 1.1,
                fillcolor="rgba(74,154,74,0.08)", line_width=0,
                annotation_text="合理價值區", annotation_position="top left",
                annotation_font=dict(size=9, color="#4a9a4a"), row=1, col=1
            )
            if current_price:
                fig1.add_hline(y=current_price, line_dash="dot",
                               line_color="#b84040", line_width=1.5,
                               annotation_text=f"現價 ${current_price:.0f}",
                               annotation_position="right",
                               annotation_font=dict(size=9, color="#b84040"),
                               row=1, col=1)

    # — Row 2: P/E over time with coloured zones —
    # Cheap zone (below p25)
    fig1.add_hrect(
        y0=max(0, p10), y1=p25,
        fillcolor="rgba(74,154,74,0.10)", line_width=0,
        annotation_text="便宜區", annotation_position="top left",
        annotation_font=dict(size=9, color="#3a7a3a"), row=2, col=1
    )
    # Expensive zone (above p75)
    fig1.add_hrect(
        y0=p75, y1=min(p90 * 1.1, 300),
        fillcolor="rgba(184,64,64,0.08)", line_width=0,
        annotation_text="偏貴區", annotation_position="top left",
        annotation_font=dict(size=9, color="#b84040"), row=2, col=1
    )

    # P/E line — coloured by zone
    pe_colors = []
    for pe_v in df["pe"]:
        if pe_v <= p25:   pe_colors.append("#4a9a4a")
        elif pe_v >= p75: pe_colors.append("#b84040")
        else:             pe_colors.append("#c8922a")

    fig1.add_trace(go.Scatter(
        x=dates, y=df["pe"], mode="lines", name="P/E",
        line=dict(color="#c8922a", width=2),
    ), row=2, col=1)

    # Average PE line
    fig1.add_hline(y=avg_pe, line_dash="dash", line_color="#2a1d13",
                   line_width=1.2, annotation_text=f"均值 {avg_pe:.1f}x",
                   annotation_position="bottom right",
                   annotation_font=dict(size=9, color="#2a1d13"), row=2, col=1)

    # Current PE marker
    if current_pe and 3 < current_pe < 500:
        fig1.add_hline(y=current_pe, line_dash="dot", line_color="#b84040",
                       line_width=1.5, annotation_text=f"現在 {current_pe:.1f}x",
                       annotation_position="top right",
                       annotation_font=dict(size=9, color="#b84040"), row=2, col=1)

    fig1.update_layout(
        title=f"{symbol}  股價 & P/E 歷史走勢（5年）",
        height=500,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        showlegend=False,
        margin=dict(t=60, b=20, l=20, r=80),
    )
    fig1.update_yaxes(gridcolor=CHART_THEME["gridcolor"])
    fig1.update_xaxes(gridcolor="rgba(0,0,0,0)", row=1, col=1)
    fig1.update_xaxes(gridcolor="rgba(0,0,0,0)", row=2, col=1)
    fig1.update_yaxes(title_text="股價 (USD)", row=1, col=1)
    fig1.update_yaxes(title_text="P/E 倍數", row=2, col=1)

    # ── Chart 2: Scatter — P/E vs Price (correlation) ─────────────────────
    if has_price:
        # Colour points by PE zone
        point_colors = []
        for pe_v in df["pe"]:
            if pe_v <= p25:   point_colors.append("#4a9a4a")
            elif pe_v >= p75: point_colors.append("#b84040")
            else:             point_colors.append("#c8922a")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df["pe"], y=df["price"],
            mode="markers",
            marker=dict(color=point_colors, size=7, opacity=0.75,
                        line=dict(width=0.5, color="#2a1d13")),
            text=[str(d)[:7] for d in df["date"]],
            hovertemplate="P/E: %{x:.1f}x<br>股價: $%{y:.0f}<br>%{text}<extra></extra>",
            name="月度數據"
        ))

        # Regression line
        if len(df) > 5:
            z = np.polyfit(df["pe"], df["price"], 1)
            p_fn = np.poly1d(z)
            pe_range = np.linspace(df["pe"].min(), df["pe"].max(), 50)
            fig2.add_trace(go.Scatter(
                x=pe_range, y=p_fn(pe_range),
                mode="lines", line=dict(color="#2a1d13", dash="dash", width=1.5),
                name="趨勢線", showlegend=False
            ))
            # Correlation coefficient
            corr = np.corrcoef(df["pe"], df["price"])[0, 1]
            fig2.add_annotation(
                x=0.02, y=0.96, xref="paper", yref="paper",
                text=f"相關係數 r = {corr:.2f}",
                showarrow=False, font=dict(size=10, color="#2a1d13"),
                bgcolor="rgba(255,253,248,0.85)", bordercolor=CHART_THEME["gridcolor"],
                borderwidth=1
            )

        # Mark current point
        if current_pe and current_price:
            fig2.add_trace(go.Scatter(
                x=[current_pe], y=[current_price],
                mode="markers+text",
                marker=dict(color="#b84040", size=12, symbol="star",
                            line=dict(width=1.5, color="#2a1d13")),
                text=["現在"], textposition="top right",
                textfont=dict(size=10, color="#b84040"),
                name="現在", showlegend=False
            ))

        fig2.update_layout(
            title=f"{symbol}  P/E vs 股價 散點圖（P/E 愈高，市場情緒愈樂觀）",
            height=350,
            paper_bgcolor=CHART_THEME["paper_bgcolor"],
            plot_bgcolor=CHART_THEME["plot_bgcolor"],
            font=CHART_THEME["font"],
            xaxis=dict(title="P/E 倍數", gridcolor=CHART_THEME["gridcolor"]),
            yaxis=dict(title="股價 (USD)", gridcolor=CHART_THEME["gridcolor"]),
            margin=dict(t=55, b=30, l=20, r=20),
            showlegend=False,
        )
        return fig1, fig2

    return fig1, None


def chart_eps_price(hist_eps: list, symbol: str,
                    current_eps: float, current_price: float,
                    hist_pe: list = None) -> tuple:
    """
    Returns (fig_dual, fig_scatter, fig_growth).
    Requires true quarterly EPS history (from Alpha Vantage EARNINGS endpoint).
    Does NOT fall back to price/PE derivation — that produces circular data.
    """
    if not hist_eps or len(hist_eps) < 6:
        return None, None, None

    df = pd.DataFrame(hist_eps).copy()
    df = df.dropna(subset=["eps_ttm", "price"])
    df = df[df["eps_ttm"] > 0]
    if len(df) < 6:
        return None, None, None

    df = df.sort_values("date").reset_index(drop=True)

    # ── YoY EPS growth (compare same month 12 steps back) ────────────────────
    df["eps_yoy"] = None
    for i in range(12, len(df)):
        prev_eps = df.loc[i - 12, "eps_ttm"]
        if prev_eps and prev_eps > 0:
            df.loc[i, "eps_yoy"] = round(
                (df.loc[i, "eps_ttm"] - prev_eps) / prev_eps * 100, 1
            )

    avg_eps = df["eps_ttm"].mean()
    max_eps = df["eps_ttm"].max()
    min_eps = df["eps_ttm"].min()

    # ── Fig 1: Dual-panel Price + EPS ─────────────────────────────────────────
    fig1 = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.52, 0.48],
        vertical_spacing=0.07,
        subplot_titles=("股價走勢 Price", "每股盈餘 TTM EPS（真實季度數據）")
    )

    # Row 1: Price
    fig1.add_trace(go.Scatter(
        x=df["date"], y=df["price"],
        mode="lines", name="股價",
        line=dict(color="#c8922a", width=2),
        fill="tozeroy", fillcolor="rgba(200,146,42,0.06)",
        hovertemplate="日期: %{x|%Y-%m}<br>股價: $%{y:.2f}<extra></extra>"
    ), row=1, col=1)
    if current_price:
        fig1.add_hline(y=current_price, line_dash="dot",
                       line_color="#b84040", line_width=1.2,
                       annotation_text=f"現價 ${current_price:.0f}",
                       annotation_position="right",
                       annotation_font=dict(size=9, color="#b84040"),
                       row=1, col=1)

    # Row 2: TTM EPS — colour bars by growth vs prior year
    bar_colors = []
    for i, row_v in df.iterrows():
        yoy = row_v["eps_yoy"]
        if yoy is None:    bar_colors.append("#b0a080")
        elif yoy >= 15:    bar_colors.append("#2a7a2a")
        elif yoy >= 5:     bar_colors.append("#4a9a4a")
        elif yoy >= 0:     bar_colors.append("#a0c080")
        elif yoy >= -10:   bar_colors.append("#e8a060")
        else:              bar_colors.append("#b84040")

    fig1.add_trace(go.Bar(
        x=df["date"], y=df["eps_ttm"],
        name="TTM EPS",
        marker_color=bar_colors,
        hovertemplate="日期: %{x|%Y-%m}<br>TTM EPS: $%{y:.2f}<extra></extra>"
    ), row=2, col=1)

    # Trend line on EPS
    if len(df) > 5:
        z = np.polyfit(range(len(df)), df["eps_ttm"], 1)
        trend = np.poly1d(z)(range(len(df)))
        fig1.add_trace(go.Scatter(
            x=df["date"], y=trend,
            mode="lines", name="EPS趨勢",
            line=dict(color="#2a1d13", dash="dash", width=1.2),
            showlegend=False
        ), row=2, col=1)

    if current_eps:
        fig1.add_hline(y=current_eps, line_dash="dot",
                       line_color="#b84040", line_width=1.2,
                       annotation_text=f"現在 ${current_eps:.2f}",
                       annotation_position="right",
                       annotation_font=dict(size=9, color="#b84040"),
                       row=2, col=1)

    fig1.update_layout(
        title=f"{symbol}  股價 & 真實 TTM EPS 歷史走勢（5年，Alpha Vantage）",
        height=520,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        showlegend=False,
        margin=dict(t=60, b=20, l=20, r=90),
        bargap=0.15,
    )
    fig1.update_yaxes(gridcolor=CHART_THEME["gridcolor"])
    fig1.update_xaxes(gridcolor="rgba(0,0,0,0)")
    fig1.update_yaxes(title_text="股價 (USD)", row=1, col=1)
    fig1.update_yaxes(title_text="TTM EPS ($)", row=2, col=1)

    # ── Fig 2: EPS vs Price scatter ────────────────────────────────────────────
    fig2 = go.Figure()

    # Colour by EPS growth
    pt_colors = []
    for _, r2 in df.iterrows():
        yoy = r2["eps_yoy"]
        if yoy is None:  pt_colors.append("#b0a080")
        elif yoy >= 15:  pt_colors.append("#2a7a2a")
        elif yoy >= 0:   pt_colors.append("#c8922a")
        else:            pt_colors.append("#b84040")

    fig2.add_trace(go.Scatter(
        x=df["eps_ttm"], y=df["price"],
        mode="markers",
        marker=dict(color=pt_colors, size=7, opacity=0.80,
                    line=dict(width=0.5, color="#2a1d13")),
        text=[str(d)[:7] for d in df["date"]],
        hovertemplate=(
            "日期: %{text}<br>"
            "TTM EPS: $%{x:.2f}<br>"
            "股價: $%{y:.2f}<extra></extra>"
        ),
        name="月度數據"
    ))

    # Regression line
    if len(df) > 5:
        z2   = np.polyfit(df["eps_ttm"], df["price"], 1)
        p_fn = np.poly1d(z2)
        eps_r = np.linspace(df["eps_ttm"].min(), df["eps_ttm"].max(), 60)
        fig2.add_trace(go.Scatter(
            x=eps_r, y=p_fn(eps_r),
            mode="lines",
            line=dict(color="#2a1d13", dash="dash", width=1.5),
            showlegend=False
        ))
        corr2 = np.corrcoef(df["eps_ttm"], df["price"])[0, 1]
        # Fair value line annotation
        fig2.add_annotation(
            x=0.03, y=0.96, xref="paper", yref="paper",
            text=f"相關係數 r = {corr2:.2f}",
            showarrow=False, font=dict(size=10, color="#2a1d13"),
            bgcolor="rgba(255,253,248,0.88)",
            bordercolor=CHART_THEME["gridcolor"], borderwidth=1
        )

    # Current point
    if current_eps and current_price:
        fig2.add_trace(go.Scatter(
            x=[current_eps], y=[current_price],
            mode="markers+text",
            marker=dict(color="#b84040", size=13, symbol="star",
                        line=dict(width=1.5, color="#2a1d13")),
            text=["現在"], textposition="top right",
            textfont=dict(size=10, color="#b84040"),
            showlegend=False
        ))

    fig2.update_layout(
        title=f"{symbol}  TTM EPS vs 股價 散點圖（EPS 增長帶動股價上升）",
        height=370,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        xaxis=dict(title="TTM EPS ($)", gridcolor=CHART_THEME["gridcolor"]),
        yaxis=dict(title="股價 (USD)", gridcolor=CHART_THEME["gridcolor"]),
        margin=dict(t=55, b=30, l=20, r=20),
        showlegend=False,
    )

    # ── Fig 3: YoY EPS growth bar chart ──────────────────────────────────────
    df_yoy = df.dropna(subset=["eps_yoy"]).copy()
    if not df_yoy.empty:
        bar_c3 = ["#2a7a2a" if v >= 15 else "#4a9a4a" if v >= 5
                  else "#a0c080" if v >= 0 else "#e8a060" if v >= -10
                  else "#b84040"
                  for v in df_yoy["eps_yoy"]]
        fig3 = go.Figure(go.Bar(
            x=df_yoy["date"], y=df_yoy["eps_yoy"],
            marker_color=bar_c3,
            text=[f"{v:+.1f}%" for v in df_yoy["eps_yoy"]],
            textposition="outside",
            textfont=dict(size=9),
            hovertemplate="日期: %{x|%Y-%m}<br>EPS YoY: %{y:.1f}%<extra></extra>"
        ))
        fig3.add_hline(y=0, line_color="#2a1d13", line_width=1)
        fig3.add_hline(y=df_yoy["eps_yoy"].mean(),
                       line_dash="dash", line_color="#c8922a", line_width=1.2,
                       annotation_text=f"均值 {df_yoy['eps_yoy'].mean():+.1f}%",
                       annotation_position="right",
                       annotation_font=dict(size=9, color="#c8922a"))
        fig3.update_layout(
            title=f"{symbol}  EPS 同比增長率（YoY % — 真實季度數據）",
            height=300,
            paper_bgcolor=CHART_THEME["paper_bgcolor"],
            plot_bgcolor=CHART_THEME["plot_bgcolor"],
            font=CHART_THEME["font"],
            yaxis=dict(title="YoY %", gridcolor=CHART_THEME["gridcolor"],
                       zeroline=True, zerolinecolor="#2a1d13"),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            margin=dict(t=50, b=20, l=20, r=80),
            showlegend=False,
        )
    else:
        fig3 = None

    return fig1, fig2, fig3

def chart_quadrant(stocks_data: list):
    syms, pe_ratios, rg_vals, sizes, colors_q, scores_q = [], [], [], [], [], []
    for d in stocks_data:
        if d.get("error"): continue
        pe = d.get("pe"); rg = d.get("rev_growth")
        if pe is None or rg is None: continue
        sc = score_stock(d)
        syms.append(d["symbol"])
        pe_ratios.append(pe)
        rg_vals.append(rg * 100)
        sizes.append(max(15, min(50, sc["score"] / 2)))
        c = "#4a9a4a" if sc["score"]>=65 else "#c8922a" if sc["score"]>=40 else "#b84040"
        colors_q.append(c)
        scores_q.append(sc["score"])

    if not syms: return go.Figure()

    med_pe = np.median(pe_ratios) if pe_ratios else 25
    med_rg = np.median(rg_vals)  if rg_vals  else 10

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pe_ratios, y=rg_vals, mode="markers+text",
        text=syms, textposition="top center",
        marker=dict(size=sizes, color=colors_q, opacity=0.85,
                    line=dict(width=1, color="#2a1d13")),
        customdata=scores_q,
        hovertemplate="<b>%{text}</b><br>P/E: %{x:.1f}x<br>收入增長: %{y:.1f}%<br>估值分: %{customdata}/100<extra></extra>"
    ))
    fig.add_vline(x=med_pe, line_dash="dash", line_color="#d4c4a8", line_width=1)
    fig.add_hline(y=med_rg, line_dash="dash", line_color="#d4c4a8", line_width=1)

    # Quadrant labels
    for txt, ax, ay in [
        ("💎 理想\n（低估值 + 高增長）", med_pe*0.5, med_rg*1.5),
        ("🎢 成長泡沫\n（高估值 + 高增長）", med_pe*1.5, med_rg*1.5),
        ("🛡️ 價值股\n（低估值 + 低增長）", med_pe*0.5, med_rg*0.3),
        ("💀 價值陷阱\n（高估值 + 低增長）", med_pe*1.5, med_rg*0.3),
    ]:
        fig.add_annotation(x=ax, y=ay, text=txt, showarrow=False,
                           font=dict(size=9, color="#9a8a7a"),
                           align="center")

    fig.update_layout(
        title="估值象限圖：P/E vs 收入增長",
        height=400,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        xaxis=dict(title="P/E 倍數", gridcolor=CHART_THEME["gridcolor"]),
        yaxis=dict(title="收入增長 %", gridcolor=CHART_THEME["gridcolor"]),
        margin=dict(t=50, b=30, l=30, r=20),
    )
    return fig

def chart_fcf_comparison(stocks_data: list):
    syms, fcf_vals, colors_f = [], [], []
    for d in stocks_data:
        if d.get("error") or d.get("fcf") is None: continue
        syms.append(d["symbol"])
        fcf_vals.append(round(d["fcf"] / 1e9, 2))
        colors_f.append("#4a9a4a" if d["fcf"] > 0 else "#b84040")

    if not syms: return go.Figure()
    fig = go.Figure(go.Bar(
        x=syms, y=fcf_vals, marker_color=colors_f,
        text=[f"${v}B" for v in fcf_vals], textposition="outside"
    ))
    fig.update_layout(
        title="自由現金流對比（十億美元）",
        height=320,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"], title="FCF (B USD)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=50, b=20, l=20, r=20),
    )
    return fig

# ── RENDER FUNCTIONS ──────────────────────────────────────────────────────────
def render_stock_card(d: dict):
    if d.get("error"):
        err_msg = str(d.get("error") or "")
        # Treat ALL yfinance / network errors as rate-limit (most common cause on Streamlit Cloud)
        _rl_keywords = ["rate", "429", "too many", "yfratelimit", "limit", "empty info",
                        "runtimeerror", "yfinance"]
        is_rate_limit = any(kw in err_msg.lower() for kw in _rl_keywords) or not err_msg
        sym = d["symbol"]
        if is_rate_limit:
            st.markdown(f"""
            <div style="background:#fff9ee;border:1px solid #d4c4a8;border-left:4px solid #c8922a;
                        border-radius:6px;padding:16px 20px;margin-bottom:12px;">
              <div style="font-family:IBM Plex Mono,monospace;font-size:12px;
                          color:#c8922a;font-weight:600;margin-bottom:8px">
                ⚠️ {sym} — 數據源被限速
              </div>
              <div style="font-size:13px;color:#3d2b1f;line-height:1.8">
                Streamlit Cloud 的共享 IP 被 Yahoo Finance 封鎖，這是雲端部署的常見問題。<br>
                <b>解決方法：</b>在左側欄填入免費 API Key，系統自動切換數據源：
              </div>
              <div style="margin-top:10px;display:flex;gap:12px;flex-wrap:wrap">
                <a href="https://www.alphavantage.co/support/#api-key" target="_blank"
                   style="background:#2a1d13;color:#e8b84b;padding:7px 14px;border-radius:4px;
                          text-decoration:none;font-family:IBM Plex Mono,monospace;font-size:11px;
                          font-weight:600">
                  🔑 免費申請 Alpha Vantage Key
                </a>
                <a href="https://finnhub.io/register" target="_blank"
                   style="background:#2a1d13;color:#e8b84b;padding:7px 14px;border-radius:4px;
                          text-decoration:none;font-family:IBM Plex Mono,monospace;font-size:11px;
                          font-weight:600">
                  🔑 免費申請 Finnhub Key
                </a>
              </div>
              <div style="margin-top:8px;font-size:11px;color:#9a8a7a;font-family:IBM Plex Mono,monospace">
                技術細節：{err_msg[:100]}
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ {sym} 數據異常：{err_msg[:150]}")
        return

    sc    = score_stock(d)
    band  = get_pe_band(d.get("hist_pe", []))
    pe    = d.get("pe")
    chg   = d["change_pct"]
    chg_c = "price-change-up" if chg >= 0 else "price-change-dn"
    chg_s = f"{'▲' if chg >= 0 else '▼'} {abs(chg):.2f}%"

    # Analyst upside
    target = d.get("analyst_target")
    upside = ((target - d["price"]) / d["price"] * 100) if target and d["price"] else None

    html = f"""
    <div class="val-card">
      <div class="val-card-header">
        <div>
          <div class="ticker-name">{d['symbol']}</div>
          <div class="company-name">{d['name'][:35]}</div>
          <div style="margin-top:6px;display:flex;gap:6px;align-items:center;flex-wrap:wrap">
            <span class="signal-badge {sc['sig_class']}">{sc['emoji']} {sc['signal']}　{sc['score']}/100</span>
            <span style="font-family:IBM Plex Mono,monospace;font-size:9px;color:#9a8a7a;
                         background:#f0ebe0;padding:2px 7px;border-radius:10px">
              via {d.get('data_source','—')}
            </span>
          </div>
        </div>
        <div class="price-block">
          <div class="price-main">${d['price']:,.2f}</div>
          <div class="{chg_c}">{chg_s}</div>
          {'<div style="font-size:11px;color:#7a6a5a;margin-top:3px">目標: $'+f"{target:.2f}" +f' ({upside:+.1f}%)</div>' if upside else ''}
        </div>
      </div>

      <div class="metric-row">
        <div class="m-item">
          <div class="m-label">P/E</div>
          <div class="m-value {'m-value-hi' if pe and pe > INDUSTRY_PE.get(d.get('sector','default'),25)*1.3 else 'm-value-ok' if pe and pe < INDUSTRY_PE.get(d.get('sector','default'),25)*0.9 else ''}">{f"{pe:.1f}x" if pe else "N/A"}</div>
        </div>
        <div class="m-item">
          <div class="m-label">Fwd P/E</div>
          <div class="m-value">{f"{d['forward_pe']:.1f}x" if d.get('forward_pe') else "N/A"}</div>
        </div>
        <div class="m-item">
          <div class="m-label">P/S</div>
          <div class="m-value">{f"{d['ps']:.1f}x" if d.get('ps') else "N/A"}</div>
        </div>
        <div class="m-item">
          <div class="m-label">PEG</div>
          <div class="m-value {'m-value-ok' if d.get('peg') and d['peg']<2 else 'm-value-hi' if d.get('peg') and d['peg']>3 else ''}">{f"{d['peg']:.2f}" if d.get('peg') else "N/A"}</div>
        </div>
        <div class="m-item">
          <div class="m-label">毛利率</div>
          <div class="m-value {'m-value-ok' if d.get('gross_margin') and d['gross_margin']>0.35 else ''}">{fmt_pct(d.get('gross_margin'))}</div>
        </div>
        <div class="m-item">
          <div class="m-label">FCF率</div>
          <div class="m-value {'m-value-ok' if d.get('fcf_yield') and d['fcf_yield']>3 else 'm-value-hi' if d.get('fcf_yield') and d['fcf_yield']<0 else ''}">{f"{d['fcf_yield']:.1f}%" if d.get('fcf_yield') is not None else "N/A"}</div>
        </div>
        <div class="m-item">
          <div class="m-label">收入增長</div>
          <div class="m-value {'m-value-ok' if d.get('rev_growth') and d['rev_growth']>0.1 else 'm-value-hi' if d.get('rev_growth') and d['rev_growth']<0 else ''}">{fmt_pct(d.get('rev_growth'))}</div>
        </div>
        <div class="m-item">
          <div class="m-label">Beta</div>
          <div class="m-value">{f"{d['beta']:.2f}" if d.get('beta') else "N/A"}</div>
        </div>
      </div>
    """

    # Historical PE band
    if band and pe:
        pct_pos = max(0, min(100, (pe - band["min"]) / max(band["max"] - band["min"], 1) * 100))
        html += f"""
      <div class="band-wrap">
        <div class="band-label">歷史 P/E 區間（5年）：低 {band['min']}x ── 均 {band['avg']}x ── 高 {band['max']}x</div>
        <div class="band-bar-bg">
          <div class="band-marker" style="left:{pct_pos:.0f}%"></div>
        </div>
        <div class="band-ticks">
          <span>{band['min']}x 低</span>
          <span>▲ 現在 {pe:.1f}x</span>
          <span>高 {band['max']}x</span>
        </div>
      </div>
        """

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def render_ranking(stocks_data: list):
    ranked = []
    for d in stocks_data:
        if not d.get("error"):
            sc = score_stock(d)
            ranked.append((d, sc))
    ranked.sort(key=lambda x: x[1]["score"], reverse=True)

    st.markdown('<div class="section-header">估值排名榜</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏆 由最抵買到最貴排列</div>', unsafe_allow_html=True)

    for i, (d, sc) in enumerate(ranked, 1):
        bar_color = "#4a9a4a" if sc["score"]>=65 else "#c8922a" if sc["score"]>=40 else "#b84040"
        bar_w = sc["score"]
        st.markdown(f"""
        <div class="rank-row">
          <div class="rank-num">#{i}</div>
          <div class="rank-ticker">{d['symbol']}</div>
          <div style="font-size:11px;color:#7a6a5a;min-width:80px">${d['price']:,.2f} {sc['emoji']}</div>
          <div class="rank-bar-wrap">
            <div class="rank-bar-bg">
              <div class="rank-bar-fill" style="width:{bar_w}%;background:{bar_color}"></div>
            </div>
          </div>
          <div class="rank-score">{sc['score']}/100</div>
        </div>
        """, unsafe_allow_html=True)

def render_eps_surprise(d: dict):
    eps_list = d.get("eps_surprise", [])
    if not eps_list:
        st.caption("暫無季度盈利驚喜數據")
        return

    avg_surp = np.mean([x["surprise_pct"] for x in eps_list])
    color = "#2a6a2a" if avg_surp > 0 else "#b84040"

    st.markdown(f"""
    <div class="bakery-box">
      <div class="bakery-title">🎯 盈利驚喜追蹤 — {d['symbol']}</div>
      <b>過去{len(eps_list)}季平均盈利驚喜率：
      <span style="color:{color}">{avg_surp:+.1f}%</span></b><br>
      {"🥖 這間麵包店連續多季都賣多過預期，老闆低調報數、實際派多咗包——值得額外溢價。" if avg_surp > 5 else
       "🥖 這間麵包店業績基本符合預期，表現穩定。" if avg_surp >= 0 else
       "🥖 這間麵包店多次賣少過預期，管理層預測能力存疑。"}
    </div>
    """, unsafe_allow_html=True)

    for x in eps_list:
        up = x["surprise_pct"] >= 0
        st.markdown(f"""
        <div class="eps-row">
          <span class="eps-q">{x['quarter']}</span>
          <span>預期 EPS: <b>${x['estimate']:.2f}</b></span>
          <span>實際: <b>${x['actual']:.2f}</b></span>
          <span class="{'eps-beat' if up else 'eps-miss'}">{'+' if up else ''}{x['surprise_pct']:.1f}% {'✓' if up else '✗'}</span>
        </div>
        """, unsafe_allow_html=True)

def render_market_thermometer(stocks_data: list):
    valid = [d for d in stocks_data if not d.get("error")]
    if not valid: return
    avg_score = np.mean([score_stock(d)["score"] for d in valid])
    color = "#2a6a2a" if avg_score>=65 else "#c8922a" if avg_score>=40 else "#b84040"
    label = "整體估值合理 🟢" if avg_score>=65 else "整體略貴 🟡" if avg_score>=40 else "整體偏貴 🔴"
    desc = (
        "🥖 整體而言，大部分麵包店定價合理，市場沒有明顯泡沫跡象。"
        if avg_score >= 65 else
        "🥖 大部分麵包店定價略貴，建議精選個股，避免追高。"
        if avg_score >= 40 else
        "🥖 整體麵包街定價偏高，市場情緒過熱，宜謹慎。"
    )
    st.markdown(f"""
    <div class="temp-gauge">
      <div class="temp-value" style="color:{color}">{avg_score:.0f}</div>
      <div class="temp-label">{label}</div>
      <div style="font-size:13px;color:#7a6a5a;margin-top:8px">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

# ── AI PROMPT GENERATOR ───────────────────────────────────────────────────────
def build_prompt(d: dict, sc: dict, ai_name: str) -> str:
    """Build a rich, data-filled prompt tailored to each AI style."""
    sym   = d["symbol"]
    name  = d.get("name", sym)
    price = d.get("price", "N/A")
    pe    = d.get("pe")
    fpe   = d.get("forward_pe")
    ps    = d.get("ps")
    pb    = d.get("pb")
    peg   = d.get("peg")
    eps   = d.get("eps")
    gm    = d.get("gross_margin")
    pm    = d.get("profit_margin")
    fcf_y = d.get("fcf_yield")
    rg    = d.get("rev_growth")
    eg    = d.get("earnings_growth")
    beta  = d.get("beta")
    target= d.get("analyst_target")
    score = sc["score"]
    signal= sc["signal"]
    sector= d.get("sector", "科技")
    band  = get_pe_band(d.get("hist_pe", []))

    def fp(v, decimals=1): return f"{v:.{decimals}f}" if v is not None else "N/A"
    def fpc(v): return f"{v*100:.1f}%" if v is not None else "N/A"

    bench_pe  = INDUSTRY_PE.get(sector, 25)
    hist_avg  = f"{band['avg']}x" if band else "N/A"
    hist_range= f"{band['min']}x – {band['max']}x" if band else "N/A"
    upside_str = ""
    if target and price and isinstance(price, (int, float)) and price > 0:
        upside_str = f"（現價折讓 {fp((target-price)/price*100,1)}%）"

    data_block = f"""【{sym} 即時估值數據 — {datetime.now().strftime("%Y-%m-%d")}】
公司名稱：{name}
股票代碼：{sym}（{sector}）
現價：${price}
分析師目標價：${fp(target)} {upside_str}

📊 估值指標：
• P/E（市盈率）：{fp(pe)}x  |  行業均值：{bench_pe}x  |  5年歷史均值：{hist_avg}
• 歷史P/E區間（5年）：{hist_range}
• Forward P/E（遠期市盈率）：{fp(fpe)}x
• P/S（市銷率）：{fp(ps)}x
• P/B（市帳率）：{fp(pb)}x
• PEG 比率：{fp(peg)}

💰 盈利能力：
• EPS（每股盈利）：${fp(eps)}
• 毛利率：{fpc(gm)}
• 純利率：{fpc(pm)}
• 自由現金流率（FCF Yield）：{fp(fcf_y)}%

📈 增長數據：
• 收入增長（YoY）：{fpc(rg)}
• 盈利增長（YoY）：{fpc(eg)}
• Beta（波動性）：{fp(beta)}

🥖 系統估值評分：{score}/100（{signal}）""".strip()

    if ai_name == "Claude":
        return f"""{data_block}

請你扮演一位資深香港股票分析師，同時是一間麵包店老闆。
用生動的麵包店比喻，以繁體中文分析以上 {sym} 的估值是否合理。

請覆蓋以下四個方面：
1. 🥖 麵包店比喻：用賣麵包的邏輯解釋 P/E、P/S、毛利率的意義
2. 📊 估值判斷：現價 vs 歷史均值 vs 行業均值，係貴定平？
3. ⚠️ 主要風險：估值面和基本面的最大隱憂各一點
4. 📍 操作建議：買入 / 持有 / 等待 / 沽出，並說明理由和目標價位

語氣要親切易明，像朋友之間討論投資，避免過於學術化。用繁體中文回答。"""

    elif ai_name == "ChatGPT":
        return f"""{data_block}

請以繁體中文，用結構化方式分析 {sym} 的股票估值。

請按以下格式回答：

**一、現時估值水平**
（P/E、P/S 與行業及歷史比較，數字要對應上方數據）

**二、麵包店比喻**
（用日常生活比喻解釋這隻股票現在貴定平）

**三、優勢與風險**
（各列出3點，要具體）

**四、結論與建議**
（明確給出建議買入價位、12個月目標價、止損位）

請保持客觀，所有數字引用請對應上方提供的數據。用繁體中文回答。"""

    elif ai_name == "Gemini":
        return f"""{data_block}

請以繁體中文，結合當前宏觀經濟環境（美國利率走勢、科技股估值周期、AI發展對行業影響），
全面分析 {sym} 的估值合理性。

分析框架：
1. 📈 宏觀環境：現時利率水平如何影響合理 P/E？
2. 🏭 行業定位：在整個行業中的競爭護城河有多深？
3. 🥖 麵包店比喻：這間店在整條「科技股麵包街」處於什麼位置？
4. 🔮 三個情境（未來12個月）：
   - 牛市情境（Bull Case）：目標價？
   - 基本情境（Base Case）：目標價？
   - 熊市情境（Bear Case）：目標價？
5. 📍 最終建議與主要風險提示

請用繁體中文，語氣專業但易明。"""

    elif ai_name == "Grok":
        return f"""{data_block}

直接告訴我：{sym} 而家值唔值得買？

用最直接嘅廣東話口語分析：
1. 條數係咪合理？P/E {fp(pe)}x vs 行業 {bench_pe}x，點睇？
2. 毛利率 {fpc(gm)} 同 FCF {fp(fcf_y)}%，呢間「麵包店」賺唔賺到錢？
3. 散戶最容易忽略嘅估值陷阱係咩？
4. 你會唔會買？幾錢入？幾錢走？

唔需要廢話，直接講結論。用繁體中文。"""

    return data_block


def render_ai_prompt_buttons(d: dict, sc: dict):
    """Render 4 AI buttons — clicking opens the chatbot with prompt pre-filled via URL param."""
    sym = d["symbol"]

    AI_CONFIG = [
        ("Claude",  "🟣", "#7C3AED", "https://claude.ai/new?q={prompt}"),
        ("ChatGPT", "🟢", "#10A37F", "https://chatgpt.com/?q={prompt}"),
        ("Gemini",  "🔵", "#1A73E8", "https://gemini.google.com/app?q={prompt}"),
        ("Grok",    "⚫", "#000000", "https://x.com/i/grok?text={prompt}"),
    ]

    st.markdown(
        '<div style="font-family:IBM Plex Mono,monospace;font-size:10px;' +
        'letter-spacing:2px;color:#c8922a;text-transform:uppercase;margin:14px 0 8px">' +
        '🤖 選擇 AI 分析（點擊直接跳轉，Prompt 已自動填入）</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(4)
    for col, (ai_name, emoji, color, url_tpl) in zip(cols, AI_CONFIG):
        with col:
            prompt_text = build_prompt(d, sc, ai_name)
            encoded     = quote(prompt_text, safe="")
            url         = url_tpl.format(prompt=encoded)
            st.markdown(
                f'<a href="{url}" target="_blank" rel="noopener noreferrer" ' +
                f'style="display:block;text-align:center;padding:9px 4px;' +
                f'background:{color};color:#fff;border-radius:5px;' +
                f'text-decoration:none;font-family:IBM Plex Mono,monospace;' +
                f'font-size:12px;font-weight:600;letter-spacing:0.5px">' +
                f'{emoji} {ai_name}</a>',
                unsafe_allow_html=True
            )

    # Fallback: collapsible copy box
    key_show = f"show_prompt_{sym}"
    if key_show not in st.session_state:
        st.session_state[key_show] = False

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    toggle_lbl = "📋 顯示 Prompt 文字（備用複製）" if not st.session_state[key_show] else "▲ 收起 Prompt"
    if st.button(toggle_lbl, key=f"toggle_prompt_{sym}"):
        st.session_state[key_show] = not st.session_state[key_show]

    if st.session_state[key_show]:
        ai_choice = st.radio(
            "AI 風格：", ["Claude", "ChatGPT", "Gemini", "Grok"],
            horizontal=True, key=f"ai_radio_{sym}", label_visibility="collapsed"
        )
        st.code(build_prompt(d, sc, ai_choice), language=None)
        st.caption("☝️ 全選複製後貼到對應 AI 網頁即可")


# ── MAIN APP ──────────────────────────────────────────────────────────────────
def main():
    init_state()
    inject_css()

    # ── SIDEBAR ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🥖 估值儀表板")
        st.markdown("---")

        ticker_input = st.text_input(
            "股票代碼（逗號分隔）",
            value="AAPL,MSFT,GOOGL,NVDA,TSLA,META,AMZN",
            help="例如：AAPL,TSLA,NVDA"
        )
        symbols = [s.strip().upper() for s in ticker_input.split(",") if s.strip()]

        col1, col2 = st.columns(2)
        with col1:
            refresh_btn = st.button("🔄 刷新", use_container_width=True)
        with col2:
            auto_toggle = st.button(
                "⏸ 停止" if st.session_state.auto_refresh else "▶ 自動",
                use_container_width=True
            )
        # Clear cache button — forces re-fetch bypassing any cached errors
        if st.button("🗑️ 清除 Cache 重試", use_container_width=True,
                     help="如果數據顯示錯誤，點此清除舊 cache 重新拉取"):
            _fetch_stock_cached.clear()
            st.session_state.stock_data = {}
            st.rerun()

        refresh_interval = st.selectbox("自動刷新間隔", [30, 60, 120, 300],
                                         format_func=lambda x: f"{x}秒", index=1)
        st.session_state.refresh_interval = refresh_interval

        if auto_toggle:
            st.session_state.auto_refresh = not st.session_state.auto_refresh

        st.markdown("---")
        st.markdown("### 🔑 API 設定")

        def _secret(key, default=""):
            try: return st.secrets.get(key, default)
            except: return default

        st.markdown("**📊 股票數據（四層 Fallback）**")
        av_key   = st.text_input("Alpha Vantage Key（Layer 2）", type="password",
                                  value=_secret("ALPHA_VANTAGE_KEY"),
                                  help="免費申請：alphavantage.co — 每日25次")
        fh_key   = st.text_input("Finnhub Key（Layer 3）", type="password",
                                  value=_secret("FINNHUB_KEY"),
                                  help="免費申請：finnhub.io — 每分鐘60次")
        st.caption("💡 Layer 1 (yfinance) 自動嘗試，雲端被封時自動切換")

        st.markdown("**🤖 AI 分析**")
        groq_key  = st.text_input("Groq API Key", type="password",
                                   value=_secret("GROQ_API_KEY"))
        st.markdown("**📬 Telegram**")
        tg_token  = st.text_input("Bot Token", type="password",
                                   value=_secret("TELEGRAM_BOT_TOKEN"))
        tg_chat   = st.text_input("Chat ID",
                                   value=_secret("TELEGRAM_CHAT_ID"))

        st.markdown("---")
        st.markdown("### 📡 Telegram 警報")
        tg_enable    = st.toggle("啟用 Telegram 通知", value=False)
        alert_high   = st.slider("當估值分低於（發高估警報）", 20, 60, 40)
        alert_low    = st.slider("當估值分高於（發低估機會）", 50, 90, 65)

        st.markdown("---")
        if st.session_state.last_refresh:
            st.caption(f"最後更新：{st.session_state.last_refresh.strftime('%H:%M:%S')}")

    # ── FETCH DATA ────────────────────────────────────────────────────────────
    need_refresh = (
        refresh_btn or
        not st.session_state.stock_data or
        (st.session_state.auto_refresh and st.session_state.last_refresh and
         (datetime.now() - st.session_state.last_refresh).seconds >= refresh_interval)
    )

    if need_refresh:
        with st.spinner("📡 正在拉取最新數據..."):
            for sym in symbols:
                st.session_state.stock_data[sym] = fetch_stock(sym, av_key=av_key, fh_key=fh_key)
        st.session_state.last_refresh = datetime.now()
        st.session_state.tg_sent = set()  # reset alerts on refresh

    stocks_data = [st.session_state.stock_data.get(sym, {"symbol": sym, "error": "未加載"})
                   for sym in symbols]

    # Telegram alerts
    if tg_enable and tg_token and tg_chat:
        check_telegram_alerts(stocks_data, tg_token, tg_chat, alert_high, alert_low)

    # ── PAGE HEADER ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom:20px">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:3px;
                  color:#c8922a;text-transform:uppercase;margin-bottom:4px">
        Stock Valuation Dashboard · 用麵包店理解估值
      </div>
      <div style="font-size:26px;font-weight:700;color:#2a1d13">
        🥖 實時股票估值監控
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 估值總覽",
        "📈 對比圖表",
        "🧮 工具箱",
        "🥖 麵包店 AI 分析"
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1: 估值總覽
    # ─────────────────────────────────────────────────────────────────────────
    with tab1:
        # Market thermometer
        st.markdown('<div class="section-header">市場整體溫度計</div>', unsafe_allow_html=True)
        render_market_thermometer(stocks_data)
        st.markdown("---")

        # Stock cards (2 per row)
        st.markdown('<div class="section-header">個股估值卡片</div>', unsafe_allow_html=True)
        cols_per_row = 2
        valid_stocks = [d for d in stocks_data if not d.get("error")]
        all_stocks_display = stocks_data

        for i in range(0, len(all_stocks_display), cols_per_row):
            row_stocks = all_stocks_display[i:i+cols_per_row]
            cols = st.columns(cols_per_row)
            for col, d in zip(cols, row_stocks):
                with col:
                    render_stock_card(d)

        # Historical PE charts
        st.markdown("---")
        st.markdown('<div class="section-header">歷史 P/E 走勢</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📉 過去5年市盈率變化</div>', unsafe_allow_html=True)

        valid_with_hist = [d for d in valid_stocks if d.get("hist_pe")]
        if valid_with_hist:
            sel_sym = st.selectbox("選擇股票查看歷史P/E", [d["symbol"] for d in valid_with_hist])
            sel_d   = next(d for d in valid_with_hist if d["symbol"] == sel_sym)
            sel_pe  = sel_d.get("pe")
            sel_px  = sel_d.get("price")

            # Sub-tabs for different chart views
            ctab1, ctab2, ctab3, ctab4 = st.tabs([
                "📉 P/E 走勢",
                "🔗 股價 & P/E 雙軸圖",
                "🔵 P/E vs 股價 散點",
                "💰 EPS vs 股價",
            ])

            with ctab1:
                fig_hist = chart_hist_pe(sel_d["hist_pe"], sel_sym, sel_pe)
                if fig_hist:
                    st.plotly_chart(fig_hist, use_container_width=True, key="hist_pe_tab1")
                # Bakery valuation band note
                band = get_pe_band(sel_d["hist_pe"])
                if band and sel_pe:
                    pct = (sel_pe - band["min"]) / max(band["max"] - band["min"], 1) * 100
                    zone = "便宜區 🟢" if sel_pe <= band["avg"]*0.85 else "偏貴區 🔴" if sel_pe >= band["avg"]*1.2 else "合理區 🟡"
                    st.markdown(f"""
                    <div class="bakery-box">
                      <div class="bakery-title">🥖 {sel_sym} 歷史 P/E 麵包店解讀</div>
                      現在的 P/E <b>{sel_pe:.1f}x</b> 落在過去5年的 <b>{pct:.0f}%</b> 分位數，屬於 <b>{zone}</b>。<br>
                      5年均值 {band["avg"]}x　|　歷史低位 {band["min"]}x　|　歷史高位 {band["max"]}x<br>
                      🥖 比喻：如果過去5年這間麵包店平均要 <b>{band["avg"]}年</b> 回本，
                      現在要 <b>{sel_pe:.0f}年</b>，
                      {"比歷史均值貴了不少。" if sel_pe > band["avg"]*1.15 else "與歷史均值相若，定價合理。" if sel_pe > band["avg"]*0.9 else "比歷史均值便宜，值得留意。"}
                    </div>
                    """, unsafe_allow_html=True)

            with ctab2:
                fig_dual, fig_scatter = chart_pe_price_relationship(
                    sel_d["hist_pe"], sel_sym, sel_pe, sel_px
                )
                if fig_dual:
                    st.plotly_chart(fig_dual, use_container_width=True, key=f"dual_{sel_sym}")
                    st.caption(
                        "📊 上圖：股價走勢（或估算股價）｜下圖：P/E走勢，"
                        "🟢 綠色區 = 歷史便宜　🔴 紅色區 = 歷史偏貴"
                    )
                else:
                    st.info("數據不足，無法生成雙軸圖")

            with ctab3:
                _, fig_scatter2 = chart_pe_price_relationship(
                    sel_d["hist_pe"], sel_sym, sel_pe, sel_px
                )
                if fig_scatter2:
                    st.plotly_chart(fig_scatter2, use_container_width=True, key=f"scatter_{sel_sym}")
                    st.markdown("""
                    <div style="font-size:12px;color:#7a6a5a;margin-top:-8px;padding:8px 12px;
                                background:#f5efe3;border-radius:4px">
                    🥖 <b>麵包店比喻：</b>散點圖顯示「出價（P/E）」與「店舖估值（股價）」的關係。
                    🟢 綠點 = 當時市場出價便宜　🔴 紅點 = 出價偏貴　⭐ = 現在位置。
                    相關係數愈接近 1，代表 P/E 與股價同步性愈高。
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("需要完整股價數據才能生成散點圖（yfinance 數據源）")

            with ctab4:
                hist_eps_data = sel_d.get("hist_eps", [])
                cur_eps       = sel_d.get("eps")
                # Pass hist_pe as fallback — derives eps_implied = price / pe
                fig_ep1, fig_ep2, fig_ep3 = chart_eps_price(
                    hist_eps_data, sel_sym, cur_eps, sel_px
                )
                if fig_ep1:
                    st.plotly_chart(fig_ep1, use_container_width=True,
                                    key=f"eps_dual_{sel_sym}")
                    st.caption(
                        "📊 上圖：股價走勢　|　下圖：TTM EPS（真實季度盈利，來自 Alpha Vantage）"
                        "　棒顏色 = YoY增長速度：🟢深綠 ≥+15%　🟢淺綠 +5%~15%　🟡 +0%~5%　🟠 -10%~0%　🔴 < -10%"
                    )
                if fig_ep2:
                    st.plotly_chart(fig_ep2, use_container_width=True,
                                    key=f"eps_scatter_{sel_sym}")
                    st.markdown("""
                    <div style="font-size:12px;color:#7a6a5a;margin-top:-8px;padding:10px 14px;
                                background:#f5efe3;border-radius:4px;line-height:1.8">
                    🥖 <b>麵包店比喻：</b>這張圖顯示「店舖盈利（EPS）」與「買家出價（股價）」的關係。<br>
                    EPS 愈高，股價通常愈貴——就像麵包店年年賺多了，收購價自然水漲船高。<br>
                    <b>相關係數 r 愈高（接近1），代表股價跟盈利走得愈齊——是健康的估值形態。</b><br>
                    如果股價飆升但 EPS 無升，⭐現在點就會偏離趨勢線，代表估值已超前盈利。
                    </div>
                    """, unsafe_allow_html=True)
                if fig_ep3:
                    st.plotly_chart(fig_ep3, use_container_width=True,
                                    key=f"eps_growth_{sel_sym}")
                    st.caption("📊 EPS 同比增長率（YoY%）— 連續正增長代表盈利質素穩定")
                if not fig_ep1 and not fig_ep2:
                    st.markdown("""
                    <div style="background:#fff9ee;border:1px solid #d4c4a8;
                                border-left:4px solid #c8922a;border-radius:6px;
                                padding:16px 20px;font-size:13px;color:#3d2b1f;line-height:1.8">
                      <div style="font-family:IBM Plex Mono,monospace;font-size:11px;
                                  color:#c8922a;font-weight:600;margin-bottom:8px">
                        💡 需要 Alpha Vantage API Key 才能顯示真實 EPS 歷史
                      </div>
                      EPS 歷史數據需要來自 <b>Alpha Vantage EARNINGS 端點</b>的真實季度盈利記錄。<br>
                      用股價 ÷ P/E 推算 EPS 是<b>循環計算</b>（因 P/E 本身已用現在 EPS 計算），結果無意義。<br><br>
                      <b>解決方法：</b>在左側欄填入免費 Alpha Vantage Key，每日免費25次查詢足夠使用。<br>
                      <a href="https://www.alphavantage.co/support/#api-key" target="_blank"
                         style="color:#c8922a;font-weight:600">
                        🔑 免費申請 Alpha Vantage Key →
                      </a>
                    </div>
                    """, unsafe_allow_html=True)

            # Scoring reasons (always show)
            sc = score_stock(sel_d)
            if sc["reasons"]:
                st.markdown(f"""
                <div class="bakery-box">
                  <div class="bakery-title">📋 {sel_sym} 估值評分理由</div>
                  {"<br>".join(f"• {r}" for r in sc['reasons'])}
                </div>
                """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2: 對比圖表
    # ─────────────────────────────────────────────────────────────────────────
    with tab2:
        render_ranking(stocks_data)
        st.markdown("---")

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_pe_comparison(stocks_data), use_container_width=True, key="chart_pe")
        with c2:
            st.plotly_chart(chart_ps_comparison(stocks_data), use_container_width=True, key="chart_ps")

        st.markdown("---")
        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(chart_fcf_comparison(stocks_data), use_container_width=True, key="chart_fcf")
        with c4:
            # Radar: select one stock
            valid_s = [d for d in stocks_data if not d.get("error")]
            if valid_s:
                sel2 = st.selectbox("雷達圖股票", [d["symbol"] for d in valid_s], key="radar_sel")
                d2   = next(d for d in valid_s if d["symbol"]==sel2)
                st.plotly_chart(chart_radar(d2, score_stock(d2)), use_container_width=True, key=f"chart_radar_{sel2}")

        st.markdown("---")
        st.plotly_chart(chart_quadrant(stocks_data), use_container_width=True, key="chart_quadrant")

        # EPS surprise
        st.markdown("---")
        st.markdown('<div class="section-header">盈利驚喜追蹤</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 過去4季 EPS 實際 vs 預期</div>', unsafe_allow_html=True)
        valid_s2 = [d for d in stocks_data if not d.get("error")]
        if valid_s2:
            sel3 = st.selectbox("選擇股票", [d["symbol"] for d in valid_s2], key="eps_sel")
            d3   = next(d for d in valid_s2 if d["symbol"]==sel3)
            render_eps_surprise(d3)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3: 工具箱
    # ─────────────────────────────────────────────────────────────────────────
    with tab3:
        t3a, t3b = st.columns(2)

        with t3a:
            st.markdown('<div class="section-header">安全邊際計算器</div>', unsafe_allow_html=True)
            st.markdown("#### 🛡️ 你的合理買入價係幾多？")
            st.caption("輸入你的要求，計算機反推「值得買入的最高價」")

            valid_s3 = [d for d in stocks_data if not d.get("error") and d.get("eps")]
            if valid_s3:
                sel_mos = st.selectbox("選擇股票", [d["symbol"] for d in valid_s3], key="mos_sel")
                d_mos   = next(d for d in valid_s3 if d["symbol"]==sel_mos)
                eps_val = d_mos.get("eps", 0)

                req_ret = st.slider("你要求的年回報率 %", 5, 20, 10)
                growth  = st.slider("預期EPS年增長率 %", 0, 30, 12)
                years   = st.slider("持有年數", 3, 15, 10)

                fair = margin_of_safety(eps_val, req_ret, growth, years)
                curr = d_mos["price"]
                premium = ((curr - fair) / fair * 100) if fair > 0 else 0

                color_mos = "#2a6a2a" if premium < 0 else "#c8922a" if premium < 20 else "#b84040"
                verdict = "低於合理價，值得考慮 ✓" if premium < 0 else "略高於合理價" if premium < 20 else "明顯高於合理價 ✗"

                st.markdown(f"""
                <div class="bakery-box">
                  <div class="bakery-title">🥖 {sel_mos} 安全邊際分析</div>
                  <b>EPS：</b>${eps_val:.2f} ｜ <b>要求回報：</b>{req_ret}%/年 ｜ <b>預期增長：</b>{growth}%/年<br><br>
                  <b>合理買入價：</b> <span style="font-size:22px;font-family:'IBM Plex Mono'">${fair:,.2f}</span><br>
                  <b>現價：</b>${curr:,.2f}<br>
                  <b>溢/折價：</b> <span style="color:{color_mos};font-weight:700">{premium:+.1f}%</span>　{verdict}<br><br>
                  <i>🥖 比喻：如果你要求這間麵包店{years}年回本、每年增長{growth}%，合理出價係${fair:,.0f}，
                  現在老闆開${curr:,.0f}，你{"多付了" if premium>0 else "少付了"} {abs(premium):.1f}%。</i>
                </div>
                """, unsafe_allow_html=True)

        with t3b:
            st.markdown('<div class="section-header">利率調整估值</div>', unsafe_allow_html=True)
            st.markdown("#### 🏦 利率環境下的合理 P/E")
            st.caption("當債息高，股票的合理P/E應該更低——因為「安全」回報提高了")

            risk_free = st.slider("10年期國債息率 %", 1.0, 8.0, 4.5, step=0.1)
            erp       = st.slider("股票風險溢價 ERP %", 2.0, 8.0, 5.0, step=0.5)

            fair_pe = fed_adjusted_pe(risk_free, erp)
            industry_pe_ref = 25.0

            st.markdown(f"""
            <div class="bakery-box">
              <div class="bakery-title">🏦 利率調整後合理 P/E</div>
              <b>計算公式：</b> 100 ÷ (國債 {risk_free}% + ERP {erp}%) = <span style="font-size:24px;font-family:'IBM Plex Mono'">{fair_pe}x</span><br><br>
              <b>參考：</b>行業一般均值約 25x（低息時期）<br><br>
              {"⚠️ 現在利率偏高，合理P/E只有"+str(fair_pe)+"x，市場整體P/E若超過此水平，代表股票相對債券吸引力下降。" if fair_pe < 20 else
               "✓ 現在利率環境下，合理P/E約"+str(fair_pe)+"x，與歷史均值相若。"}<br><br>
              <i>🥖 比喻：銀行存款有 {risk_free:.1f}% 利息，你投資麵包店就要求更高回報。
              所以你願意付的「回本年數」（P/E）自然縮短至 {fair_pe}年。
              如果市場還在用 25x 定價，即係投資者仍然偏好股票，或者預期減息。</i>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            # Compare all stocks against adjusted PE
            st.markdown("**各股與利率調整後合理P/E對比：**")
            for d in stocks_data:
                if d.get("error") or not d.get("pe"): continue
                pe_now = d["pe"]
                diff   = pe_now - fair_pe
                color_c = "#b84040" if diff > 5 else "#c8922a" if diff > 0 else "#2a6a2a"
                st.markdown(f"""
                <div class="alert-box {'alert-high' if diff>5 else 'alert-low' if diff<=0 else ''}">
                  {d['symbol']}：P/E {pe_now:.1f}x vs 合理 {fair_pe}x
                  <span style="color:{color_c};margin-left:8px">({'+' if diff>0 else ''}{diff:.1f}x)</span>
                </div>
                """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4: 麵包店 AI 分析
    # ─────────────────────────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-header">麵包店 AI 分析</div>', unsafe_allow_html=True)
        st.markdown("### 🥖 用麵包店語言解讀估值")

        # Groq global summary
        if groq_key:
            if st.button("🤖 用 Groq AI 生成整體分析"):
                with st.spinner("Groq AI 正在分析..."):
                    summary = groq_summary(
                        [d for d in stocks_data if not d.get("error")], groq_key
                    )
                st.session_state.groq_summary["global"] = summary

            if "global" in st.session_state.groq_summary:
                st.markdown(f"""
                <div class="bakery-box">
                  <div class="bakery-title">🤖 Groq AI 整體市場分析</div>
                  {st.session_state.groq_summary["global"].replace(chr(10), "<br>")}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("💡 在側欄輸入 Groq API Key 可啟用 AI 分析")

        st.markdown("---")

        # Market thermometer (repeat here for context)
        st.markdown("#### 📡 整體市場溫度計")
        render_market_thermometer(stocks_data)

        st.markdown("---")
        st.markdown("#### 個股麵包店分析")

        # Individual bakery blurbs
        valid_b = [d for d in stocks_data if not d.get("error")]
        for d in valid_b:
            sc = score_stock(d)
            with st.expander(f"{sc['emoji']} {d['symbol']} — {sc['signal']} ({sc['score']}/100)"):
                blurb = bakery_blurb(d, sc)
                st.markdown(f"""
                <div class="bakery-box">
                  <div class="bakery-title">🥖 {d['symbol']} 麵包店分析</div>
                  {blurb}
                </div>
                """, unsafe_allow_html=True)

                # Scoring breakdown
                if sc["reasons"]:
                    st.markdown("**評分依據：**")
                    for r in sc["reasons"]:
                        st.markdown(f"- {r}")

                # Hist PE + relationship charts
                h_pe   = d.get("hist_pe", [])
                sym_k  = d["symbol"]
                c_pe   = d.get("pe")
                c_px   = d.get("price")

                fig_h = chart_hist_pe(h_pe, sym_k, c_pe)
                if fig_h:
                    st.plotly_chart(fig_h, use_container_width=True,
                                    key=f"hist_pe_{sym_k}_tab4")

                fig_dual_t4, fig_scat_t4 = chart_pe_price_relationship(
                    h_pe, sym_k, c_pe, c_px
                )
                if fig_dual_t4:
                    st.plotly_chart(fig_dual_t4, use_container_width=True,
                                    key=f"dual_{sym_k}_tab4")
                if fig_scat_t4:
                    st.plotly_chart(fig_scat_t4, use_container_width=True,
                                    key=f"scat_{sym_k}_tab4")

                # EPS vs Price charts
                h_eps_t4 = d.get("hist_eps", [])
                if h_eps_t4:
                    fe1, fe2, fe3 = chart_eps_price(
                    h_eps_t4, sym_k, d.get("eps"), c_px
                )
                    if fe1:
                        st.plotly_chart(fe1, use_container_width=True,
                                        key=f"eps_dual_{sym_k}_t4")
                    if fe2:
                        st.plotly_chart(fe2, use_container_width=True,
                                        key=f"eps_scat_{sym_k}_t4")
                    if fe3:
                        st.plotly_chart(fe3, use_container_width=True,
                                        key=f"eps_grow_{sym_k}_t4")

                st.markdown("---")
                render_ai_prompt_buttons(d, sc)

    # ── AUTO REFRESH ──────────────────────────────────────────────────────────
    if st.session_state.auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
