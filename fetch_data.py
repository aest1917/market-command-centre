import yfinance as yf
import pandas as pd
import numpy as np
import json, sys
from datetime import datetime, timezone, timedelta

# ── HELPERS ───────────────────────────────────────────────────────────────────

def pct(cur, past):
    if past and past != 0:
        return round((cur - past) / abs(past) * 100, 2)
    return None

def fmt_pct(v):
    if v is None: return "—"
    return f"+{v:.2f}%" if v >= 0 else f"{v:.2f}%"

def fmt_price(v):
    if v is None: return "—"
    if v >= 10000: return f"{v:,.0f}"
    if v >= 1000:  return f"{v:,.2f}"
    if v >= 100:   return f"{v:.2f}"
    return f"{v:.3f}" if v < 1 else f"{v:.2f}"

def ema(s, p): return s.ewm(span=p, adjust=False).mean()
def sma(s, p): return s.rolling(window=p).mean()

def fetch(sym, period="1y"):
    try:
        h = yf.Ticker(sym).history(period=period)
        return None if h.empty or len(h) < 5 else h
    except Exception as e:
        print(f"  ERR {sym}: {e}", file=sys.stderr)
        return None

def perf(hist):
    if hist is None or hist.empty:
        return dict(price="—", d1="—", w1="—", m1="—", w52="—", ytd="—", d1_val=None, w1_val=None, trend=[])
    c = hist["Close"]
    p = c.iloc[-1]
    d1  = pct(p, c.iloc[-2])  if len(c) >= 2  else None
    w1  = pct(p, c.iloc[-6])  if len(c) >= 6  else None
    m1  = pct(p, c.iloc[-22]) if len(c) >= 22 else None
    w52 = pct(p, c.iloc[0])   if len(c) >= 50 else None
    now = pd.Timestamp.now(tz="UTC")
    ystart = pd.Timestamp(now.year, 1, 1, tz="UTC")
    yh = hist[hist.index >= ystart]
    ytd = pct(p, yh["Close"].iloc[0]) if not yh.empty else None
    trend = [round(pct(c.iloc[i], c.iloc[i-1]) or 0, 2) for i in range(-5, 0) if len(c) >= abs(i)]
    return dict(price=fmt_price(p), d1=fmt_pct(d1), w1=fmt_pct(w1), m1=fmt_pct(m1),
                w52=fmt_pct(w52), ytd=fmt_pct(ytd), d1_val=d1, w1_val=w1, trend=trend)

def pulse(sym):
    hist = fetch(sym)
    if hist is None:
        return dict(symbol=sym, price="—", d1="—", w1="—", m1="—", w52="—", ytd="—",
                    ema10=False, ema21=False, sma50=False, sma200=False)
    p = perf(hist)
    c = hist["Close"]
    pv = c.iloc[-1]
    return dict(symbol=sym, **p,
                ema10 =pv > ema(c,10).iloc[-1],
                ema21 =pv > ema(c,21).iloc[-1],
                sma50 =pv > sma(c,50).iloc[-1],
                sma200=pv > sma(c,200).iloc[-1] if len(c)>=200 else False)

def grp(tickers):
    out = []
    for sym, code, label in tickers:
        print(f"  {sym}", file=sys.stderr)
        h = fetch(sym)
        p = perf(h)
        out.append(dict(ticker=sym, code=code, label=label, **p))
    return out

def grp_sorted(tickers):
    rows = grp(tickers)
    rows.sort(key=lambda x: x.get("w1_val") or -999, reverse=True)
    return rows

# ── TICKER LISTS ──────────────────────────────────────────────────────────────

PULSE         = ["SPY", "QQQ"]

FUTURES       = [("ES=F","ES","S&P 500"),("NQ=F","NQ","Nasdaq"),
                 ("YM=F","YM","Dow"),("RTY=F","RTY","Russell 2000")]

VIX_DXY       = [("^VIX","VIX","Volatility Index"),("DX-Y.NYB","DXY","US Dollar Index")]

CRYPTO        = [("BTC-USD","BTC","Bitcoin"),("ETH-USD","ETH","Ethereum")]

METALS        = [("GC=F","GC","Gold"),("SI=F","SI","Silver"),("HG=F","HG","Copper")]

ENERGY        = [("CL=F","WTI","Crude Oil WTI"),("BZ=F","BRN","Brent Crude"),
                 ("NG=F","NG","Natural Gas")]

