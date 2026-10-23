import json
import os
import datetime
import yfinance as yf
import requests

def get_market_data():
    data = {
        "last_updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "oil": 82.0,
        "usdjpy": 148.5,
        "yield_spread": 18.0,
        "cds_oas": 360.0,
        "shiller_cape": 37.4,
        "buffett_ind": 198.0,
        "top10_weight": 35.8
    }

    # 1. Fetch live market tickers via yfinance
    try:
        tickers = yf.Tickers("BZ=F CL=F JPY=X ^TNX ^IRX")
        
        # Brent Crude or WTI Crude
        oil_price = tickers.tickers["BZ=F"].history(period="5d")["Close"].dropna()
        if not oil_price.empty:
            data["oil"] = round(float(oil_price.iloc[-1]), 2)

        # USD / JPY
        jpy_rate = tickers.tickers["JPY=X"].history(period="5d")["Close"].dropna()
        if not jpy_rate.empty:
            data["usdjpy"] = round(float(jpy_rate.iloc[-1]), 2)

        # 10Y Yield (^TNX) minus 13-Week / 2Y proxy (basis points)
        tnx = tickers.tickers["^TNX"].history(period="5d")["Close"].dropna()
        irx = tickers.tickers["^IRX"].history(period="5d")["Close"].dropna()
        if not tnx.empty and not irx.empty:
            spread = (float(tnx.iloc[-1]) - float(irx.iloc[-1])) * 100
            data["yield_spread"] = round(spread, 1)
    except Exception as e:
        print(f"Error fetching yfinance: {e}")

    # 2. Fetch St. Louis Fed FRED data (Free Open Series)
    try:
        # High Yield OAS (BAMLH0A0HYM2) & 10Y-2Y Spread (T10Y2Y)
        fred_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLH0A0HYM2"
        res = requests.get(fred_url, timeout=10)
        if res.status_code == 200:
            lines = [line.strip() for line in res.text.split("\n") if line.strip() and not line.startswith("DATE")]
            last_val = lines[-1].split(",")[-1]
            if last_val != ".":
                data["cds_oas"] = round(float(last_val) * 100, 0)
    except Exception as e:
        print(f"Error fetching FRED: {e}")

    # Save to data.json
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Updated data.json successfully:", data)

if __name__ == "__main__":
    get_market_data()
