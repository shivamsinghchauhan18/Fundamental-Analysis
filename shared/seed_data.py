from datetime import datetime, timedelta
import json
import math
import random
from shared.database import SessionLocal, init_db
from shared.models import HistoricalFinancials, CapacityAnalysis, SentimentData, ValuationModels, HistoricalStockSeries

SEED_HISTORICAL = [
    {
        "company": "TSLA",
        "current_price": 220.0,
        "current_pe": 65.0,
        "forward_pe": 55.0,
        "current_peg": 3.25,
        "revenue_cagr_5y": 32.4,
        "gross_margin_trend": [25.6, 27.0, 21.0, 18.2, 17.8],  # Compressing gross margins
        "operating_margin_trend": [12.1, 16.8, 9.2, 8.0, 8.5],
        "net_margin_trend": [10.2, 14.1, 8.0, 7.5, 8.2],
        "fcf_margin": 7.8,
        "sector_median_pe": 15.0,
        "revenue_5y": [53.8, 81.5, 96.8, 96.8, 102.5],  # In billions
        "ebitda_5y": [9.6, 16.7, 13.5, 12.8, 14.2],
        "net_income_5y": [5.5, 12.6, 7.3, 7.1, 8.4],
        "fcf_5y": [5.0, 7.6, 4.4, 4.3, 8.0],
        "roe": 14.5,
        "roa": 8.6,
        "alert": "OVERVALUED",
        "educational_note": "Tesla trades at a P/E of 65.0x, significantly above the sector median of 15.0x. A P/E of 65.0 implies investors expect a sustained growth rate of 65% per year to justify a PEG ratio of 1.0. However, Tesla's 5-year revenue CAGR has slowed to 32.4% and recent margins are compressing due to pricing pressure, raising concern that its growth is decelerating while the valuation remains priced for massive expansion."
    },
    {
        "company": "NVDA",
        "current_price": 950.0,
        "current_pe": 72.0,
        "forward_pe": 45.0,
        "current_peg": 2.88,
        "revenue_cagr_5y": 68.5,
        "gross_margin_trend": [64.9, 56.9, 72.7, 76.0, 75.2],  # Peak semiconductor margins
        "operating_margin_trend": [37.3, 33.4, 54.1, 62.0, 61.2],
        "net_margin_trend": [36.2, 32.0, 48.8, 55.0, 54.1],
        "fcf_margin": 45.5,
        "sector_median_pe": 25.0,
        "revenue_5y": [26.9, 27.0, 60.9, 96.3, 112.5],
        "ebitda_5y": [11.2, 10.1, 35.8, 62.5, 72.0],
        "net_income_5y": [9.7, 8.6, 29.8, 53.0, 60.8],
        "fcf_5y": [8.1, 7.5, 27.0, 48.2, 51.2],
        "roe": 72.0,
        "roa": 44.5,
        "alert": "OVERVALUED",
        "educational_note": "Nvidia trades at a trailing P/E of 72.0x, implying 72% expected growth. While Nvidia's 5-year revenue CAGR is an astonishing 68.5% driven by AI hyperscaler demand, the semiconductor industry is highly cyclical and packaging supply constraints (TSMC CoWoS capacity) along with hardware customer concentration create high volatility. At PEG 2.88, the stock is pricing in continuous, unconstrained AI chip purchasing."
    },
    {
        "company": "PLTR",
        "current_price": 24.0,
        "current_pe": 160.0,
        "forward_pe": 85.0,
        "current_peg": 6.4,
        "revenue_cagr_5y": 24.8,
        "gross_margin_trend": [77.5, 78.2, 79.1, 80.5, 81.3],
        "operating_margin_trend": [-10.5, -4.5, 5.0, 12.0, 16.5],  # Transitioning to GAAP profit
        "net_margin_trend": [-12.0, -5.2, 4.2, 10.0, 15.0],
        "fcf_margin": 26.2,
        "sector_median_pe": 32.0,
        "revenue_5y": [1.1, 1.5, 1.9, 2.2, 2.8],
        "ebitda_5y": [-0.1, -0.05, 0.2, 0.35, 0.58],
        "net_income_5y": [-0.13, -0.08, 0.08, 0.22, 0.42],
        "fcf_5y": [0.15, 0.32, 0.45, 0.65, 0.73],
        "roe": 12.8,
        "roa": 9.4,
        "alert": "OVERVALUED",
        "educational_note": "Palantir's trailing P/E of 160.0x represents a dramatic expectation mismatch (PEG of 6.4). An enterprise software company growing at a 5-year revenue CAGR of 24.8% cannot support a 160x multiple unless growth accelerates radically. High SG&A costs from its hands-on AIP 'bootcamps' indicate customer acquisition is capital-intensive, despite impressive gross margins."
    }
]

