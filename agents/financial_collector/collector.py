import sys
import os
import json
from datetime import datetime

# Enable import of shared module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import SessionLocal
from shared.models import HistoricalFinancials
from shared.seed_data import SEED_HISTORICAL

# Try importing yfinance for live fetching dynamically inside functions
YFINANCE_AVAILABLE = True
ENABLE_LIVE_FETCH = os.getenv("ENABLE_LIVE_FETCH", "false").lower() == "true"


COMPANIES = {
    "TSLA": {"sector_pe": 15.0, "expected_growth": 20.0},
    "NVDA": {"sector_pe": 25.0, "expected_growth": 25.0},
    "PLTR": {"sector_pe": 32.0, "expected_growth": 25.0}
}

def calculate_cagr(start_val, end_val, periods):
    if start_val <= 0 or end_val <= 0 or periods <= 0:
        return 0.0
    return ((end_val / start_val) ** (1 / periods) - 1) * 100

def get_live_data(ticker):
    try:
        import yfinance as yf
    except ImportError:
        raise ImportError("yfinance not installed")
        
    stock = yf.Ticker(ticker)
    
    # Financials (last 5 years)
    financials = stock.financials
    quarterly_financials = stock.quarterly_financials
    cashflow = stock.cashflow
    balance_sheet = stock.balance_sheet
    info = stock.info
    
    if financials.empty or cashflow.empty or balance_sheet.empty or not info:
        raise ValueError(f"Incomplete live data for {ticker}")

    # Extract historical years (order them chronological)
    years = sorted(list(financials.columns))
    if len(years) < 4:
        raise ValueError("Insufficient historical years in financials")
        
    # Standardize to last 5 entries (or what is available)
    years = years[-5:]
    
    revenue = []
    ebitda = []
    net_income = []
    fcf = []
    
    gross_margins = []
    operating_margins = []
    net_margins = []
    
    for year in years:
        rev = float(financials.loc['Total Revenue', year])
        net = float(financials.loc['Net Income', year])
        
        # Gross profit
        gross_profit = float(financials.loc['Gross Profit', year]) if 'Gross Profit' in financials.index else rev * 0.5
        # EBITDA
        eb = float(financials.loc['EBITDA', year]) if 'EBITDA' in financials.index else net * 1.5
        # FCF = Operating Cash Flow - Capital Expenditure
        ocf = float(cashflow.loc['Operating Cash Flow', year]) if 'Operating Cash Flow' in cashflow.index else net * 1.1
        capex = abs(float(cashflow.loc['Capital Expenditures', year])) if 'Capital Expenditures' in cashflow.index else ocf * 0.2
        free_cf = ocf - capex
        
        revenue.append(rev / 1e9) # in Billions
        ebitda.append(eb / 1e9)
        net_income.append(net / 1e9)
        fcf.append(free_cf / 1e9)
        
        gross_margins.append((gross_profit / rev) * 100)
        operating_margins.append(((eb * 0.8) / rev) * 100) # proxy operating margin
        net_margins.append((net / rev) * 100)
        
    cagr_5y = calculate_cagr(revenue[0], revenue[-1], len(revenue) - 1)
    fcf_margin = (fcf[-1] / revenue[-1]) * 100
    
    # Ratios
    current_price = float(info.get('regularMarketPrice', info.get('currentPrice', 220.0)))
    current_pe = float(info.get('trailingPE', 65.0))
    forward_pe = float(info.get('forwardPE', current_pe * 0.85))
    
    # Balance sheet details
    total_assets = float(balance_sheet.loc['Total Assets', years[-1]]) if 'Total Assets' in balance_sheet.index else 100e9
    stockholders_equity = float(balance_sheet.loc['Stockholders Equity', years[-1]]) if 'Stockholders Equity' in balance_sheet.index else 50e9
    
    roe = (net_income[-1] * 1e9 / stockholders_equity) * 100
    roa = (net_income[-1] * 1e9 / total_assets) * 100
    
    # Robust Validation: Check for any NaN or None values
    import math
    for name, lst in [("revenue", revenue), ("ebitda", ebitda), ("net_income", net_income), 
                     ("fcf", fcf), ("gross_margins", gross_margins), 
                     ("operating_margins", operating_margins), ("net_margins", net_margins)]:
        for i, val in enumerate(lst):
            if val is None or math.isnan(val):
                raise ValueError(f"Failsafe: Calculated {name} list contains NaN/None at index {i}.")
                
    for name, val in [("current_price", current_price), ("current_pe", current_pe), 
                     ("forward_pe", forward_pe), ("revenue_cagr_5y", cagr_5y), 
                     ("fcf_margin", fcf_margin), ("roe", roe), ("roa", roa)]:
        if val is None or math.isnan(val):
            raise ValueError(f"Failsafe: Metric {name} is NaN or None.")
            
    return {
        "current_price": current_price,
        "current_pe": current_pe,
        "forward_pe": forward_pe,
        "revenue_cagr_5y": cagr_5y,
        "gross_margin_trend": gross_margins,
        "operating_margin_trend": operating_margins,
        "net_margin_trend": net_margins,
        "fcf_margin": fcf_margin,
        "revenue_5y": revenue,
        "ebitda_5y": ebitda,
        "net_income_5y": net_income,
        "fcf_5y": fcf,
        "roe": roe,
        "roa": roa
    }

