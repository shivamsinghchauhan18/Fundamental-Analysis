from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import math
import random
import time
import threading
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import SessionLocal, init_db
from shared.models import (
    HistoricalFinancials, CapacityAnalysis, SentimentData, ValuationModels, EarningsAlert,
    StatisticalFoundationData, CorrelationRiskData, GraphNetworkData, MacroIndicatorsData, PeerComparisonData
)

app = FastAPI(title="Fundamental Analysis Platform", description="Real-time stock analysis with live market data")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory cache with TTL
# ---------------------------------------------------------------------------
_cache = {}
_cache_lock = threading.Lock()

def cached_fetch(key, fetch_fn, ttl=300):
    now = time.time()
    with _cache_lock:
        if key in _cache:
            val, ts = _cache[key]
            if now - ts < ttl:
                return val
    result = fetch_fn()
    with _cache_lock:
        _cache[key] = (result, now)
    return result

# ---------------------------------------------------------------------------
# Technical indicator calculations (pure Python)
# ---------------------------------------------------------------------------
def calc_sma(prices, period):
    out = [None] * len(prices)
    for i in range(period - 1, len(prices)):
        out[i] = sum(prices[i - period + 1:i + 1]) / period
    return out

def calc_ema(prices, period):
    out = [None] * len(prices)
    if len(prices) < period or period <= 0:
        return out
    k = 2.0 / (period + 1)
    sma_start = sum(prices[:period]) / period
    out[period - 1] = sma_start
    for i in range(period, len(prices)):
        out[i] = prices[i] * k + out[i - 1] * (1 - k)
    return out