SEED_CAPACITY = [
    {
        "company": "TSLA",
        "production_capacity": {
            "Gigafactory Fremont Capacity": "650,000 vehicles/year",
            "Gigafactory Shanghai Capacity": "950,000 vehicles/year",
            "Gigafactory Berlin Capacity": "375,000 vehicles/year",
            "Gigafactory Texas Capacity": "375,000 vehicles/year",
            "Total Installed Capacity": "2,350,000 vehicles/year",
            "Global Utilization Rate": "85.2%",
            "Expansion Timeline": "Monterrey Gigafactory delayed; phase 2 Berlin on hold",
            "FSD Deferred Revenue Balance": "$3.1 Billion"
        },
        "backlog_trends": {
            "Automotive Backlog Days": "Declined from 45 days in 2022 to 8 days in 2026 (inventory buildup)",
            "Energy Storage Backlog": "Megapack backlog remains healthy at 14 months, but represents <15% of total sales"
        },
        "implied_revenue_required": 411.0,  # Billions
        "realistic_achievable_revenue": 150.0, # Billions
        "valuation_gap": 261.0, # Billions
        "waterfall_data": {
            "Current Revenue": 102.5,
            "Target Revenue (justifying P/E)": 411.0,
            "Realistic Maximum Revenue (2028)": 150.0,
            "Valuation Gap": 261.0
        },
        "educational_note": "Tesla's current market cap of ~$700B implies it must generate $35B in net income to justify its price at a standard P/E of 20x. At current net margins of 8.5%, this requires $411B in annual revenue—exceeding total global production capacity and realistic market share limitations by 2028, which supports a maximum of $150B. The $261B 'Hope Premium' reflects pricing-in of fully autonomous robotaxis and humanoid robots."
    },
    {
        "company": "NVDA",
        "production_capacity": {
            "GPU Supply Constraints": "TSMC CoWoS packaging capacity bottleneck. Demand outstrips allocation by 2.5x",
            "Customer Concentration Risk": "Microsoft, Meta, Amazon, and Google account for 44.5% of total Data Center revenue",
            "Competitive Share Pressure": "AMD MI300 series capturing 8.2% market share; Google TPU v5e and AWS Trainium/Inferentia rising",
            "Data Center Revenue Share": "84.8% of total revenue (Gaming declined to 11.2%)"
        },
        "backlog_trends": {
            "Lead Times for H200/Blackwell": "12-14 months backlog for top cloud providers",
            "Hyperscaler Capex Lifecycle": "Hyperscalers building capacity that will lead to digesting cycles in 2027/2028"
        },
        "implied_revenue_required": 183.0,
        "realistic_achievable_revenue": 120.0,
        "valuation_gap": 63.0,
        "waterfall_data": {
            "Current Revenue": 112.5,
            "Target Revenue (justifying P/E)": 183.0,
            "Realistic Maximum Revenue (2028)": 120.0,
            "Valuation Gap": 63.0
        },
        "educational_note": "Nvidia's valuation implies it must generate $183B in annual revenue by 2028 to satisfy a fair valuation (PEG=1.0 at 25% growth, giving P/E of 25x). While they currently dominate AI chips, semiconductor supply bottlenecks (TSMC packaging constraints) and the fact that hyperscalers will eventually complete buildout and enter digestion phases limits realistic revenue capacity to $120B. The $63B gap represents the premium placed on an unbroken, non-cyclical AI spending cycle."
    },
    {
        "company": "PLTR",
        "production_capacity": {
            "Government Revenue Share": "54.5%",
            "Commercial Revenue Share": "45.5%",
            "Net Dollar Retention Rate (NDR)": "112%",
            "AIP Bootcamp Client Acquisition": "Bootcamps increased from 20/quarter to 180/quarter, but are heavily resource-intensive",
            "CAC to LTV Ratio": "Customer Acquisition Cost is extremely high due to engineers deployed on-site (LTV/CAC = 2.1x)"
        },
        "backlog_trends": {
            "Remaining Performance Obligations (RPO)": "$1.4 Billion (growing at 18.5% YoY)",
            "Average Contract Value (ACV) Trend": "Average commercial ACV declining from $6.2M to $2.8M (broader base but smaller deals)"
        },
        "implied_revenue_required": 12.2,
        "realistic_achievable_revenue": 4.5,
        "valuation_gap": 7.7,
        "waterfall_data": {
            "Current Revenue": 2.8,
            "Target Revenue (justifying P/E)": 12.2,
            "Realistic Maximum Revenue (2028)": 4.5,
            "Valuation Gap": 7.7
        },
        "educational_note": "Palantir's trailing valuation implies a target revenue of $12.2B to satisfy a 30x P/E ratio at a 15% net margin. Given enterprise software competitive pressures and the lumpy nature of government contracts, Palantir's realistic 2028 revenue is capped at $4.5B. The $7.7B gap highlights how commercial AI bootcamp hype is priced as a high-margin recurring SaaS product, when it operates like a consultancy."
    }
]