YIELDS        = [("^IRX","13W","13-Week"),("^FVX","5Y","5-Year"),
                 ("^TNX","10Y","10-Year"),("^TYX","30Y","30-Year")]

GLOBAL        = [("^N225","NKY","Nikkei 225"),("^HSI","HSI","Hang Seng"),
                 ("^GDAXI","DAX","Germany DAX"),("^FTSE","UKX","FTSE 100"),
                 ("^AXJO","AS51","ASX 200"),("^KS11","KOSPI","South Korea")]

# Clement's Major ETF Stats
MAJOR_ETF     = [("SPY","SPY","S&P 500"),("QQQ","QQQ","Nasdaq 100"),
                 ("IWM","IWM","Russell 2000"),("DIA","DIA","Dow Jones"),
                 ("RSP","RSP","S&P 500 Equal Weight"),("MDY","MDY","S&P 400 Mid-Cap"),
                 ("IJR","IJR","S&P 600 Small-Cap"),("VTI","VTI","Total US Market"),
                 ("EFA","EFA","Intl Developed"),("EEM","EEM","Emerging Markets"),
                 ("HYG","HYG","High Yield Bonds"),("TLT","TLT","20Y+ Treasury"),
                 ("GLD","GLD","Gold"),("USO","USO","Oil")]

# S&P 500 Sub-Market — broad market segments
SUBMARKET     = [("XLK","XLK","Technology"),("XLF","XLF","Financials"),
                 ("XLV","XLV","Health Care"),("XLE","XLE","Energy"),
                 ("XLI","XLI","Industrials"),("XLY","XLY","Cons. Discretionary"),
                 ("XLP","XLP","Cons. Staples"),("XLU","XLU","Utilities"),
                 ("XLB","XLB","Materials"),("XLRE","XLRE","Real Estate"),
                 ("XLC","XLC","Comm. Services"),
                 ("IVW","IVW","S&P 500 Growth"),("IVE","IVE","S&P 500 Value"),
                 ("IJH","IJH","S&P 400 Mid-Cap"),("VBR","VBR","Small-Cap Value"),
                 ("VUG","VUG","Large-Cap Growth")]

# Cap-weighted S&P 500 sectors
SP_SECTORS    = [("XLE","XLE","Energy"),("XLU","XLU","Utilities"),
                 ("XLB","XLB","Materials"),("XLP","XLP","Cons. Staples"),
                 ("XLI","XLI","Industrials"),("XLRE","XLRE","Real Estate"),
                 ("XLF","XLF","Financials"),("XLV","XLV","Health Care"),
                 ("XLC","XLC","Comm. Services"),("XLY","XLY","Cons. Discret."),
                 ("XLK","XLK","Technology")]

# Equal-weight S&P 500 sectors (Invesco RYxx series)
EW_SECTORS    = [("RYE","RYE","Energy EW"),("RYU","RYU","Utilities EW"),
                 ("RTM","RTM","Materials EW"),("RHS","RHS","Cons. Staples EW"),
                 ("RGI","RGI","Industrials EW"),("KBWR","KBWR","Financials EW"),
                 ("RYH","RYH","Health Care EW"),("EWCO","EWCO","Comm. Services EW"),
                 ("RCD","RCD","Cons. Discret. EW"),("RYT","RYT","Technology EW"),
                 ("EWRE","EWRE","Real Estate EW")]

# Your personal thematic watchlist
THEMATIC      = [("MNRS","MNRS","Gold Miners"),("ARKX","ARKX","ARK Space"),
                 ("UFO","UFO","Space ETF"),("QTUM","QTUM","Quantum"),
                 ("TAN","TAN","Solar"),("ICLN","ICLN","Clean Energy"),
                 ("HACK","HACK","Cybersecurity"),("ARKQ","ARKQ","ARK Robotics"),
                 ("IGV","IGV","Software"),("BOTZ","BOTZ","Robotics/AI"),
                 ("ARKK","ARKK","ARK Innovation"),("SOXX","SOXX","Semis iShares"),
                 ("SMH","SMH","Semis")]

# Breadth ETFs — MA trackers (TradingView MMTW equivalent proxies)
BREADTH_ETFS  = [("RSP","RSP","Equal Weight S&P vs SPY breadth"),
                 ("QQEW","QQEW","Equal Weight Nasdaq"),
                 ("IWO","IWO","Russell 2000 Growth"),
                 ("IWN","IWN","Russell 2000 Value"),
                 ("SPHB","SPHB","S&P 500 High Beta"),
                 ("SPLV","SPLV","S&P 500 Low Volatility")]