def calc_rsi(prices, period=14):
    out = [None] * len(prices)
    if len(prices) < period + 1:
        return out
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [max(d, 0) for d in deltas]
    losses = [max(-d, 0) for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0:
        out[period] = 100.0
    else:
        rs = avg_gain / avg_loss
        out[period] = 100.0 - 100.0 / (1.0 + rs)
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            out[i + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            out[i + 1] = 100.0 - 100.0 / (1.0 + rs)
    return out

def calc_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = calc_ema(prices, fast)
    ema_slow = calc_ema(prices, slow)
    macd_line = [None] * len(prices)
    for i in range(len(prices)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line[i] = ema_fast[i] - ema_slow[i]
    valid = [v for v in macd_line if v is not None]
    signal_line_vals = calc_ema(valid, signal) if len(valid) >= signal else [None] * len(valid)
    signal_line = [None] * len(prices)
    histogram = [None] * len(prices)
    vi = 0
    for i in range(len(prices)):
        if macd_line[i] is not None:
            if vi < len(signal_line_vals):
                signal_line[i] = signal_line_vals[vi]
            if macd_line[i] is not None and signal_line[i] is not None:
                histogram[i] = macd_line[i] - signal_line[i]
            vi += 1
    return macd_line, signal_line, histogram

def calc_bollinger(prices, period=20, num_std=2):
    sma = calc_sma(prices, period)
    upper = [None] * len(prices)
    lower = [None] * len(prices)
    for i in range(period - 1, len(prices)):
        window = prices[i - period + 1:i + 1]
        mean = sma[i]
        variance = sum((x - mean) ** 2 for x in window) / period
        std = math.sqrt(variance)
        upper[i] = mean + num_std * std
        lower[i] = mean - num_std * std
    return sma, upper, lower

def safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (TypeError, ValueError):
        return default

# ---------------------------------------------------------------------------
# yfinance helpers
# ---------------------------------------------------------------------------
def _fetch_yf_stock(ticker):
    import yfinance as yf
    t = yf.Ticker(ticker)
    info = t.info or {}
    return t, info

def _fetch_yf_history(ticker, period="1y", interval="1d"):
    import yfinance as yf
    t = yf.Ticker(ticker)
    df = t.history(period=period, interval=interval)
    return df

# ---------------------------------------------------------------------------
# NEW: Market Overview
# ---------------------------------------------------------------------------
@app.get("/api/market-overview")
def market_overview():
    def _fetch():
        import yfinance as yf
        indices = {
            "^GSPC": "S&P 500",
            "^IXIC": "NASDAQ",
            "^DJI": "Dow Jones",
            "^RUT": "Russell 2000",
            "^VIX": "VIX",
            "GC=F": "Gold",
            "CL=F": "Crude Oil",
            "BTC-USD": "Bitcoin",
        }
        result = []
        for sym, name in indices.items():
            try:
                t = yf.Ticker(sym)
                hist = t.history(period="5d")
                if hist.empty or len(hist) < 2:
                    continue
                current = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                change = current - prev
                change_pct = (change / prev) * 100 if prev != 0 else 0
                result.append({
                    "symbol": sym,
                    "name": name,
                    "price": round(current, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                })
            except Exception:
                continue

        trending_tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "TSLA", "META", "NFLX"]
        trending = []
        for sym in trending_tickers:
            try:
                t = yf.Ticker(sym)
                hist = t.history(period="5d")
                if hist.empty or len(hist) < 2:
                    continue
                info = t.info or {}
                current = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                change_pct = ((current - prev) / prev) * 100 if prev != 0 else 0
                trending.append({
                    "symbol": sym,
                    "name": info.get("shortName", sym),
                    "price": round(current, 2),
                    "change_pct": round(change_pct, 2),
                    "market_cap": safe_float(info.get("marketCap", 0)),
                    "pe_ratio": safe_float(info.get("trailingPE", 0)),
                    "volume": safe_float(info.get("volume", 0)),
                })
            except Exception:
                continue
        return {"indices": result, "trending": trending}
    return cached_fetch("market_overview", _fetch, ttl=120)

# ---------------------------------------------------------------------------
# NEW: Live Stock Analysis (any ticker)
# ---------------------------------------------------------------------------
@app.get("/api/stock/{ticker}")
def get_stock_analysis(ticker: str, period: str = "1y"):
    ticker = ticker.upper().strip()
    if not ticker.isalpha() or len(ticker) > 10:
        raise HTTPException(status_code=400, detail="Invalid ticker symbol")

    def _fetch():
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.info or {}
        hist = t.history(period=period, interval="1d")
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

        dates = [d.strftime("%Y-%m-%d") for d in hist.index]
        opens = [round(float(v), 2) for v in hist["Open"]]
        highs = [round(float(v), 2) for v in hist["High"]]
        lows = [round(float(v), 2) for v in hist["Low"]]
        closes = [round(float(v), 2) for v in hist["Close"]]
        volumes = [int(v) for v in hist["Volume"]]

        sma_20 = calc_sma(closes, 20)
        sma_50 = calc_sma(closes, 50)
        sma_200 = calc_sma(closes, 200)
        ema_12 = calc_ema(closes, 12)
        ema_26 = calc_ema(closes, 26)
        rsi = calc_rsi(closes, 14)
        macd_line, signal_line, macd_hist = calc_macd(closes)
        bb_mid, bb_upper, bb_lower = calc_bollinger(closes, 20, 2)

        current_price = closes[-1]
        prev_close = closes[-2] if len(closes) > 1 else closes[0]
        price_change = current_price - prev_close
        price_change_pct = (price_change / prev_close) * 100 if prev_close else 0

        high_52w = max(closes[-min(252, len(closes)):])
        low_52w = min(closes[-min(252, len(closes)):])

        daily_returns = [(closes[i] - closes[i - 1]) / closes[i - 1] * 100 for i in range(1, len(closes))]
        avg_return = sum(daily_returns) / len(daily_returns) if daily_returns else 0
        volatility = math.sqrt(sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)) if daily_returns else 0
        annualized_vol = volatility * math.sqrt(252)

        perf_1d = price_change_pct
        perf_1w = ((closes[-1] / closes[-min(5, len(closes))]) - 1) * 100 if len(closes) >= 5 else 0
        perf_1m = ((closes[-1] / closes[-min(21, len(closes))]) - 1) * 100 if len(closes) >= 21 else 0
        perf_3m = ((closes[-1] / closes[-min(63, len(closes))]) - 1) * 100 if len(closes) >= 63 else 0
        perf_1y = ((closes[-1] / closes[0]) - 1) * 100

        return {
            "ticker": ticker,
            "name": info.get("shortName", info.get("longName", ticker)),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "description": info.get("longBusinessSummary", ""),
            "website": info.get("website", ""),
            "country": info.get("country", ""),
            "employees": info.get("fullTimeEmployees", 0),
            "price": {
                "current": current_price,
                "change": round(price_change, 2),
                "change_pct": round(price_change_pct, 2),
                "open": opens[-1],
                "high": highs[-1],
                "low": lows[-1],
                "prev_close": prev_close,
                "volume": volumes[-1],
                "avg_volume": int(safe_float(info.get("averageVolume", 0))),
                "high_52w": round(high_52w, 2),
                "low_52w": round(low_52w, 2),
            },
            "fundamentals": {
                "market_cap": safe_float(info.get("marketCap", 0)),
                "pe_ratio": safe_float(info.get("trailingPE", 0)),
                "forward_pe": safe_float(info.get("forwardPE", 0)),
                "peg_ratio": safe_float(info.get("pegRatio", 0)),
                "eps": safe_float(info.get("trailingEps", 0)),
                "dividend_yield": safe_float(info.get("dividendYield", 0)) * 100,
                "beta": safe_float(info.get("beta", 0)),
                "profit_margin": safe_float(info.get("profitMargins", 0)) * 100,
                "revenue": safe_float(info.get("totalRevenue", 0)),
                "revenue_growth": safe_float(info.get("revenueGrowth", 0)) * 100,
                "gross_margins": safe_float(info.get("grossMargins", 0)) * 100,
                "operating_margins": safe_float(info.get("operatingMargins", 0)) * 100,
                "roe": safe_float(info.get("returnOnEquity", 0)) * 100,
                "debt_to_equity": safe_float(info.get("debtToEquity", 0)),
                "current_ratio": safe_float(info.get("currentRatio", 0)),
                "book_value": safe_float(info.get("bookValue", 0)),
                "price_to_book": safe_float(info.get("priceToBook", 0)),
                "free_cash_flow": safe_float(info.get("freeCashflow", 0)),
            },
            "performance": {
                "perf_1d": round(perf_1d, 2),
                "perf_1w": round(perf_1w, 2),
                "perf_1m": round(perf_1m, 2),
                "perf_3m": round(perf_3m, 2),
                "perf_1y": round(perf_1y, 2),
                "volatility": round(annualized_vol, 2),
            },
            "chart": {
                "dates": dates,
                "open": opens,
                "high": highs,
                "low": lows,
                "close": closes,
                "volume": volumes,
            },
            "technicals": {
                "sma_20": sma_20,
                "sma_50": sma_50,
                "sma_200": sma_200,
                "ema_12": ema_12,
                "ema_26": ema_26,
                "rsi": rsi,
                "macd_line": macd_line,
                "macd_signal": signal_line,
                "macd_histogram": macd_hist,
                "bb_upper": bb_upper,
                "bb_middle": bb_mid,
                "bb_lower": bb_lower,
            },
        }
    return cached_fetch(f"stock_{ticker}_{period}", _fetch, ttl=120)

# ---------------------------------------------------------------------------
# NEW: Live Quote (lightweight, short TTL)
# ---------------------------------------------------------------------------
@app.get("/api/live-quote/{ticker}")
def get_live_quote(ticker: str):
    ticker = ticker.upper().strip()

    def _fetch():
        import yfinance as yf
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data for {ticker}")
        info = t.info or {}
        current = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current
        return {
            "ticker": ticker,
            "name": info.get("shortName", ticker),
            "price": round(current, 2),
            "change": round(current - prev, 2),
            "change_pct": round(((current - prev) / prev) * 100 if prev else 0, 2),
            "volume": int(hist["Volume"].iloc[-1]),
        }
    return cached_fetch(f"quote_{ticker}", _fetch, ttl=60)

# ---------------------------------------------------------------------------
# NEW: Compare multiple stocks
# ---------------------------------------------------------------------------
@app.get("/api/compare")
def compare_stocks(tickers: str = Query(..., description="Comma-separated tickers")):
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if len(ticker_list) < 2 or len(ticker_list) > 6:
        raise HTTPException(status_code=400, detail="Provide 2-6 tickers")

    def _fetch():
        import yfinance as yf
        results = []
        for sym in ticker_list:
            try:
                t = yf.Ticker(sym)
                info = t.info or {}
                hist = t.history(period="1y", interval="1d")
                if hist.empty:
                    continue
                closes = [round(float(v), 2) for v in hist["Close"]]
                dates = [d.strftime("%Y-%m-%d") for d in hist.index]
                base = closes[0] if closes[0] != 0 else 1
                normalized = [round((c / base) * 100, 2) for c in closes]
                current = closes[-1]
                prev = closes[-2] if len(closes) > 1 else current
                results.append({
                    "ticker": sym,
                    "name": info.get("shortName", sym),
                    "dates": dates,
                    "closes": closes,
                    "normalized": normalized,
                    "current_price": current,
                    "change_pct": round(((current - prev) / prev) * 100 if prev else 0, 2),
                    "perf_ytd": round(((closes[-1] / closes[0]) - 1) * 100, 2),
                    "market_cap": safe_float(info.get("marketCap", 0)),
                    "pe_ratio": safe_float(info.get("trailingPE", 0)),
                    "peg_ratio": safe_float(info.get("pegRatio", 0)),
                    "eps": safe_float(info.get("trailingEps", 0)),
                    "revenue_growth": safe_float(info.get("revenueGrowth", 0)) * 100,
                    "profit_margin": safe_float(info.get("profitMargins", 0)) * 100,
                    "beta": safe_float(info.get("beta", 0)),
                    "dividend_yield": safe_float(info.get("dividendYield", 0)) * 100,
                    "roe": safe_float(info.get("returnOnEquity", 0)) * 100,
                    "debt_to_equity": safe_float(info.get("debtToEquity", 0)),
                    "volumes": [int(v) for v in hist["Volume"]],
                })
            except Exception:
                continue
        return {"stocks": results}
    return cached_fetch(f"compare_{'_'.join(ticker_list)}", _fetch, ttl=180)


# ---------------------------------------------------------------------------
# NEW: Sector Heatmap (Bloomberg HEAT)
# ---------------------------------------------------------------------------
SECTOR_ETFS = [
    ("XLK", "Technology"),
    ("XLF", "Financials"),
    ("XLV", "Health Care"),
    ("XLY", "Cons. Discretionary"),
    ("XLP", "Cons. Staples"),
    ("XLE", "Energy"),
    ("XLI", "Industrials"),
    ("XLU", "Utilities"),
    ("XLB", "Materials"),
    ("XLRE", "Real Estate"),
    ("XLC", "Communication"),
]

SECTOR_CONSTITUENTS = {
    "XLK": ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "AMD", "ADBE", "CSCO", "ACN"],
    "XLF": ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "SPGI", "AXP"],
    "XLV": ["LLY", "UNH", "JNJ", "MRK", "ABBV", "TMO", "ABT", "PFE", "DHR", "AMGN"],
    "XLY": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "BKNG", "TJX", "SBUX", "ABNB"],
    "XLP": ["WMT", "PG", "COST", "KO", "PEP", "PM", "MDLZ", "MO", "CL", "TGT"],
    "XLE": ["XOM", "CVX", "COP", "EOG", "SLB", "OXY", "PSX", "MPC", "VLO", "PXD"],
    "XLI": ["GE", "CAT", "RTX", "HON", "UPS", "UNP", "BA", "LMT", "DE", "ETN"],
    "XLU": ["NEE", "SO", "DUK", "CEG", "AEP", "SRE", "D", "PCG", "EXC", "XEL"],
    "XLB": ["LIN", "SHW", "APD", "ECL", "FCX", "NEM", "DOW", "DD", "PPG", "NUE"],
    "XLRE": ["PLD", "AMT", "EQIX", "WELL", "DLR", "SPG", "PSA", "O", "CCI", "EXR"],
    "XLC": ["GOOG", "META", "NFLX", "DIS", "TMUS", "VZ", "T", "CMCSA", "EA", "WBD"],
}

