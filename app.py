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
INDUSTRY_PE = {
    "Technology": 28.0,
    "Consumer Electronics": 25.0,
    "Software": 35.0,
    "Semiconductors": 30.0,
    "Internet Content & Information": 30.0,
    "Auto Manufacturers": 15.0,
    "Financial Services": 14.0,
    "Healthcare": 22.0,
    "Energy": 12.0,
    "Consumer Defensive": 20.0,
    "Communication Services": 22.0,
    "default": 25.0,
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

# ── DATA FETCHING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def fetch_stock(symbol: str) -> dict:
    try:
        tk = yf.Ticker(symbol)
        info = tk.info or {}

        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
        prev  = info.get("previousClose") or price
        chg   = ((price - prev) / prev * 100) if prev else 0

        # Financials for EPS surprise
        try:
            qfin = tk.quarterly_financials
            qearnings = tk.quarterly_earnings
        except Exception:
            qfin = pd.DataFrame()
            qearnings = pd.DataFrame()

        # Historical PE (5yr monthly close + trailing EPS proxy)
        try:
            hist = tk.history(period="5y", interval="1mo")
            hist_prices = hist["Close"].dropna()
        except Exception:
            hist_prices = pd.Series(dtype=float)

        trailing_eps = info.get("trailingEps") or 0
        hist_pe = []
        if trailing_eps and trailing_eps > 0 and not hist_prices.empty:
            # Approximate historical PE using current EPS as proxy
            for date, p in hist_prices.items():
                hist_pe.append({"date": date, "pe": round(p / trailing_eps, 2)})

        # EPS surprise (last 4 quarters)
        eps_surprise = []
        if qearnings is not None and not qearnings.empty:
            for i, (idx, row) in enumerate(qearnings.iterrows()):
                if i >= 4:
                    break
                actual   = row.get("Earnings", None)
                estimate = row.get("Estimate", None)
                if actual is not None and estimate is not None and estimate != 0:
                    surprise_pct = (actual - estimate) / abs(estimate) * 100
                    eps_surprise.append({
                        "quarter": str(idx)[:7],
                        "actual": actual,
                        "estimate": estimate,
                        "surprise_pct": round(surprise_pct, 1),
                    })

        # FCF
        op_cf   = info.get("operatingCashflow") or 0
        capex   = info.get("capitalExpenditures") or 0
        fcf     = op_cf - abs(capex)

        # Market cap tier
        mkt_cap = info.get("marketCap") or 0

        return {
            "symbol":        symbol.upper(),
            "name":          info.get("longName") or info.get("shortName") or symbol,
            "price":         round(price, 2),
            "prev_close":    round(prev, 2),
            "change_pct":    round(chg, 2),
            "pe":            info.get("trailingPE"),
            "forward_pe":    info.get("forwardPE"),
            "ps":            info.get("priceToSalesTrailing12Months"),
            "pb":            info.get("priceToBook"),
            "eps":           trailing_eps,
            "peg":           info.get("trailingPegRatio"),
            "gross_margin":  info.get("grossMargins"),
            "profit_margin": info.get("profitMargins"),
            "fcf":           fcf,
            "fcf_yield":     (fcf / mkt_cap * 100) if mkt_cap else None,
            "mkt_cap":       mkt_cap,
            "sector":        info.get("sector") or "default",
            "industry":      info.get("industry") or "",
            "52w_high":      info.get("fiftyTwoWeekHigh"),
            "52w_low":       info.get("fiftyTwoWeekLow"),
            "beta":          info.get("beta"),
            "revenue":       info.get("totalRevenue"),
            "net_income":    info.get("netIncomeToCommon"),
            "rev_growth":    info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "analyst_target": info.get("targetMeanPrice"),
            "hist_pe":       hist_pe,
            "eps_surprise":  eps_surprise,
            "dividend_yield": info.get("dividendYield"),
            "short_ratio":   info.get("shortRatio"),
            "error":         None,
        }
    except Exception as e:
        return {"symbol": symbol.upper(), "error": str(e), "price": 0, "change_pct": 0}

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
    name   = d.get("name", d["symbol"])
    sym    = d["symbol"]
    pe     = d.get("pe")
    ps     = d.get("ps")
    gm     = d.get("gross_margin")
    rg     = d.get("rev_growth")
    fcf_y  = d.get("fcf_yield")
    score  = scoring["score"]
    sector = d.get("sector", "")

    # Build narrative
    lines = []

    # Opening
    if score >= 65:
        lines.append(f"**{sym}** 就像一間「物有所值」的麵包店——")
    elif score >= 40:
        lines.append(f"**{sym}** 就像一間「裝修靚但略貴」的麵包店——")
    else:
        lines.append(f"**{sym}** 就像一間「名氣大但超出預算」的麵包店——")

    # PE story
    if pe and pe > 0:
        bench = INDUSTRY_PE.get(sector, 25)
        wait_yr = int(pe)
        if pe < bench * 0.85:
            lines.append(f"你花 **${pe:.0f}萬** 買下每年賺 $1萬 的店，只需 **{wait_yr}年回本**，比同區麵包店（{bench:.0f}年）更快，算是抵買。")
        elif pe < bench * 1.2:
            lines.append(f"你花 **${pe:.0f}萬** 買下每年賺 $1萬 的店，需要 **{wait_yr}年回本**，與同區麵包店（{bench:.0f}年）相若，定價合理。")
        else:
            lines.append(f"你花 **${pe:.0f}萬** 買下每年賺 $1萬 的店，需要 **{wait_yr}年回本**，比同區麵包店（{bench:.0f}年）貴得多。")

    # Gross margin story
    if gm and gm > 0:
        gm_pct = gm * 100
        if gm_pct > 45:
            lines.append(f"這間店每賣 $100 的麵包，賺到 **${gm_pct:.0f} 毛利**，即是說材料成本極低，烤箱效率全城最高 🏆")
        elif gm_pct > 30:
            lines.append(f"這間店毛利率 **{gm_pct:.0f}%**，算是中上水平，成本控制不錯。")
        else:
            lines.append(f"這間店毛利率只有 **{gm_pct:.0f}%**，原材料佔成本頗高，利潤空間有限。")

    # Revenue growth
    if rg is not None:
        rg_pct = rg * 100
        if rg_pct > 15:
            lines.append(f"最近一年麵包銷量急增 **{rg_pct:.1f}%**，即係每個月都有更多新熟客排隊，生意滾雪球。")
        elif rg_pct > 0:
            lines.append(f"麵包銷量穩步增長 **{rg_pct:.1f}%**，生意平穩向上。")
        elif rg_pct < 0:
            lines.append(f"⚠️ 麵包銷量下跌 **{abs(rg_pct):.1f}%**，要留意係短期現象定係長期趨勢。")

    # FCF
    if fcf_y is not None:
        if fcf_y > 4:
            lines.append(f"老闆每年實際落袋現金回報率達 **{fcf_y:.1f}%**，即係每 $100 投資，每年收到 ${fcf_y:.1f} 真實現金，非常健康。💰")
        elif fcf_y < 0:
            lines.append(f"⚠️ 老闆現金流為負（{fcf_y:.1f}%），即係店舖支出多過收入，要靠借貸或發新股支撐。")

    # Verdict
    if score >= 65:
        lines.append(f"\n**📍 結論：** 以現價計，這間麵包店定價合理，值得考慮。")
    elif score >= 40:
        lines.append(f"\n**📍 結論：** 這間麵包店略貴，但品牌有溢價，可以等回調再考慮。")
    else:
        lines.append(f"\n**📍 結論：** 現價偏貴，建議等估值回落至更合理水平才入場。")

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
    df = df[df["pe"].between(1, 500)]
    if df.empty: return None

    avg = df["pe"].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["pe"], mode="lines",
        line=dict(color="#c8922a", width=1.5), name="P/E", fill="tozeroy",
        fillcolor="rgba(200,146,42,0.08)"
    ))
    fig.add_hline(y=avg, line_dash="dash", line_color="#2a1d13", line_width=1.5,
                  annotation_text=f"均值 {avg:.1f}x", annotation_position="right")
    if current_pe:
        fig.add_hline(y=current_pe, line_dash="dot", line_color="#b84040", line_width=1.5,
                      annotation_text=f"現在 {current_pe:.1f}x", annotation_position="left")
    fig.update_layout(
        title=f"{symbol} 歷史 P/E（5年）",
        height=260,
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=CHART_THEME["font"],
        yaxis=dict(gridcolor=CHART_THEME["gridcolor"], title="P/E"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=50, b=20, l=20, r=60),
        showlegend=False,
    )
    return fig

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
        st.error(f"❌ {d['symbol']} 數據獲取失敗：{d['error']}")
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
          <div style="margin-top:6px">
            <span class="signal-badge {sc['sig_class']}">{sc['emoji']} {sc['signal']}　{sc['score']}/100</span>
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

        refresh_interval = st.selectbox("自動刷新間隔", [30, 60, 120, 300],
                                         format_func=lambda x: f"{x}秒", index=1)
        st.session_state.refresh_interval = refresh_interval

        if auto_toggle:
            st.session_state.auto_refresh = not st.session_state.auto_refresh

        st.markdown("---")
        st.markdown("### 🔑 API 設定")
        groq_key  = st.text_input("Groq API Key", type="password",
                                   value=st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else "")
        tg_token  = st.text_input("Telegram Bot Token", type="password",
                                   value=st.secrets.get("TELEGRAM_BOT_TOKEN", "") if hasattr(st, "secrets") else "")
        tg_chat   = st.text_input("Telegram Chat ID",
                                   value=st.secrets.get("TELEGRAM_CHAT_ID", "") if hasattr(st, "secrets") else "")

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
                st.session_state.stock_data[sym] = fetch_stock(sym)
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
            sel_d = next(d for d in valid_with_hist if d["symbol"] == sel_sym)
            fig_hist = chart_hist_pe(sel_d["hist_pe"], sel_sym, sel_d.get("pe"))
            if fig_hist:
                st.plotly_chart(fig_hist, use_container_width=True, key="hist_pe_tab1")

            # Scoring reasons
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
                growth  = st.slider("預期EPS年增長率 %", 0, 100, 12)
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

                # Hist PE chart inline
                fig_h = chart_hist_pe(d.get("hist_pe", []), d["symbol"], d.get("pe"))
                if fig_h:
                    st.plotly_chart(fig_h, use_container_width=True, key=f"hist_pe_{d['symbol']}_tab4")

    # ── AUTO REFRESH ──────────────────────────────────────────────────────────
    if st.session_state.auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
