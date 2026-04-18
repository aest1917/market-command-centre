# Market Command Centre
Bloomberg-style trading dashboard. Auto-refreshes daily via GitHub Actions + Yahoo Finance.
Built for swing traders — PHT timezone, EOD data.

## Files
- `index.html` — the dashboard (open this in browser)
- `fetch_data.py` — Python script that pulls all market data
- `data.json` — generated data file (auto-updated by GitHub Actions)
- `.github/workflows/update.yml` — auto-refresh schedule

## Setup (5 minutes)

### Step 1 — Create GitHub repo
- Go to github.com → click + → New repository
- Name: `market-command-centre`
- Visibility: **Public**
- Do NOT tick "Add README" or any initialize options
- Click Create repository

### Step 2 — Upload files
On the empty repo page, click **uploading an existing file**
Upload these 3 files:
- `index.html`
- `fetch_data.py`
- `data.json`
Click **Commit changes**

### Step 3 — Create the workflow file
- Click **Add file** → **Create new file**
- In the filename box type exactly: `.github/workflows/update.yml`
- Open your local `update.yml` in Notepad, copy all, paste into the editor
- Click **Commit changes**

### Step 4 — Enable GitHub Pages
- Repo → **Settings** → **Pages** (left sidebar)
- Source: **Deploy from a branch**
- Branch: **main** · Folder: **/ (root)**
- Click **Save**
- Wait 1-2 minutes

### Step 5 — Run first data fetch
- Repo → **Actions** tab
- Click **Update Market Data** → **Run workflow** → **Run workflow**
- Wait ~60 seconds for green checkmark
- Real data is now in your repo

### Step 6 — Open your dashboard
```
https://aestinar.github.io/market-command-centre/
```

## Auto-refresh
Runs automatically at **06:00 PHT (22:00 UTC) Monday–Friday**
You can also trigger manually via Actions → Run workflow anytime.

## Sections
- **00** Header — PHT live clock, market status, BLK/NVY theme toggle
- **01** Index Pulse — SPY + QQQ with 1D/1W/1M/52W/YTD + EMA/SMA indicators
- **02** Macro — Futures, VIX/DXY, Crypto, Metals, Energy, Yields, Global Indices
- **03** Equities — Major ETFs, Sub-Market, Sub-Sector, EW Sub-Sector, Top 10 Thematic
- **04** Breadth — % above 20/50/200MA, New Highs/Lows, VIX level
- **05** NYSE Calendar — Next holiday countdown + full 2026 schedule

## To add tickers
Edit `fetch_data.py` — find the list you want (e.g. `THEMATIC`) and add your ticker:
```python
("TICKER", "TICKER", "Description"),
```