@app.get("/api/sector-heatmap")
def sector_heatmap():
    def _fetch():
        import yfinance as yf
        sectors = []
        for etf, label in SECTOR_ETFS:
            try:
                t = yf.Ticker(etf)
                hist = t.history(period="5d")
                if hist.empty or len(hist) < 2:
                    continue
                cur = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                chg_pct = ((cur - prev) / prev) * 100 if prev else 0.0
                constituents = []
                for sym in SECTOR_CONSTITUENTS.get(etf, []):
                    try:
                        ct = yf.Ticker(sym)
                        ch = ct.history(period="5d")
                        if ch.empty or len(ch) < 2:
                            continue
                        c_cur = float(ch["Close"].iloc[-1])
                        c_prev = float(ch["Close"].iloc[-2])
                        c_chg = ((c_cur - c_prev) / c_prev) * 100 if c_prev else 0.0
                        info = ct.info or {}
                        constituents.append({
                            "symbol": sym,
                            "price": round(c_cur, 2),
                            "change_pct": round(c_chg, 2),
                            "market_cap": safe_float(info.get("marketCap", 0)),
                        })
                    except Exception:
                        continue
                sectors.append({
                    "etf": etf,
                    "label": label,
                    "price": round(cur, 2),
                    "change_pct": round(chg_pct, 2),
                    "constituents": constituents,
                })
            except Exception:
                continue
        return {"sectors": sectors, "generated_at": datetime.now(timezone.utc).isoformat()}
    return cached_fetch("sector_heatmap", _fetch, ttl=180)

# ---------------------------------------------------------------------------
# NEW: News Feed (Bloomberg N)
# ---------------------------------------------------------------------------
@app.get("/api/news/{ticker}")
def get_news(ticker: str):
    ticker = ticker.upper().strip()
    def _fetch():
        import yfinance as yf
        import re
        t = yf.Ticker(ticker)
        # Pull company name for better relevance matching ("Apple" matches more than "AAPL")
        name_aliases = [ticker]
        try:
            info = t.info or {}
            full = info.get("shortName") or info.get("longName") or ""
            if full:
                # First token: "Apple Inc." -> "Apple"
                first = re.split(r"[\s,\.]+", full.strip())[0]
                if first and len(first) >= 3 and first.upper() not in {"INC", "CORP", "LTD", "PLC", "THE"}:
                    name_aliases.append(first.upper())
        except Exception:
            pass
        try:
            raw = t.news or []
        except Exception:
            raw = []
        out = []
        for item in raw[:40]:
            content = item.get("content") if isinstance(item, dict) else None
            if isinstance(content, dict):
                title = content.get("title", "") or ""
                summary = content.get("summary", "") or content.get("description", "") or ""
                provider = content.get("provider") or {}
                pub = provider.get("displayName", "") if isinstance(provider, dict) else ""
                # Prefer canonicalUrl, fall back to clickThroughUrl (Yahoo proxy)
                link = ""
                cu = content.get("canonicalUrl")
                if isinstance(cu, dict):
                    link = cu.get("url") or ""
                if not link:
                    cth = content.get("clickThroughUrl")
                    if isinstance(cth, dict):
                        link = cth.get("url") or ""
                ts_str = content.get("pubDate") or content.get("displayTime")
                if ts_str:
                    try:
                        ts = int(datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp())
                    except Exception:
                        ts = int(time.time())
                else:
                    ts = int(time.time())
                # Thumbnail (small)
                thumb_url = ""
                thumb = content.get("thumbnail")
                if isinstance(thumb, dict):
                    resolutions = thumb.get("resolutions") or []
                    for r in resolutions:
                        if isinstance(r, dict) and r.get("tag") and "x" in str(r.get("tag", "")):
                            thumb_url = r.get("url") or ""
                            break
                    if not thumb_url:
                        thumb_url = thumb.get("originalUrl") or ""
            else:
                # Legacy yfinance format
                title = item.get("title", "") or ""
                pub = item.get("publisher", "") or ""
                summary = item.get("summary", "") or ""
                link = item.get("link", "") or ""
                ts = int(item.get("providerPublishTime", time.time()))
                thumb_url = ""
            if not title:
                continue
            # Relevance: 2 = ticker/name in title, 1 = in summary, 0 = neither (related by Yahoo algo only)
            title_u = title.upper()
            summary_u = summary.upper()
            in_title = any(alias in title_u for alias in name_aliases)
            in_summary = any(alias in summary_u for alias in name_aliases)
            if in_title:
                relevance = 2
            elif in_summary:
                relevance = 1
            else:
                relevance = 0
            out.append({
                "title": title,
                "publisher": pub,
                "summary": (summary or "")[:300],
                "link": link,
                "timestamp": ts,
                "time_str": datetime.fromtimestamp(ts).strftime("%H:%M"),
                "date_str": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                "thumb": thumb_url,
                "relevance": relevance,
            })
        # Sort: most-relevant first, then newest first within each tier
        out.sort(key=lambda r: (-r["relevance"], -r["timestamp"]))
        return {
            "ticker": ticker,
            "aliases": name_aliases,
            "news": out,
            "counts": {
                "total": len(out),
                "title": sum(1 for n in out if n["relevance"] == 2),
                "summary": sum(1 for n in out if n["relevance"] == 1),
                "related": sum(1 for n in out if n["relevance"] == 0),
            },
        }
    return cached_fetch(f"news_{ticker}", _fetch, ttl=300)