SEED_SENTIMENT = [
    {
        "company": "TSLA",
        "sentiment_momentum_score": -0.45,
        "news_sentiment_score": -0.15,
        "news_sentiment_distribution": {"positive": 18, "neutral": 35, "negative": 47},
        "analyst_upgrades": 4,
        "analyst_downgrades": 16,
        "price_target_avg": 178.5,
        "price_target_high": 310.0,
        "price_target_low": 85.0,
        "earnings_beat_frequency": 60.0,
        "ownership_institutional": 42.5,
        "ownership_retail": 57.5,  # High retail ownership
        "short_interest_pct": 3.8,
        "options_call_put_ratio": 1.25,
        "insider_selling_trend": {
            "Insider Transaction Net (Last 12M)": "-$2.4 Billion (primarily Elon Musk)",
            "Institutional Buying Rate": "Declining (-4.2% YoY)",
            "Retail Buying Rate": "Accelerating (+12.5% YoY)"
        },
        "red_flags": [
            "Declining media sentiment and margin compression alongside elevated P/E",
            "Insiders selling massive volume while retail ownership hits historical peak (smart money exiting)",
            "Analyst downgrades accelerating due to electric vehicle delivery misses"
        ],
        "educational_note": "A highly typical pattern of retail FOMO. Media sentiment is negative due to price-cutting and autonomous vehicle delays, and institutional money is quietly rotating out (-4.2%), yet retail purchasing drives volume, keeping the P/E highly elevated."
    },
    {
        "company": "NVDA",
        "sentiment_momentum_score": 0.85,
        "news_sentiment_score": 0.72,
        "news_sentiment_distribution": {"positive": 72, "neutral": 20, "negative": 8},
        "analyst_upgrades": 24,
        "analyst_downgrades": 2,
        "price_target_avg": 1150.0,
        "price_target_high": 1400.0,
        "price_target_low": 800.0,
        "earnings_beat_frequency": 95.0,  # Extremely high beat rate
        "ownership_institutional": 68.2,
        "ownership_retail": 31.8,
        "short_interest_pct": 1.2,
        "options_call_put_ratio": 3.1,  # Massive bullish options activity
        "insider_selling_trend": {
            "Insider Transaction Net (Last 12M)": "-$1.8 Billion (executives liquidating scheduled stock options)",
            "Institutional Buying Rate": "Stabilizing (+1.5% YoY)",
            "Retail Buying Rate": "Extremely High (Retail volume matching institutional)"
        },
        "red_flags": [
            "Excessive bullishness in options market (Call/Put at 3.1x), historically a retail momentum peak signal",
            "Consistent earnings sandbagging (beating conservative estimates by double digits to fuel media narrative)",
            "Insider sales exceeding buying by 45:1"
        ],
        "educational_note": "Peak AI sentiment. Media articles are 72% positive, call/put ratio is a bubbly 3.1, and analysts are continuously raising targets (24 upgrades vs 2 downgrades). However, insiders are aggressively selling ($1.8B), taking advantage of the historic valuation peak."
    },
    {
        "company": "PLTR",
        "sentiment_momentum_score": 0.52,
        "news_sentiment_score": 0.42,
        "news_sentiment_distribution": {"positive": 55, "neutral": 30, "negative": 15},
        "analyst_upgrades": 12,
        "analyst_downgrades": 4,
        "price_target_avg": 22.0,
        "price_target_high": 35.0,
        "price_target_low": 9.0,
        "earnings_beat_frequency": 80.0,
        "ownership_institutional": 38.0,
        "ownership_retail": 62.0,  # Highly retail dominated
        "short_interest_pct": 6.5,
        "options_call_put_ratio": 1.85,
        "insider_selling_trend": {
            "Insider Transaction Net (Last 12M)": "-$840 Million (Alex Karp & Peter Thiel)",
            "Institutional Buying Rate": "Increasing (+2.8% YoY)",
            "Retail Buying Rate": "Highly volatile, sentiment-driven spikes"
        },
        "red_flags": [
            "Extremely high retail ownership (62%) and massive retail discussion board hype",
            "CEO and Co-founders sold over $800M in shares while stock surged",
            "Analyst target average ($22.0) sits below current market price ($24.0), signaling target detachment"
        ],
        "educational_note": "A prime example of high retail hype coupled with strategic insider selling. While Alex Karp and co-founders sold $840M, retail investors are aggressively bidding the price up based on commercial boot camp news, ignoring the underlying professional target consensus ($22.0)."
    }
]