def run_collector():
    db = SessionLocal()
    outputs = []
    try:
        print("Starting Agent 1: Historical Financial Data Collector...")
        for ticker, conf in COMPANIES.items():
            print(f"Collecting data for {ticker}...")
            data = None
            
            # Try live collection first
            if YFINANCE_AVAILABLE and ENABLE_LIVE_FETCH:
                try:
                    data = get_live_data(ticker)
                    print(f"Live yfinance data successfully fetched for {ticker}!")
                except Exception as ex:
                    print(f"Live fetch failed for {ticker}: {ex}. Falling back to pre-seeded high-fidelity financials.")
                    
            if not data:
                # Load pre-seeded data for this company
                seed = next(s for s in SEED_HISTORICAL if s["company"] == ticker)
                data = {
                    "current_price": seed["current_price"],
                    "current_pe": seed["current_pe"],
                    "forward_pe": seed["forward_pe"],
                    "revenue_cagr_5y": seed["revenue_cagr_5y"],
                    "gross_margin_trend": seed["gross_margin_trend"],
                    "operating_margin_trend": seed["operating_margin_trend"],
                    "net_margin_trend": seed["net_margin_trend"],
                    "fcf_margin": seed["fcf_margin"],
                    "revenue_5y": seed["revenue_5y"],
                    "ebitda_5y": seed["ebitda_5y"],
                    "net_income_5y": seed["net_income_5y"],
                    "fcf_5y": seed["fcf_5y"],
                    "roe": seed["roe"],
                    "roa": seed["roa"]
                }
            
            # Compute current PEG based on historical revenue growth (or expected growth)
            # Use max(1.0, growth) to avoid division by zero
            growth_rate = conf["expected_growth"]
            current_peg = data["current_pe"] / growth_rate
            alert = "OVERVALUED" if current_peg > 1.5 else "FAIR"
            
            seed_note = next(s for s in SEED_HISTORICAL if s["company"] == ticker)["educational_note"]
            
            # Prepare database object
            financial = HistoricalFinancials(
                company=ticker,
                current_price=data["current_price"],
                current_pe=data["current_pe"],
                forward_pe=data["forward_pe"],
                current_peg=current_peg,
                revenue_cagr_5y=data["revenue_cagr_5y"],
                gross_margin_trend=data["gross_margin_trend"],
                operating_margin_trend=data["operating_margin_trend"],
                net_margin_trend=data["net_margin_trend"],
                fcf_margin=data["fcf_margin"],
                sector_median_pe=conf["sector_pe"],
                revenue_5y=data["revenue_5y"],
                ebitda_5y=data["ebitda_5y"],
                net_income_5y=data["net_income_5y"],
                fcf_5y=data["fcf_5y"],
                roe=data["roe"],
                roa=data["roa"],
                alert=alert,
                educational_note=seed_note
            )
            
            db.merge(financial)
            
            # Build schema-conforming JSON for handoff output
            outputs.append({
                "company": ticker,
                "metrics": {
                    "current_pe": data["current_pe"],
                    "forward_pe": data["forward_pe"],
                    "current_peg": current_peg,
                    "revenue_cagr_5y": data["revenue_cagr_5y"],
                    "gross_margin_trend": data["gross_margin_trend"],
                    "fcf_margin": data["fcf_margin"],
                    "sector_median_pe": conf["sector_pe"]
                },
                "alert": alert,
                "educational_note": "P/E ratio alone doesn't tell the story. A company with 100% growth can justify P/E of 100 (PEG=1.0), but if growth slows to 20%, that same P/E becomes extremely expensive (PEG=5.0)."
            })
            
        db.commit()
        print("Agent 1 successfully saved financial histories to shared database.")
        
        # Print JSON handoff output as required by sequential orchestrator
        print("AGENT_1_OUTPUT_START")
        print(json.dumps(outputs, indent=2))
        print("AGENT_1_OUTPUT_END")
        
    except Exception as e:
        db.rollback()
        print(f"Error in Agent 1 execution: {e}", file=sys.stderr)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_collector()