# ---------------------------------------------------------------------------
# NEW: Economic Calendar (Bloomberg ECO)
# ---------------------------------------------------------------------------
@app.get("/api/economic-calendar")
def economic_calendar():
    def _fetch():
        today = datetime.now()
        events = []

        def next_weekday_in_month(year, month, weekday, occurrence):
            d = datetime(year, month, 1)
            count = 0
            while d.month == month:
                if d.weekday() == weekday:
                    count += 1
                    if count == occurrence:
                        return d
                d += timedelta(days=1)
            return None

        for offset in range(0, 4):
            month = today.month + offset
            year = today.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            cpi = datetime(year, month, min(13, 28))
            ppi = datetime(year, month, min(15, 28))
            retail = datetime(year, month, min(17, 28))
            gdp = datetime(year, month, min(28, 28))
            nfp = next_weekday_in_month(year, month, 4, 1)
            fomc = next_weekday_in_month(year, month, 2, 3)
            for d, name, importance, fc, prev in [
                (cpi,    "CPI YoY",                "high",   "3.1%",  "3.2%"),
                (ppi,    "PPI YoY",                "med",    "1.6%",  "1.7%"),
                (retail, "Retail Sales MoM",       "med",    "0.4%",  "0.7%"),
                (gdp,    "GDP QoQ Annualized",     "high",   "2.4%",  "2.5%"),
                (nfp,    "Non-Farm Payrolls",      "high",   "175K",  "187K"),
                (fomc,   "FOMC Rate Decision",     "high",   "5.50%", "5.50%"),
            ]:
                if d is None or d < today - timedelta(days=2):
                    continue
                events.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "time": "08:30" if name in ("CPI YoY", "PPI YoY", "Retail Sales MoM", "GDP QoQ Annualized", "Non-Farm Payrolls") else "14:00",
                    "country": "US",
                    "event": name,
                    "importance": importance,
                    "forecast": fc,
                    "previous": prev,
                })

        earnings_picks = [
            ("AAPL", "Q earnings"), ("MSFT", "Q earnings"), ("NVDA", "Q earnings"),
            ("GOOG", "Q earnings"), ("AMZN", "Q earnings"), ("META", "Q earnings"),
            ("TSLA", "Q earnings"), ("JPM", "Q earnings"), ("WMT", "Q earnings"),
        ]
        for i, (sym, label) in enumerate(earnings_picks):
            d = today + timedelta(days=3 + i * 4)
            events.append({
                "date": d.strftime("%Y-%m-%d"),
                "time": "16:30",
                "country": "US",
                "event": f"{sym} {label}",
                "importance": "high",
                "forecast": "—",
                "previous": "—",
            })
        events.sort(key=lambda e: (e["date"], e["time"]))
        return {"events": events[:40], "generated_at": today.isoformat()}
    return cached_fetch("eco_calendar", _fetch, ttl=3600)

# ---------------------------------------------------------------------------
# NEW: Screener (Bloomberg EQS) - top movers
# ---------------------------------------------------------------------------
SCREENER_UNIVERSE = [
    "AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "LLY",
    "AVGO", "JPM", "V", "WMT", "UNH", "XOM", "MA", "PG", "JNJ", "ORCL",
    "HD", "COST", "ABBV", "MRK", "BAC", "NFLX", "CVX", "KO", "AMD", "ADBE",
    "PEP", "TMO", "CRM", "MCD", "CSCO", "ACN", "LIN", "ABT", "WFC", "INTU",
    "DIS", "TXN", "PLTR", "QCOM", "IBM", "GS", "BA", "CAT", "GE", "PFE",
]

@app.get("/api/screener")
def screener(mode: str = Query("gainers", description="gainers|losers|volume|active")):
    def _fetch():
        import yfinance as yf
        rows = []
        for sym in SCREENER_UNIVERSE:
            try:
                t = yf.Ticker(sym)
                hist = t.history(period="5d")
                if hist.empty or len(hist) < 2:
                    continue
                cur = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2])
                chg_pct = ((cur - prev) / prev) * 100 if prev else 0.0
                vol = int(hist["Volume"].iloc[-1])
                info = t.info or {}
                rows.append({
                    "symbol": sym,
                    "name": info.get("shortName", sym),
                    "price": round(cur, 2),
                    "change_pct": round(chg_pct, 2),
                    "volume": vol,
                    "market_cap": safe_float(info.get("marketCap", 0)),
                    "pe_ratio": safe_float(info.get("trailingPE", 0)),
                })
            except Exception:
                continue
        if mode == "gainers":
            rows.sort(key=lambda r: r["change_pct"], reverse=True)
        elif mode == "losers":
            rows.sort(key=lambda r: r["change_pct"])
        elif mode == "volume" or mode == "active":
            rows.sort(key=lambda r: r["volume"], reverse=True)
        return {"mode": mode, "rows": rows[:25]}
    return cached_fetch(f"screener_{mode}", _fetch, ttl=180)

# ---------------------------------------------------------------------------
# NEW: Live Correlation Matrix (Bloomberg-style, any tickers)
# ---------------------------------------------------------------------------
DEFAULT_CORR_UNIVERSE = SCREENER_UNIVERSE[:30]