# We will pre-generate a template of Monte Carlo distributions for the seed data so they render instantly
def generate_monte_carlo_template(company, base_price, growth_rate, std_dev=0.15, steps=252):
    import math
    import random
    # Seed random for consistency
    random.seed(42 if company == "TSLA" else (43 if company == "NVDA" else 44))
    
    # Simple Geometric Brownian Motion paths
    paths = []
    sample_paths = []
    for _ in range(1000): # Seed uses 1000 paths for fast DB storage, orchestrator runs 10,000
        path = [base_price]
        current = base_price
        for _ in range(steps):
            z = random.normalvariate(0.0, 1.0)
            pct = (growth_rate - 0.5 * (std_dev**2)) / steps + std_dev * z / math.sqrt(steps)
            current *= (1 + pct)
            path.append(current)
        paths.append(path[-1])
        if len(sample_paths) < 100:
            sample_paths.append(path)
        
    paths = sorted(paths)
    
    def get_percentile(sorted_list, pct):
        idx = (len(sorted_list) - 1) * (pct / 100.0)
        low = math.floor(idx)
        high = math.ceil(idx)
        if low == high:
            return sorted_list[low]
        return sorted_list[low] * (high - idx) + sorted_list[high] * (idx - low)
        
    percentiles = {
        "p5": float(get_percentile(paths, 5)),
        "p25": float(get_percentile(paths, 25)),
        "p50": float(get_percentile(paths, 50)),
        "p75": float(get_percentile(paths, 75)),
        "p95": float(get_percentile(paths, 95))
    }
    # Value at Risk at 95% is the 5th percentile price relative to current
    var_95 = max(0.0, 100.0 * (1.0 - percentiles["p5"] / base_price))
    return sample_paths, percentiles, var_95  # sample paths, metrics, var

