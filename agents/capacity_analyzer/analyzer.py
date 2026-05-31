import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import SessionLocal
from shared.models import HistoricalFinancials, CapacityAnalysis
from shared.seed_data import SEED_CAPACITY

SHARES_OUTSTANDING = {
    "TSLA": 3.18, # Billions
    "NVDA": 2.30, # Billions
    "PLTR": 2.29  # Billions
}

TARGET_PE = {
    "TSLA": 20.0, # Fair value P/E matching expected 20% growth
    "NVDA": 25.0, # Fair value P/E matching expected 25% growth
    "PLTR": 20.0  # Fair value P/E matching expected 20% growth
}

def run_analyzer():
    db = SessionLocal()
    outputs = []
    try:
        print("Starting Agent 2: Forward-Looking Capacity & Order Book Analyzer...")
        
        # Read historical financials from DB
        financials = {f.company: f for f in db.query(HistoricalFinancials).all()}
        
        if not financials:
            print("Warning: HistoricalFinancials table is empty! Ensure Agent 1 runs first. Using fallback data.")
            
        for ticker, seed in [(s["company"], s) for s in SEED_CAPACITY]:
            print(f"Analyzing capacity limits for {ticker}...")
            
            # Fetch price and margins from Agent 1 database entries
            if ticker in financials:
                f_record = financials[ticker]
                current_price = f_record.current_price
                # Use current net margin (last value in margin trend or fcf_margin, let's use net_margin_trend[-1])
                net_margins = f_record.net_margin_trend
                net_margin = net_margins[-1] / 100.0 if net_margins else 0.10
                current_revenue = f_record.revenue_5y[-1]
            else:
                # Fallback to seed values
                current_price = seed["waterfall_data"]["Current Revenue"] * 2.0  # proxy
                net_margin = 0.10
                current_revenue = seed["waterfall_data"]["Current Revenue"]
                
            shares = SHARES_OUTSTANDING[ticker]
            market_cap = current_price * shares
            target_pe = TARGET_PE[ticker]
            
            # Mathematical modeling: Required Revenue to justify today's valuation at Target P/E
            # Required Net Income = Market Cap / Target P/E
            # Required Revenue = Required Net Income / Net Margin
            required_net_income = market_cap / target_pe
            implied_rev_required = required_net_income / net_margin
            
            # Realistic revenue from operational capacity (gigafactory output or GPU packaging caps)
            realistic_achievable_revenue = seed["realistic_achievable_revenue"]
            valuation_gap = implied_rev_required - realistic_achievable_revenue
            
            # Structure waterfall chart data
            waterfall_data = {
                "Current Revenue": current_revenue,
                "Target Revenue (justifying P/E)": implied_rev_required,
                "Realistic Maximum Revenue (2028)": realistic_achievable_revenue,
                "Valuation Gap": valuation_gap
            }
            
            analysis = CapacityAnalysis(
                company=ticker,
                production_capacity=seed["production_capacity"],
                backlog_trends=seed["backlog_trends"],
                implied_revenue_required=implied_rev_required,
                realistic_achievable_revenue=realistic_achievable_revenue,
                valuation_gap=valuation_gap,
                waterfall_data=waterfall_data,
                educational_note=seed["educational_note"]
            )
            
            db.merge(analysis)
            
            outputs.append({
                "company": ticker,
                "capacity_analysis": {
                    "production_capacity": seed["production_capacity"],
                    "implied_revenue_required_by_2028": implied_rev_required,
                    "realistic_achievable_revenue": realistic_achievable_revenue,
                    "valuation_gap": valuation_gap
                },
                "waterfall_chart": waterfall_data,
                "educational_visualization_note": "Waterfall chart showing: Current Revenue -> Required Revenue (to justify P/E) -> Realistic Revenue (based on capacity) -> VALUATION GAP"
            })
            
        db.commit()
        print("Agent 2 successfully wrote capacity analytics to shared database.")
        
        print("AGENT_2_OUTPUT_START")
        print(json.dumps(outputs, indent=2))
        print("AGENT_2_OUTPUT_END")
        
    except Exception as e:
        db.rollback()
        print(f"Error in Agent 2 execution: {e}", file=sys.stderr)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_analyzer()