@app.get("/api/correlation-matrix")
def correlation_matrix(
    tickers: str = Query("", description="Comma-separated tickers; empty for default 30-name universe"),
    period: str = Query("1y", description="1mo|3mo|6mo|1y|2y|5y"),
    order: str = Query("input", description="input|cluster|avg"),
):
    if tickers:
        tlist = []
        for t in tickers.split(","):
            t = t.strip().upper()
            if t and t not in tlist:
                tlist.append(t)
    else:
        tlist = list(DEFAULT_CORR_UNIVERSE)
    if len(tlist) < 2:
        raise HTTPException(status_code=400, detail="Provide at least 2 tickers")
    if len(tlist) > 60:
        raise HTTPException(status_code=400, detail="Max 60 tickers")
    if period not in {"1mo", "3mo", "6mo", "1y", "2y", "5y"}:
        raise HTTPException(status_code=400, detail="Invalid period")

    cache_key = f"corrmtx_{','.join(tlist)}_{period}_{order}"

    def _fetch():
        import yfinance as yf
        import numpy as np
        import pandas as pd
        # Bulk download to minimize HTTP round-trips
        try:
            df = yf.download(
                tickers=tlist, period=period, interval="1d",
                auto_adjust=True, progress=False, threads=True,
                group_by="column",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"yfinance bulk download failed: {e}")

        # Extract a Close-price DataFrame indexed by date with ticker columns
        if isinstance(df.columns, pd.MultiIndex):
            if "Close" in df.columns.get_level_values(0):
                closes = df["Close"]
            else:
                raise HTTPException(status_code=500, detail="yfinance returned no Close column")
        else:
            # Single-ticker shape: shouldn't happen since we require 2+, but guard anyway
            closes = df[["Close"]].rename(columns={"Close": tlist[0]})

        closes = closes.dropna(axis=1, how="all")
        if closes.shape[1] < 2:
            raise HTTPException(status_code=500, detail="Could not fetch enough usable tickers")

        # Daily log returns; drop rows with any NaN to keep matrix consistent
        log_ret = np.log(closes / closes.shift(1)).dropna(how="any")
        if log_ret.shape[0] < 20:
            raise HTTPException(status_code=500, detail=f"Only {log_ret.shape[0]} usable observations after alignment")

        corr = log_ret.corr(method="pearson")
        out_tickers = [str(t) for t in corr.columns.tolist()]
        mat = corr.to_numpy().astype(float)

        # Optional reordering for visual block-diagonal structure
        if order == "avg":
            # Sort by average pairwise correlation (descending)
            avg_per = np.nanmean(np.where(np.eye(len(mat), dtype=bool), np.nan, mat), axis=1)
            idx = np.argsort(-avg_per)
        elif order == "cluster":
            # Greedy nearest-neighbor reorder starting from highest-avg ticker
            n = len(mat)
            avg_per = np.nanmean(np.where(np.eye(n, dtype=bool), np.nan, mat), axis=1)
            start = int(np.argmax(avg_per))
            visited = {start}
            order_list = [start]
            while len(order_list) < n:
                last = order_list[-1]
                # Nearest = most correlated, among unvisited
                row = mat[last].copy()
                for v in visited:
                    row[v] = -np.inf
                nxt = int(np.argmax(row))
                order_list.append(nxt)
                visited.add(nxt)
            idx = np.array(order_list)
        else:
            idx = np.arange(len(mat))

        out_tickers = [out_tickers[i] for i in idx]
        mat = mat[idx][:, idx]
        # Round, convert NaN to None for JSON
        matrix = [[(None if (val != val) else round(float(val), 3)) for val in row] for row in mat]

        # Stats
        n = len(out_tickers)
        off = []
        for i in range(n):
            for j in range(i + 1, n):
                v = matrix[i][j]
                if v is not None:
                    off.append(v)
        avg = (sum(off) / len(off)) if off else 0.0
        # Highest / lowest pairs
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                v = matrix[i][j]
                if v is not None:
                    pairs.append((v, out_tickers[i], out_tickers[j]))
        pairs.sort()
        lowest = [{"a": p[1], "b": p[2], "corr": p[0]} for p in pairs[:5]]
        highest = [{"a": p[1], "b": p[2], "corr": p[0]} for p in reversed(pairs[-5:])]

        return {
            "tickers": out_tickers,
            "requested": tlist,
            "dropped": [t for t in tlist if t not in out_tickers],
            "matrix": matrix,
            "period": period,
            "order": order,
            "observations": int(log_ret.shape[0]),
            "avg_correlation": round(avg, 3),
            "highest_pairs": highest,
            "lowest_pairs": lowest,
        }

    return cached_fetch(cache_key, _fetch, ttl=600)

# ---------------------------------------------------------------------------
# NEW: Asset Correlation Network (Mantegna-style)
#     Method = MST | threshold | kNN
#     Community detection via greedy modularity
# ---------------------------------------------------------------------------
@app.get("/api/network")
def network_graph(
    tickers: str = Query("", description="Comma-separated tickers; empty for default 30-name universe"),
    period: str = Query("1y", description="1mo|3mo|6mo|1y|2y|5y"),
    method: str = Query("mst", description="mst|threshold|knn"),
    threshold: float = Query(0.5, description="For method=threshold: minimum |rho| for an edge"),
    k: int = Query(3, description="For method=knn: nearest-neighbor count"),
):
    if tickers:
        tlist = []
        for t in tickers.split(","):
            t = t.strip().upper()
            if t and t not in tlist:
                tlist.append(t)
    else:
        tlist = list(DEFAULT_CORR_UNIVERSE)
    if len(tlist) < 3:
        raise HTTPException(status_code=400, detail="Need at least 3 tickers")
    if len(tlist) > 60:
        raise HTTPException(status_code=400, detail="Max 60 tickers")
    if method not in {"mst", "threshold", "knn"}:
        raise HTTPException(status_code=400, detail="Invalid method")
    if period not in {"1mo", "3mo", "6mo", "1y", "2y", "5y"}:
        raise HTTPException(status_code=400, detail="Invalid period")
    threshold = max(0.05, min(0.99, threshold))
    k = max(1, min(10, k))

    cache_key = f"network_{','.join(tlist)}_{period}_{method}_{threshold}_{k}"

    def _fetch():
        import yfinance as yf
        import numpy as np
        import pandas as pd
        import networkx as nx

        try:
            df = yf.download(
                tickers=tlist, period=period, interval="1d",
                auto_adjust=True, progress=False, threads=True,
                group_by="column",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"yfinance bulk download failed: {e}")

        if isinstance(df.columns, pd.MultiIndex):
            if "Close" not in df.columns.get_level_values(0):
                raise HTTPException(status_code=500, detail="yfinance returned no Close column")
            closes = df["Close"]
        else:
            closes = df[["Close"]].rename(columns={"Close": tlist[0]})

        closes = closes.dropna(axis=1, how="all")
        if closes.shape[1] < 3:
            raise HTTPException(status_code=500, detail="Fewer than 3 tickers had usable data")

        log_ret = np.log(closes / closes.shift(1)).dropna(how="any")
        if log_ret.shape[0] < 20:
            raise HTTPException(status_code=500, detail=f"Only {log_ret.shape[0]} usable observations")

        corr = log_ret.corr(method="pearson")
        symbols = [str(s) for s in corr.columns.tolist()]
        n = len(symbols)
        rho = corr.to_numpy().astype(float)
        # Mantegna distance: d = sqrt(2(1 - rho)), range [0, 2]
        dist = np.sqrt(np.clip(2.0 * (1.0 - rho), 0.0, 4.0))

        # Build the full weighted graph (complete graph minus self-loops)
        G_full = nx.Graph()
        for s in symbols:
            G_full.add_node(s)
        for i in range(n):
            for j in range(i + 1, n):
                G_full.add_edge(symbols[i], symbols[j],
                                weight=float(dist[i, j]),
                                corr=float(rho[i, j]),
                                abs_corr=float(abs(rho[i, j])))

        # Filter by method
        if method == "mst":
            G = nx.minimum_spanning_tree(G_full, weight="weight")
        elif method == "threshold":
            G = nx.Graph()
            for s in symbols:
                G.add_node(s)
            for i in range(n):
                for j in range(i + 1, n):
                    if abs(rho[i, j]) >= threshold:
                        G.add_edge(symbols[i], symbols[j],
                                   weight=float(dist[i, j]),
                                   corr=float(rho[i, j]))
        else:  # knn
            G = nx.Graph()
            for s in symbols:
                G.add_node(s)
            for i in range(n):
                d_i = dist[i].copy()
                d_i[i] = np.inf
                nn = np.argsort(d_i)[:k]
                for j in nn:
                    a, b = symbols[i], symbols[int(j)]
                    if not G.has_edge(a, b):
                        G.add_edge(a, b,
                                   weight=float(dist[i, int(j)]),
                                   corr=float(rho[i, int(j)]))

        # Centralities
        deg = nx.degree_centrality(G)
        try:
            bet = nx.betweenness_centrality(G, weight="weight")
        except Exception:
            bet = {s: 0.0 for s in symbols}
        # Eigenvector centrality on largest connected component (power iteration; no scipy required).
        # Computed unweighted so it captures pure structural position regardless of edge strength.
        try:
            if G.number_of_edges() > 0:
                largest = max(nx.connected_components(G), key=len)
                Gc = G.subgraph(largest).copy()
                eig_part = nx.eigenvector_centrality(Gc, max_iter=1000, tol=1e-6)
                eig = {s: eig_part.get(s, 0.0) for s in symbols}
            else:
                eig = {s: 0.0 for s in symbols}
        except (nx.PowerIterationFailedConvergence, Exception):
            eig = {s: 0.0 for s in symbols}

        # Community detection
        try:
            communities = list(nx.community.greedy_modularity_communities(G))
        except Exception:
            communities = [set(symbols)]
        cluster_id = {}
        clusters_out = []
        for i, c in enumerate(communities):
            members = sorted(list(c))
            for s in members:
                cluster_id[s] = i
            clusters_out.append({"id": i, "size": len(members), "members": members})

        nodes = []
        for s in symbols:
            nodes.append({
                "id": s, "label": s,
                "cluster": cluster_id.get(s, -1),
                "degree": int(G.degree(s)),
                "degree_centrality": round(deg.get(s, 0.0), 4),
                "betweenness_centrality": round(bet.get(s, 0.0), 4),
                "eigenvector_centrality": round(eig.get(s, 0.0), 4),
            })

        edges = []
        for a, b, attrs in G.edges(data=True):
            edges.append({
                "from": a, "to": b,
                "weight": round(float(attrs.get("weight", 0.0)), 3),
                "corr": round(float(attrs.get("corr", 0.0)), 3),
            })

        n_components = nx.number_connected_components(G)
        isolated = [s for s in symbols if G.degree(s) == 0]
        top_betweenness = sorted(nodes, key=lambda x: -x["betweenness_centrality"])[:8]
        top_degree = sorted(nodes, key=lambda x: -x["degree_centrality"])[:8]
        top_eigenvector = sorted(nodes, key=lambda x: -x["eigenvector_centrality"])[:8]

        return {
            "method": method,
            "period": period,
            "threshold": threshold if method == "threshold" else None,
            "k": k if method == "knn" else None,
            "observations": int(log_ret.shape[0]),
            "n_nodes": len(nodes),
            "n_edges": len(edges),
            "n_components": int(n_components),
            "isolated": isolated,
            "clusters": clusters_out,
            "nodes": nodes,
            "edges": edges,
            "top_betweenness": top_betweenness,
            "top_degree": top_degree,
            "top_eigenvector": top_eigenvector,
            "dropped": [t for t in tlist if t not in symbols],
        }

    return cached_fetch(cache_key, _fetch, ttl=900)