def get_seed_valuations():
    # Build seed valuations dynamically based on target math
    # TSLA: Base growth 20%. Fair PE = 20. Net margin 8.2%. Current EPS = 220 / 65 = 3.38
    # Fair Price = 3.38 * 20 = 67.6
    
    # NVDA: Base growth 25%. Fair PE = 25. Current EPS = 950 / 72 = 13.19
    # Fair Price = 13.19 * 25 = 329.7
    
    # PLTR: Base growth 20%. Fair PE = 20. Current EPS = 24 / 160 = 0.15
    # Fair Price = 0.15 * 20 = 3.0
    
    # Generating Monte Carlo
    tsla_paths, tsla_perc, tsla_var = generate_monte_carlo_template("TSLA", 220.0, 0.05) # under stress, growth slows
    nvda_paths, nvda_perc, nvda_var = generate_monte_carlo_template("NVDA", 950.0, 0.12)
    pltr_paths, pltr_perc, pltr_var = generate_monte_carlo_template("PLTR", 24.0, 0.08)
    
    return [
        {
            "company": "TSLA",
            "fair_pe_base": 20.0,
            "fair_price_bull": 118.3,
            "fair_price_base": 67.6,
            "fair_price_bear": 50.7,
            "downside_risk_pct": 69.27,
            "growth_rate_bull": 35.0,
            "growth_rate_base": 20.0,
            "growth_rate_bear": 15.0,
            "monte_carlo_distribution": {"sample": tsla_paths, "percentiles": tsla_perc},
            "value_at_risk_95": tsla_var,
            "stress_test_recession": {"growth": 5.0, "margin": 5.2, "fair_price": 16.9, "downside": 92.3},
            "stress_test_competition": {"growth": 10.0, "margin": 6.5, "fair_price": 33.8, "downside": 84.6},
            "stress_test_margin_pressure": {"growth": 18.0, "margin": 4.5, "fair_price": 60.8, "downside": 72.4},
            "sensitivity_matrix": [
                {"growth": 10.0, "peg_0_8": 27.0, "peg_1_0": 33.8, "peg_1_2": 40.6},
                {"growth": 20.0, "peg_0_8": 54.1, "peg_1_0": 67.6, "peg_1_2": 81.1},
                {"growth": 30.0, "peg_0_8": 81.1, "peg_1_0": 101.4, "peg_1_2": 121.7}
            ],
            "breakeven_growth_years": {"growth_needed": 45.2, "years_needed": 10},
            "educational_note": "Using PEG = 1.0, Tesla's fair value P/E is capped at its base growth rate of 20%, generating a P/E target of 20.0x vs. today's 65.0x. This projects a fair value of $67.6, presenting a 69% downside risk. To justify today's $220 share price at PEG = 1.0, Tesla must grow its EPS at 45.2% annually for the next 10 years, which is operationally unachievable under vehicle capacity ceilings."
        },
        {
            "company": "NVDA",
            "fair_pe_base": 25.0,
            "fair_price_bull": 461.6,
            "fair_price_base": 329.7,
            "fair_price_bear": 197.8,
            "downside_risk_pct": 65.3,
            "growth_rate_bull": 35.0,
            "growth_rate_base": 25.0,
            "growth_rate_bear": 15.0,
            "monte_carlo_distribution": {"sample": nvda_paths, "percentiles": nvda_perc},
            "value_at_risk_95": nvda_var,
            "stress_test_recession": {"growth": 8.0, "margin": 32.5, "fair_price": 105.5, "downside": 88.9},
            "stress_test_competition": {"growth": 12.0, "margin": 40.0, "fair_price": 158.3, "downside": 83.3},
            "stress_test_margin_pressure": {"growth": 20.0, "margin": 38.0, "fair_price": 263.8, "downside": 72.2},
            "sensitivity_matrix": [
                {"growth": 15.0, "peg_0_8": 158.3, "peg_1_0": 197.8, "peg_1_2": 237.4},
                {"growth": 25.0, "peg_0_8": 263.8, "peg_1_0": 329.7, "peg_1_2": 395.7},
                {"growth": 35.0, "peg_0_8": 369.3, "peg_1_0": 461.6, "peg_1_2": 553.9}
            ],
            "breakeven_growth_years": {"growth_needed": 36.8, "years_needed": 10},
            "educational_note": "A highly profitable cyclical business valued as a compounding utility. Capping base growth at 25% due to CoWoS constraints yields a fair price of $329.7. Under a competition stress test (market share slides 10%, gross margins compress to 40%), fair value drops to $158.3, representing an 83% downside from the AI-narrative peak."
        },
        {
            "company": "PLTR",
            "fair_pe_base": 20.0,
            "fair_price_bull": 4.5,
            "fair_price_base": 3.0,
            "fair_price_bear": 2.25,
            "downside_risk_pct": 87.5,
            "growth_rate_bull": 30.0,
            "growth_rate_base": 20.0,
            "growth_rate_bear": 15.0,
            "monte_carlo_distribution": {"sample": pltr_paths, "percentiles": pltr_perc},
            "value_at_risk_95": pltr_var,
            "stress_test_recession": {"growth": 5.0, "margin": 8.0, "fair_price": 0.75, "downside": 96.9},
            "stress_test_competition": {"growth": 10.0, "margin": 10.5, "fair_price": 1.5, "downside": 93.75},
            "stress_test_margin_pressure": {"growth": 15.0, "margin": 9.5, "fair_price": 2.25, "downside": 90.6},
            "sensitivity_matrix": [
                {"growth": 15.0, "peg_0_8": 1.8, "peg_1_0": 2.25, "peg_1_2": 2.7},
                {"growth": 20.0, "peg_0_8": 2.4, "peg_1_0": 3.0, "peg_1_2": 3.6},
                {"growth": 30.0, "peg_0_8": 3.6, "peg_1_0": 4.5, "peg_1_2": 5.4}
            ],
            "breakeven_growth_years": {"growth_needed": 58.4, "years_needed": 10},
            "educational_note": "Palantir's fair base price of $3.0 is a massive reduction from today's $24.0. To justify $24.0 at PEG = 1.0, Palantir must grow at 58.4% compounded for 10 years, which is unheard of in enterprise software, especially with current NDR (112%) and heavy human-consultancy bootcamp overhead."
        }
    ]