# ── BREADTH CALCULATION ───────────────────────────────────────────────────────
# Approximate % above MA using SPY/QQQ breadth proxies
# Real MMTW requires tick-level data; we compute from our sector ETFs as proxy

def calc_breadth(sp_sector_hists):
    """Use the 11 sector ETFs as a simple proxy breadth read"""
    above_20, above_50, above_200 = [], [], []
    for h in sp_sector_hists:
        if h is None or h.empty: continue
        c = h["Close"]
        pv = c.iloc[-1]
        if len(c) >= 20:  above_20.append(1  if pv > sma(c,20).iloc[-1]  else 0)
        if len(c) >= 50:  above_50.append(1  if pv > sma(c,50).iloc[-1]  else 0)
        if len(c) >= 200: above_200.append(1 if pv > sma(c,200).iloc[-1] else 0)
    def pct_str(lst): return str(round(sum(lst)/len(lst)*100)) if lst else None
    return dict(pct_above_20ma=pct_str(above_20),
                pct_above_50ma=pct_str(above_50),
                pct_above_200ma=pct_str(above_200),
                new_highs="—", new_lows="—",  # requires tick data
                vix_price=None)

# ── MAIN FETCH ────────────────────────────────────────────────────────────────

print("Pulse...", file=sys.stderr)
pulse_data = [pulse(s) for s in PULSE]

print("Futures...", file=sys.stderr);   futures_data  = grp(FUTURES)
print("VIX/DXY...", file=sys.stderr);   vix_data      = grp(VIX_DXY)
print("Crypto...", file=sys.stderr);    crypto_data   = grp(CRYPTO)
print("Metals...", file=sys.stderr);    metals_data   = grp(METALS)
print("Energy...", file=sys.stderr);    energy_data   = grp(ENERGY)
print("Yields...", file=sys.stderr);    yields_data   = grp(YIELDS)
print("Global...", file=sys.stderr);    global_data   = grp(GLOBAL)
print("Major ETF...", file=sys.stderr); major_etf     = grp(MAJOR_ETF)
print("Sub-Market...", file=sys.stderr);submarket     = grp_sorted(SUBMARKET)
print("SP Sectors...", file=sys.stderr);sp_sectors    = grp_sorted(SP_SECTORS)
print("EW Sectors...", file=sys.stderr);ew_sectors    = grp_sorted(EW_SECTORS)
print("Thematic...", file=sys.stderr);  thematic      = grp_sorted(THEMATIC)
print("Breadth ETFs...",file=sys.stderr);breadth_etfs = grp(BREADTH_ETFS)

# Breadth calculation using sector hists
sector_hists = [fetch(t[0]) for t in SP_SECTORS]
breadth = calc_breadth(sector_hists)

# Pull VIX price into breadth
vix_row = next((r for r in vix_data if r["code"]=="VIX"), None)
if vix_row: breadth["vix_price"] = vix_row["price"]

# ── TIMESTAMP ─────────────────────────────────────────────────────────────────
now_utc = datetime.now(timezone.utc)
now_pht = now_utc + timedelta(hours=8)
refresh_utc = now_utc.strftime("%d %b %Y %H:%M UTC")
refresh_pht = now_pht.strftime("%d %b %Y %H:%M PHT")

# ── OUTPUT ────────────────────────────────────────────────────────────────────
data = dict(
    refresh_utc=refresh_utc, refresh_pht=refresh_pht,
    pulse=pulse_data, futures=futures_data, vix_dxy=vix_data,
    crypto=crypto_data, metals=metals_data, energy=energy_data,
    yields=yields_data, global_idx=global_data,
    major_etf=major_etf, submarket=submarket,
    sp_sectors=sp_sectors, ew_sectors=ew_sectors,
    thematic=thematic, breadth=breadth, breadth_etfs=breadth_etfs
)

class SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        import numpy as np
        if isinstance(obj, (np.bool_)): return bool(obj)
        if isinstance(obj, (np.integer)): return int(obj)
        if isinstance(obj, (np.floating)): return float(obj)
        if isinstance(obj, (np.ndarray,)): return obj.tolist()
        return super().default(obj)

with open("data.json","w") as f:
    json.dump(data, f, indent=2, cls=SafeEncoder)

print(f"Done — {refresh_pht}", file=sys.stderr)
print("OK")