# ---------------------------------------------------------------------------
# NEW: Market Session Status (for status bar)
# ---------------------------------------------------------------------------
@app.get("/api/market-status")
def market_status():
    now = datetime.now(timezone.utc)
    et_offset = timedelta(hours=-4)
    et = now + et_offset
    weekday = et.weekday()
    hhmm = et.hour * 60 + et.minute
    if weekday >= 5:
        session = "CLOSED"
    elif hhmm < 4 * 60:
        session = "CLOSED"
    elif hhmm < 9 * 60 + 30:
        session = "PRE-MKT"
    elif hhmm < 16 * 60:
        session = "OPEN"
    elif hhmm < 20 * 60:
        session = "AFTER"
    else:
        session = "CLOSED"
    return {
        "session": session,
        "et_time": et.strftime("%H:%M:%S"),
        "et_date": et.strftime("%Y-%m-%d"),
        "weekday": et.strftime("%a"),
    }


# ===========================================================================
# EXISTING ENDPOINTS (preserved from v2.0)
# ===========================================================================

SHARES_OUTSTANDING = {"TSLA": 3.18, "NVDA": 2.30, "PLTR": 2.29}

def run_monte_carlo(current_price, base_growth, std_dev, paths=100, steps=252):
    dt = 1.0 / steps
    mu = base_growth / 100.0
    sigma = std_dev
    drift = (mu - 0.5 * sigma**2) * dt
    diffusion = sigma * math.sqrt(dt)
    final_prices = []
    sample_paths = []
    for i in range(paths):
        path = [current_price]
        current = current_price
        for _ in range(steps):
            z = random.normalvariate(0.0, 1.0)
            current *= math.exp(drift + diffusion * z)
            if i < 100:
                path.append(current)
        final_prices.append(current)
        if i < 100:
            sample_paths.append(path)
    final_prices.sort()
    def get_percentile(sorted_list, pct):
        idx = (len(sorted_list) - 1) * (pct / 100.0)
        low = math.floor(idx)
        high = math.ceil(idx)
        if low == high:
            return sorted_list[low]
        return sorted_list[low] * (high - idx) + sorted_list[high] * (idx - low)
    percentiles = {
        "p5": float(get_percentile(final_prices, 5)),
        "p25": float(get_percentile(final_prices, 25)),
        "p50": float(get_percentile(final_prices, 50)),
        "p75": float(get_percentile(final_prices, 75)),
        "p95": float(get_percentile(final_prices, 95))
    }
    var_95 = max(0.0, 100.0 * (1.0 - percentiles["p5"] / current_price))
    return sample_paths, percentiles, var_95