def generate_stock_series(n_days=1305):
    # Setup tickers, drifts, vols, correlations
    # Annualized parameters
    assets = {
        "SPY": {"mu": 0.09, "vol": 0.14, "rho": 1.0, "final": 510.0, "vol_base": 70e6},
        "QQQ": {"mu": 0.12, "vol": 0.18, "rho": 0.90, "final": 440.0, "vol_base": 45e6},
        "IWM": {"mu": 0.08, "vol": 0.20, "rho": 0.75, "final": 200.0, "vol_base": 30e6},
        "TSLA": {"mu": 0.15, "vol": 0.40, "rho": 0.65, "final": 220.0, "vol_base": 85e6},
        "NVDA": {"mu": 0.22, "vol": 0.44, "rho": 0.70, "final": 950.0, "vol_base": 55e6},
        "PLTR": {"mu": 0.18, "vol": 0.48, "rho": 0.60, "final": 24.0, "vol_base": 35e6},
        "GLD": {"mu": 0.06, "vol": 0.11, "rho": -0.10, "final": 210.0, "vol_base": 8e6},
        "USO": {"mu": 0.04, "vol": 0.28, "rho": 0.25, "final": 75.0, "vol_base": 12e6},
        "COPX": {"mu": 0.07, "vol": 0.26, "rho": 0.40, "final": 45.0, "vol_base": 3e6},
        "TLT": {"mu": 0.02, "vol": 0.13, "rho": -0.15, "final": 92.0, "vol_base": 18e6},
    }
    
    dt = 1.0 / 252.0
    random.seed(42) # Deterministic
    
    # Store price paths
    paths = {ticker: [100.0] for ticker in assets}
    volumes = {ticker: [] for ticker in assets}
    
    for _ in range(n_days):
        Zm = random.normalvariate(0, 1)
        for ticker, params in assets.items():
            Zi = random.normalvariate(0, 1)
            # Daily drift and diffusion
            mu_d = (params["mu"] - 0.5 * params["vol"]**2) * dt
            sig_d = params["vol"] * math.sqrt(dt)
            
            # Correlated noise
            noise = params["rho"] * Zm + math.sqrt(1.0 - params["rho"]**2) * Zi
            ret = mu_d + sig_d * noise
            
            # Update price
            paths[ticker].append(paths[ticker][-1] * math.exp(ret))
            
            # Generate volume
            vol_noise = random.normalvariate(0, 0.2)
            vol = params["vol_base"] * math.exp(vol_noise)
            # Volume spikes when return is extreme
            if abs(ret) > 1.8 * params["vol"] * math.sqrt(dt):
                vol *= 1.8
            volumes[ticker].append(vol)
            
    # Model VIX separately as non-stationary/mean-reverting linked to SPY return
    vix_path = []
    # VIX is high when market return is negative
    for i in range(n_days):
        # We look at SPY return at day i
        spy_ret = math.log(paths["SPY"][i+1] / paths["SPY"][i])
        # VIX base is 15. Standard leverage effect: VIX rises when SPY drops
        # Daily noise
        vix_noise = random.normalvariate(0, 0.15)
        # VIX formula
        vix_val = 14.5 * math.exp(-12.0 * spy_ret + vix_noise)
        vix_val = max(9.0, min(85.0, vix_val))
        vix_path.append(vix_val)
        
    # Now we adjust paths so they end EXACTLY at final prices
    adjusted_paths = {}
    for ticker, params in assets.items():
        raw_final = paths[ticker][-1]
        factor = params["final"] / raw_final
        # Scale all path prices
        adjusted_paths[ticker] = [p * factor for p in paths[ticker][1:]] # discard the first 100.0 start
        
    # Scale VIX to end at 14.0
    vix_factor = 14.0 / vix_path[-1]
    adjusted_paths["VIX"] = [v * vix_factor for v in vix_path]
    volumes["VIX"] = [0.0] * n_days
    
    return adjusted_paths, volumes

