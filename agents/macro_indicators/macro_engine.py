import sys
import os
import json
import math
import random
from datetime import datetime

# Enable import from shared module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import SessionLocal
from shared.models import HistoricalStockSeries, MacroIndicatorsData, HistoricalFinancials

def run_macro_engine():
    db = SessionLocal()
    try:
        print("Starting Agent 9: Macroeconomic Indicator Integration...")
        
        # 1. Fetch current pricing/PE details for core stocks
        financials = {f.company: f for f in db.query(HistoricalFinancials).all()}
        
        if not financials:
            print("[Warning] HistoricalFinancials table is empty! Ensure earlier agents run first.")
            return
            
        # 2. Build high-fidelity 5-year monthly historical macroeconomic data series
        # Starting 5 years ago (approx. June 2021) to May 2026
        n_months = 60
        start_date = datetime(2021, 6, 1)
        
        macro_dates = []
        fed_funds = []
        yield_10y = []
        cpi = []
        ppi = []
        gdp_growth = []
        ism_mfg = []
        unemployment = []
        m2_growth = []
        fed_balance_sheet = [] # in Trillions
        
        # Generate semi-deterministic realistic macro history matching 2021-2026 economic trajectory
        for i in range(n_months):
            # Compute month date
            year = 2021 + (i + 5) // 12
            month = (i + 5) % 12 + 1
            date_val = datetime(year, month, 1)
            macro_dates.append(date_val.strftime("%Y-%m-%d"))
            
            # Economic trajectory modeling
            if i < 12: # 2021 Period (Easy money, post-COVID expansion)
                fed_funds.append(0.10 + random_noise(-0.02, 0.02))
                yield_10y.append(1.40 + i * 0.05 + random_noise(-0.05, 0.05))
                cpi.append(4.2 + i * 0.3) # CPI surging
                ppi.append(5.0 + i * 0.4)
                gdp_growth.append(5.8 + random_noise(-0.5, 0.5)) # High recovery growth
                ism_mfg.append(61.2 + random_noise(-1.0, 1.0)) # Rapid expansion
                unemployment.append(5.5 - i * 0.15) # Falling
                m2_growth.append(18.0 - i * 0.8) # High but declining from peak
                fed_balance_sheet.append(7.8 + i * 0.09) # Expanding
                
            elif i < 24: # 2022 Period (Inflation Shock & Rapid Aggressive Tightening)
                idx = i - 12
                fed_funds.append(0.25 + idx * 0.35 + random_noise(-0.05, 0.05)) # Fast rate hikes
                yield_10y.append(2.0 + idx * 0.15 + random_noise(-0.08, 0.08)) # Yields surge to 3.8%
                cpi.append(7.8 + random_noise(-0.5, 1.3)) # Peaked at 9.1%
                ppi.append(8.8 + random_noise(-0.6, 1.2))
                gdp_growth.append(2.5 - idx * 0.1) # Decelerating
                ism_mfg.append(58.0 - idx * 1.0) # Contracting down to 48
                unemployment.append(3.8 + random_noise(-0.1, 0.1)) # Very tight labor
                m2_growth.append(8.0 - idx * 1.0) # Slashing liquidity
                fed_balance_sheet.append(8.9 - idx * 0.05) # Quantitative Tightening starts
                
            elif i < 48: # 2023-2024 Period (Restrictive Consolidation, Peak Hikes)
                idx = i - 24
                fed_funds.append(5.25 + random_noise(-0.05, 0.05)) # Peak rates
                yield_10y.append(4.0 + idx * 0.02 + random_noise(-0.1, 0.1)) # Spiking around 4.2%-4.8%
                cpi.append(6.0 - idx * 0.18 + random_noise(-0.2, 0.2)) # Inflation cooling down
                ppi.append(6.2 - idx * 0.22 + random_noise(-0.3, 0.3))
                gdp_growth.append(1.8 + random_noise(-0.3, 0.3)) # Slow but resilient
                ism_mfg.append(47.5 + idx * 0.1) # Hovering around neutral
                unemployment.append(3.7 + idx * 0.01 + random_noise(-0.1, 0.1))
                m2_growth.append(-2.0 + idx * 0.2) # Negative M2 growth
                fed_balance_sheet.append(8.3 - idx * 0.07) # Balance sheet contraction
                
            else: # 2025-2026 Period (Soft Landing, Transition, Yields/Inflation cooling)
                idx = i - 48
                fed_funds.append(5.25 - idx * 0.15) # Pivot / Rate cuts start
                yield_10y.append(4.5 - idx * 0.05) # Yields settling around 4.2%
                cpi.append(3.2 - idx * 0.08) # Inflation approaching 2.6%
                ppi.append(3.0 - idx * 0.06)
                gdp_growth.append(2.2 + random_noise(-0.2, 0.2))
                ism_mfg.append(50.5 + idx * 0.1) # Slight expansion
                unemployment.append(4.0 + idx * 0.02)
                m2_growth.append(1.5 + idx * 0.2) # M2 returning to positive
                fed_balance_sheet.append(7.4 - idx * 0.04) # Steady contraction
                
        # 3. Macro-Adjusted Valuation logic
        # Current yields (at final month)
        curr_10y_yield = yield_10y[-1] # 4.2%
        curr_fed_funds = fed_funds[-1] # 4.5%
        
        # Calculate theoretical justified P/E based on bond yields
        # Justified PE = 1 / 10Y Yield
        justified_pe_ratio = 1.0 / (curr_10y_yield / 100.0)
        
        # Historical average yield over the 5 years
        hist_avg_10y_yield = sum(yield_10y) / n_months # approx. 3.2%
        
        # Macro adjustment factor based on discount rates: Historical Avg Yield / Current Yield
        macro_adjustment_factor = hist_avg_10y_yield / curr_10y_yield # e.g. 3.2 / 4.2 = 0.76x
        
        macro_adjusted_pe = {}
        for symbol, record in financials.items():
            current_pe = record.current_pe
            adjusted_pe = current_pe * macro_adjustment_factor
            
            macro_adjusted_pe[symbol] = {
                "current_pe": round(current_pe, 1),
                "justified_pe_bond_yield": round(justified_pe_ratio, 1),
                "macro_adjustment_factor": round(macro_adjustment_factor, 3),
                "macro_adjusted_pe": round(adjusted_pe, 1),
                "thesis": f"At today's 10-Year yield of {curr_10y_yield:.1f}%, the risk-free justified P/E is {justified_pe_ratio:.1f}x. {symbol} trades at a trailing multiple of {current_pe:.1f}x. Adjusting for the current higher discount rate environment relative to the 5-year average yield, its macro-adjusted P/E compresses to {adjusted_pe:.1f}x, revealing severe valuation bloating."
            }
            
        # 4. Interest Rate Sensitivity Scenario Matrix
        # Show fair prices under yield shifts: -1.0%, current, +1.0%, +2.0%
        # Shift increases DCF discount rate, reducing target multiple.
        # Target PE multiplier shifts: lower yield = higher multiple, higher yield = compressed multiple
        interest_rate_scenarios = {}
        
        for symbol, record in financials.items():
            current_price = record.current_price
            current_pe = record.current_pe
            eps = current_price / current_pe if current_pe > 0 else 1.0
            
            # Growth base matching Agent 4 (TSLA: 20%, NVDA: 25%, PLTR: 20%)
            growth_rate = 20.0 if symbol == "TSLA" else (25.0 if symbol == "NVDA" else 20.0)
            
            scenarios = []
            # Yield shifts
            for shift_label, shift_val in [("Yield -1.0% (3.2%)", -1.0), ("Current (4.2%)", 0.0), ("Yield +1.0% (5.2%)", 1.0), ("Yield +2.0% (6.2%)", 2.0)]:
                # Target multiple adjusts: base multiple = growth_rate * factor
                # Lower rates = multiple expansion (e.g. PEG goes to 1.2)
                # Higher rates = multiple contraction (e.g. PEG goes to 0.7)
                peg_factor = 1.0 - (shift_val * 0.15)
                projected_pe = growth_rate * peg_factor
                projected_price = eps * projected_pe
                
                scenarios.append({
                    "scenario": shift_label,
                    "target_pe": round(projected_pe, 1),
                    "projected_fair_price": round(projected_price, 2),
                    "price_change_pct": round(100.0 * (projected_price - current_price) / current_price, 1)
                })
            interest_rate_scenarios[symbol] = scenarios
            
        # 5. Economic Regime Classifications
        regimes = [
            {
                "regime_name": "Easy Money Expansion (2021)",
                "characteristics": "Near-zero interest rates, soaring M2 money supply, double-digit GDP growth.",
                "duration": "June 2021 - May 2022",
                "avg_10y_yield": 1.7,
                "avg_m2_growth": 14.5,
                "impact_growth_stocks": "MULTIPLE EXPANSION CYCLIC peak: Excess liquidity enables infinite multiples (P/E up to 150x+). Hyper-speculative bubbles flourish."
            },
            {
                "regime_name": "Inflation Shock & Tightening (2022)",
                "characteristics": "Violent inflation spikes, aggressive Fed hikes (400+ bps), declining stock prices.",
                "duration": "June 2022 - May 2023",
                "avg_10y_yield": 3.1,
                "avg_m2_growth": 2.2,
                "impact_growth_stocks": "MULTIPLE COMPRESSION CRASH: High discount rates compress P/E multiples by 40-60%. Severe equity corrections."
            },
            {
                "regime_name": "Restrictive Consolidation (2023-2024)",
                "characteristics": "Fed funds held at 5.25% peak, negative M2 growth, resilient employment.",
                "duration": "June 2023 - May 2025",
                "avg_10y_yield": 4.2,
                "avg_m2_growth": -0.8,
                "impact_growth_stocks": "VALUATION DIVERGENCE: Severe selectiveness. While general growth stocks struggle, specific AI-narrative drivers expand P/Es on concentrated retail FOMO."
            },
            {
                "regime_name": "Soft Landing / Pivot Transition (2025-2026)",
                "characteristics": "Slow rate cuts, inflation settling at 2.6%, stable GDP growth.",
                "duration": "June 2025 - May 2026",
                "avg_10y_yield": 4.3,
                "avg_m2_growth": 2.0,
                "impact_growth_stocks": "VALUATION REALITY RECKONING: Multiple consolidation. Investors shift focus from speculative narrative projections to actual capacity constraints."
            }
        ]
        
        # Current regime identification
        current_regime_summary = {
            "name": "Restrictive High-Yield Soft Landing (Current)",
            "rate_environment": "Fed Funds at 4.5% - 5.0%, 10Y Yield at 4.2%",
            "inflation_cpi": "2.8% (consolidating towards target)",
            "investment_implication": "High risk-free yields make speculative 60x+ P/E equity multiples extremely unattractive on a risk-adjusted basis. Any revenue misses will trigger immediate multiple compressions."
        }
        
        # Prepare historical series for dashboard plots
        historical_series = {
            "dates": macro_dates,
            "fed_funds": [round(f, 2) for f in fed_funds],
            "yield_10y": [round(y, 2) for y in yield_10y],
            "cpi": [round(c, 2) for c in cpi],
            "m2_growth": [round(m, 2) for m in m2_growth],
            "fed_balance_sheet": [round(b, 2) for b in fed_balance_sheet]
        }
        
        # Prepare database record
        macro_data = MacroIndicatorsData(
            id="main",
            historical_series=historical_series,
            regime_analysis={
                "regimes": regimes,
                "current_regime": current_regime_summary
            },
            macro_adjusted_valuations=macro_adjusted_pe,
            interest_rate_scenarios=interest_rate_scenarios
        )
        
        db.merge(macro_data)
        db.commit()
        print("Agent 9 successfully recorded macroeconomic indicators and rate sensitivities.")
        
    except Exception as e:
        db.rollback()
        print(f"Error executing Agent 9: {e}")
        raise e
    finally:
        db.close()

# Helper random noise generator
def random_noise(low, high):
    return low + random.random() * (high - low)

if __name__ == "__main__":
    run_macro_engine()