def get_unified_data(db, company_code: str):
    company_code = company_code.upper()
    hist = db.query(HistoricalFinancials).filter(HistoricalFinancials.company == company_code).first()
    cap = db.query(CapacityAnalysis).filter(CapacityAnalysis.company == company_code).first()
    sent = db.query(SentimentData).filter(SentimentData.company == company_code).first()
    val = db.query(ValuationModels).filter(ValuationModels.company == company_code).first()
    if not hist:
        raise HTTPException(status_code=404, detail=f"Company {company_code} not found.")
    return {
        "company": company_code,
        "historical": {
            "current_price": hist.current_price,
            "current_pe": hist.current_pe,
            "forward_pe": hist.forward_pe,
            "current_peg": hist.current_peg,
            "revenue_cagr_5y": hist.revenue_cagr_5y,
            "gross_margin_trend": hist.gross_margin_trend,
            "operating_margin_trend": hist.operating_margin_trend,
            "net_margin_trend": hist.net_margin_trend,
            "fcf_margin": hist.fcf_margin,
            "sector_median_pe": hist.sector_median_pe,
            "revenue_5y": hist.revenue_5y,
            "ebitda_5y": hist.ebitda_5y,
            "net_income_5y": hist.net_income_5y,
            "fcf_5y": hist.fcf_5y,
            "roe": hist.roe,
            "roa": hist.roa,
            "alert": hist.alert,
            "educational_note": hist.educational_note
        },
        "capacity": {
            "production_capacity": cap.production_capacity if cap else {},
            "backlog_trends": cap.backlog_trends if cap else {},
            "implied_revenue_required": cap.implied_revenue_required if cap else 0.0,
            "realistic_achievable_revenue": cap.realistic_achievable_revenue if cap else 0.0,
            "valuation_gap": cap.valuation_gap if cap else 0.0,
            "waterfall_data": cap.waterfall_data if cap else {},
            "educational_note": cap.educational_note if cap else ""
        },
        "sentiment": {
            "sentiment_momentum_score": sent.sentiment_momentum_score if sent else 0.0,
            "news_sentiment_score": sent.news_sentiment_score if sent else 0.0,
            "news_sentiment_distribution": sent.news_sentiment_distribution if sent else {},
            "analyst_upgrades": sent.analyst_upgrades if sent else 0,
            "analyst_downgrades": sent.analyst_downgrades if sent else 0,
            "price_target_avg": sent.price_target_avg if sent else 0.0,
            "price_target_high": sent.price_target_high if sent else 0.0,
            "price_target_low": sent.price_target_low if sent else 0.0,
            "earnings_beat_frequency": sent.earnings_beat_frequency if sent else 0.0,
            "ownership_institutional": sent.ownership_institutional if sent else 0.0,
            "ownership_retail": sent.ownership_retail if sent else 0.0,
            "short_interest_pct": sent.short_interest_pct if sent else 0.0,
            "options_call_put_ratio": sent.options_call_put_ratio if sent else 0.0,
            "insider_selling_trend": sent.insider_selling_trend if sent else {},
            "red_flags": sent.red_flags if sent else [],
            "educational_note": sent.educational_note if sent else ""
        },
        "valuation": {
            "fair_pe_base": val.fair_pe_base if val else 0.0,
            "fair_price_bull": val.fair_price_bull if val else 0.0,
            "fair_price_base": val.fair_price_base if val else 0.0,
            "fair_price_bear": val.fair_price_bear if val else 0.0,
            "downside_risk_pct": val.downside_risk_pct if val else 0.0,
            "growth_rate_bull": val.growth_rate_bull if val else 0.0,
            "growth_rate_base": val.growth_rate_base if val else 0.0,
            "growth_rate_bear": val.growth_rate_bear if val else 0.0,
            "monte_carlo_distribution": val.monte_carlo_distribution if val else {},
            "value_at_risk_95": val.value_at_risk_95 if val else 0.0,
            "stress_test_recession": val.stress_test_recession if val else {},
            "stress_test_competition": val.stress_test_competition if val else {},
            "stress_test_margin_pressure": val.stress_test_margin_pressure if val else {},
            "sensitivity_matrix": val.sensitivity_matrix if val else [],
            "breakeven_growth_years": val.breakeven_growth_years if val else {},
            "educational_note": val.educational_note if val else ""
        }
    }

@app.get("/api/companies")
def get_companies():
    db = SessionLocal()
    try:
        companies = db.query(HistoricalFinancials.company).all()
        return [get_unified_data(db, c_code) for (c_code,) in companies]
    finally:
        db.close()

@app.get("/api/companies/{company}")
def get_company(company: str):
    db = SessionLocal()
    try:
        return get_unified_data(db, company)
    finally:
        db.close()

@app.post("/api/recalculate")
def recalculate_peg(company: str = Body(..., embed=True), custom_growth: float = Body(..., embed=True)):
    if not isinstance(custom_growth, (int, float)) or math.isnan(custom_growth) or math.isinf(custom_growth):
        raise HTTPException(status_code=400, detail="Expected growth must be a valid finite number.")
    if custom_growth < 1.0 or custom_growth > 150.0:
        raise HTTPException(status_code=400, detail="Growth rate must be between 1.0% and 150.0%.")
    company = company.upper()
    db = SessionLocal()
    try:
        hist = db.query(HistoricalFinancials).filter(HistoricalFinancials.company == company).first()
        cap = db.query(CapacityAnalysis).filter(CapacityAnalysis.company == company).first()
        val = db.query(ValuationModels).filter(ValuationModels.company == company).first()
        if not hist or not val:
            raise HTTPException(status_code=404, detail="Company not found.")
        hist.current_peg = hist.current_pe / custom_growth
        hist.alert = "OVERVALUED" if hist.current_peg > 1.5 else "FAIR"
        eps = hist.current_price / hist.current_pe if hist.current_pe > 0 else 1.0
        net_margins = hist.net_margin_trend
        net_margin = (net_margins[-1] / 100.0) if net_margins else 0.10
        shares = SHARES_OUTSTANDING.get(company, 1.0)
        market_cap = hist.current_price * shares
        required_net_income = market_cap / custom_growth
        implied_rev_required = required_net_income / net_margin
        realistic_achievable_revenue = cap.realistic_achievable_revenue if cap else 10.0
        valuation_gap = implied_rev_required - realistic_achievable_revenue
        if cap:
            cap.implied_revenue_required = implied_rev_required
            cap.valuation_gap = valuation_gap
            cap.waterfall_data = {
                "Current Revenue": hist.revenue_5y[-1],
                "Target Revenue (justifying P/E)": implied_rev_required,
                "Realistic Maximum Revenue (2028)": realistic_achievable_revenue,
                "Valuation Gap": valuation_gap
            }
        val.fair_pe_base = custom_growth
        val.growth_rate_base = custom_growth
        val.growth_rate_bull = custom_growth * 1.35
        val.growth_rate_bear = custom_growth * 0.75
        val.fair_price_bull = eps * val.growth_rate_bull
        val.fair_price_base = eps * val.growth_rate_base
        val.fair_price_bear = eps * val.growth_rate_bear
        val.downside_risk_pct = 100.0 * (1.0 - val.fair_price_base / hist.current_price)
        val.sensitivity_matrix = []
        for g in [custom_growth * 0.5, custom_growth, custom_growth * 1.5]:
            val.sensitivity_matrix.append({"growth": round(g, 1), "peg_0_8": float(eps * g * 0.8), "peg_1_0": float(eps * g * 1.0), "peg_1_2": float(eps * g * 1.2)})
        expected_g = custom_growth / 100.0
        ratio = hist.current_pe / custom_growth
        years_needed = float(math.log(ratio) / math.log(1.0 + expected_g)) if ratio > 1.0 else 0.0
        val.breakeven_growth_years["years_needed"] = round(years_needed, 2)
        std_dev = 0.35 if company == "TSLA" else (0.40 if company == "NVDA" else 0.42)
        sample_paths, percentiles, var_95 = run_monte_carlo(hist.current_price, custom_growth, std_dev)
        val.monte_carlo_distribution = {"sample": sample_paths, "percentiles": percentiles}
        val.value_at_risk_95 = var_95
        db.commit()
        return get_unified_data(db, company)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/alerts")
def get_earnings_alerts():
    db = SessionLocal()
    try:
        alerts = db.query(EarningsAlert).order_by(EarningsAlert.timestamp.desc()).all()
        return [
            {"id": a.id, "company": a.company, "event_name": a.event_name, "timestamp": a.timestamp.isoformat(),
             "growth_rate_expected": a.growth_rate_expected, "growth_rate_actual": a.growth_rate_actual,
             "deviation_pct": a.deviation_pct, "action_taken": a.action_taken, "alert_message": a.alert_message, "is_active": a.is_active}
            for a in alerts
        ]
    finally:
        db.close()