def seed_database():
    init_db()
    db = SessionLocal()
    try:
        print("Seeding database with high-fidelity financial modeling...")
        
        # 1. Historical Financials
        for item in SEED_HISTORICAL:
            obj = HistoricalFinancials(**item)
            db.merge(obj)
            
        # 2. Capacity Analysis
        for item in SEED_CAPACITY:
            obj = CapacityAnalysis(**item)
            db.merge(obj)
            
        # 3. Sentiment Data
        for item in SEED_SENTIMENT:
            obj = SentimentData(**item)
            db.merge(obj)
            
        # 4. Valuation Models
        for item in get_seed_valuations():
            obj = ValuationModels(**item)
            db.merge(obj)
            
        # 5. Historical Daily Stock Price Series (for TSLA, NVDA, PLTR and benchmarks/commodities)
        if db.query(HistoricalStockSeries).count() == 0:
            print("Generating and seeding 5 years of daily return series...")
            n_days = 1305
            prices, volumes = generate_stock_series(n_days)
            
            # Start date is 5 years before today (2026-05-27)
            current_date = datetime(2026, 5, 27)
            # Walk backwards to find 1305 business days
            dates = []
            temp_date = current_date - timedelta(days=1)
            while len(dates) < n_days:
                if temp_date.weekday() < 5: # Monday-Friday
                    dates.append(temp_date)
                temp_date -= timedelta(days=1)
            dates.reverse() # Order chronologically
            
            # Batch inserts for speed
            stock_records = []
            for i in range(n_days):
                date_val = dates[i]
                for symbol in prices.keys():
                    stock_records.append(
                        HistoricalStockSeries(
                            symbol=symbol,
                            date=date_val,
                            close=float(prices[symbol][i]),
                            volume=float(volumes[symbol][i])
                        )
                    )
            
            db.bulk_save_objects(stock_records)
            print(f"Successfully seeded {len(stock_records)} historical price records.")
            
        db.commit()
        print("Database successfully seeded with institutional-grade data!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