@app.post("/api/trigger-earnings")
def trigger_mock_earnings(company: str = Body(..., embed=True)):
    company = company.upper()
    db = SessionLocal()
    try:
        hist = db.query(HistoricalFinancials).filter(HistoricalFinancials.company == company).first()
        cap = db.query(CapacityAnalysis).filter(CapacityAnalysis.company == company).first()
        val = db.query(ValuationModels).filter(ValuationModels.company == company).first()
        if not hist or not val:
            raise HTTPException(status_code=404, detail="Company not found.")
        expected_growth = 20.0 if company == "TSLA" else (25.0 if company == "NVDA" else 20.0)
        actual_growth = 14.0 if company == "TSLA" else (32.0 if company == "NVDA" else 17.0)
        deviation = ((actual_growth - expected_growth) / expected_growth) * 100.0
        hist.current_peg = hist.current_pe / actual_growth
        hist.alert = "OVERVALUED" if hist.current_peg > 1.5 else "FAIR"
        eps = hist.current_price / hist.current_pe if hist.current_pe > 0 else 1.0
        net_margins = hist.net_margin_trend
        net_margin = (net_margins[-1] / 100.0) if net_margins else 0.10
        shares = SHARES_OUTSTANDING.get(company, 1.0)
        market_cap = hist.current_price * shares
        required_net_income = market_cap / actual_growth
        implied_rev_required = required_net_income / net_margin
        realistic_achievable_revenue = cap.realistic_achievable_revenue if cap else 10.0
        valuation_gap = implied_rev_required - realistic_achievable_revenue
        if cap:
            cap.implied_revenue_required = implied_rev_required
            cap.valuation_gap = valuation_gap
        val.fair_pe_base = actual_growth
        val.growth_rate_base = actual_growth
        val.growth_rate_bull = actual_growth * 1.35
        val.growth_rate_bear = actual_growth * 0.75
        val.fair_price_bull = eps * val.growth_rate_bull
        val.fair_price_base = eps * val.growth_rate_base
        val.fair_price_bear = eps * val.growth_rate_bear
        val.downside_risk_pct = 100.0 * (1.0 - val.fair_price_base / hist.current_price)
        val.sensitivity_matrix = []
        for g in [actual_growth * 0.5, actual_growth, actual_growth * 1.5]:
            val.sensitivity_matrix.append({"growth": round(g, 1), "peg_0_8": float(eps * g * 0.8), "peg_1_0": float(eps * g * 1.0), "peg_1_2": float(eps * g * 1.2)})
        expected_g = actual_growth / 100.0
        ratio = hist.current_pe / actual_growth
        years_needed = float(math.log(ratio) / math.log(1.0 + expected_g)) if ratio > 1.0 else 0.0
        val.breakeven_growth_years = {"growth_needed": val.breakeven_growth_years.get("growth_needed", 25.0), "years_needed": round(years_needed, 2)}
        std_dev = 0.35 if company == "TSLA" else (0.40 if company == "NVDA" else 0.42)
        sample_paths, percentiles, var_95 = run_monte_carlo(hist.current_price, actual_growth, std_dev)
        val.monte_carlo_distribution = {"sample": sample_paths, "percentiles": percentiles}
        val.value_at_risk_95 = var_95
        if deviation < -10.0:
            alert_msg = f"Q2 growth missed by {abs(deviation):.1f}%! Expected {expected_growth:.1f}%, Actual {actual_growth:.1f}%. Fair target: ${val.fair_price_base:.2f}."
            action_taken = f"Downgraded multiple. Recalculated PEG bounds."
        elif deviation > 10.0:
            alert_msg = f"Q2 growth beat by {deviation:.1f}%! Expected {expected_growth:.1f}%, Actual {actual_growth:.1f}%. Fair target: ${val.fair_price_base:.2f}."
            action_taken = f"Upgraded multiple. Re-ran Monte Carlo."
        else:
            alert_msg = f"Q2 growth in-line. Expected {expected_growth:.1f}%, Actual {actual_growth:.1f}%."
            action_taken = f"No changes required."
        new_alert = EarningsAlert(company=company, event_name="Q2 Earnings Release",
            growth_rate_expected=expected_growth, growth_rate_actual=actual_growth,
            deviation_pct=deviation, action_taken=action_taken, alert_message=alert_msg, is_active=1)
        db.add(new_alert)
        db.commit()
        return {"company": get_unified_data(db, company), "new_alert": {"company": company, "alert_message": alert_msg, "action_taken": action_taken, "deviation_pct": deviation}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/statistical-foundation")
def get_statistical_foundation():
    db = SessionLocal()
    try:
        data = db.query(StatisticalFoundationData).all()
        return [
            {"company": d.company, "missing_values_pct": d.missing_values_pct, "outliers_detected": d.outliers_detected,
             "distribution_type": d.distribution_type, "is_stationary": d.is_stationary,
             "jarque_bera_p_value": d.jarque_bera_p_value, "mean": d.mean, "median": d.median,
             "std_dev": d.std_dev, "skewness": d.skewness, "kurtosis": d.kurtosis,
             "adf_statistic": d.adf_statistic, "adf_p_value": d.adf_p_value,
             "returns_distribution": d.returns_distribution, "qq_plot_data": d.qq_plot_data,
             "acf_data": d.acf_data, "outliers_data": d.outliers_data}
            for d in data
        ]
    finally:
        db.close()

@app.get("/api/correlation-analyzer")
def get_correlation_analyzer():
    db = SessionLocal()
    try:
        data = db.query(CorrelationRiskData).filter(CorrelationRiskData.id == "main").first()
        if not data:
            raise HTTPException(status_code=404, detail="Correlation data not found.")
        return {"correlation_matrix": data.correlation_matrix, "rolling_correlations": data.rolling_correlations,
                "betas": data.betas, "alphas": data.alphas,
                "commodity_correlations": data.commodity_correlations, "risk_warnings": data.risk_warnings}
    finally:
        db.close()

@app.get("/api/graph-network")
def get_graph_network():
    db = SessionLocal()
    try:
        data = db.query(GraphNetworkData).filter(GraphNetworkData.id == "main").first()
        if not data:
            raise HTTPException(status_code=404, detail="Graph data not found.")
        return {"nodes": data.nodes, "edges": data.edges, "centrality_metrics": data.centrality_metrics, "risk_paths": data.risk_paths}
    finally:
        db.close()

@app.get("/api/macro-indicators")
def get_macro_indicators():
    db = SessionLocal()
    try:
        data = db.query(MacroIndicatorsData).filter(MacroIndicatorsData.id == "main").first()
        if not data:
            raise HTTPException(status_code=404, detail="Macro data not found.")
        return {"historical_series": data.historical_series, "regime_analysis": data.regime_analysis,
                "macro_adjusted_valuations": data.macro_adjusted_valuations, "interest_rate_scenarios": data.interest_rate_scenarios}
    finally:
        db.close()

@app.get("/api/peer-comparison")
def get_peer_comparison():
    db = SessionLocal()
    try:
        data = db.query(PeerComparisonData).all()
        return [{"company": d.company, "peer_metrics": d.peer_metrics, "sotp_model": d.sotp_model, "scenario_weightings": d.scenario_weightings} for d in data]
    finally:
        db.close()

static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return {"status": "Dashboard static directory missing."}

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
