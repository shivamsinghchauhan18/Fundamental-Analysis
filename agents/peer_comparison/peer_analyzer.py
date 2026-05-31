import sys
import os
import json
from datetime import datetime

# Enable import from shared module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import SessionLocal
from shared.models import PeerComparisonData, HistoricalFinancials

def run_peer_analyzer():
    db = SessionLocal()
    try:
        print("Starting Agent 10: Automotive & Tech Peer Analysis...")
        
        # 1. Fetch current financials for Tesla from DB
        tsla_fin = db.query(HistoricalFinancials).filter(HistoricalFinancials.company == "TSLA").first()
        
        if not tsla_fin:
            print("[Warning] TSLA financials record missing! Make sure Agent 1 runs first.")
            return
            
        tsla_pe = tsla_fin.current_pe # 65.0
        tsla_ps = 6.8 # standard P/S
        tsla_ev_ebitda = 49.3 # standard EV/EBITDA
        tsla_margin = tsla_fin.gross_margin_trend[-1] # 17.8
        tsla_growth = tsla_fin.revenue_cagr_5y # 32.4
        tsla_market_cap = 700.0 # Billions
        
        # 2. Define Automotive Peer Group
        auto_peers = [
            {"symbol": "TM", "name": "Toyota Motor", "pe": 9.8, "ps": 0.82, "ev_ebitda": 6.8, "margin": 18.0, "growth": 6.2, "market_cap": 280.0},
            {"symbol": "GM", "name": "General Motors", "pe": 5.5, "ps": 0.35, "ev_ebitda": 4.2, "margin": 13.5, "growth": 4.8, "market_cap": 50.0},
            {"symbol": "F", "name": "Ford Motor", "pe": 6.2, "ps": 0.28, "ev_ebitda": 5.1, "margin": 10.2, "growth": 3.5, "market_cap": 45.0},
            {"symbol": "BMW", "name": "BMW Group", "pe": 7.2, "ps": 0.45, "ev_ebitda": 4.8, "margin": 19.5, "growth": 5.0, "market_cap": 65.0},
            {"symbol": "RIVN", "name": "Rivian Auto", "pe": 20.0, "ps": 2.10, "ev_ebitda": 15.0, "margin": -12.5, "growth": 18.0, "market_cap": 12.0}, # positive proxy pe for average
            {"symbol": "LCID", "name": "Lucid Group", "pe": 25.0, "ps": 8.50, "ev_ebitda": 18.0, "margin": -85.0, "growth": 14.2, "market_cap": 8.0}
        ]
        
        # 3. Define Tech/Autonomy/Storage Peer Group
        tech_peers = [
            {"symbol": "GOOGL", "name": "Alphabet (Waymo)", "pe": 27.0, "ps": 6.2, "ev_ebitda": 18.5, "margin": 56.5, "growth": 14.1, "market_cap": 2100.0},
            {"symbol": "UBER", "name": "Uber Technologies", "pe": 35.0, "ps": 3.2, "ev_ebitda": 24.2, "margin": 38.5, "growth": 15.5, "market_cap": 140.0},
            {"symbol": "LYFT", "name": "Lyft Inc.", "pe": 18.2, "ps": 1.1, "ev_ebitda": 12.5, "margin": 28.2, "growth": 11.2, "market_cap": 6.0},
            {"symbol": "ENPH", "name": "Enphase Energy", "pe": 28.5, "ps": 7.5, "ev_ebitda": 19.2, "margin": 44.5, "growth": 12.0, "market_cap": 15.0},
            {"symbol": "SEDG", "name": "SolarEdge Tech", "pe": 18.0, "ps": 2.5, "ev_ebitda": 11.8, "margin": 25.2, "growth": 8.5, "market_cap": 4.5}
        ]
        
        # 4. Calculate Sector Averages
        def calc_avg(peers, key):
            vals = [p[key] for p in peers]
            return sum(vals) / len(vals)
            
        auto_avg_pe = calc_avg(auto_peers, "pe") # approx. 12.3x
        auto_avg_ps = calc_avg(auto_peers, "ps") # approx. 2.0x
        auto_avg_ev = calc_avg(auto_peers, "ev_ebitda") # approx. 9.0x
        auto_avg_margin = calc_avg(auto_peers, "margin") # approx. 10.6%
        auto_avg_growth = calc_avg(auto_peers, "growth") # approx. 8.6%
        
        tech_avg_pe = calc_avg(tech_peers, "pe") # approx. 25.3x
        tech_avg_ps = calc_avg(tech_peers, "ps") # approx. 4.1x
        tech_avg_ev = calc_avg(tech_peers, "ev_ebitda") # approx. 17.2x
        tech_avg_margin = calc_avg(tech_peers, "margin") # approx. 38.6%
        tech_avg_growth = calc_avg(tech_peers, "growth") # approx. 12.3%
        
        # 5. Compile Peer Metrics Table
        peer_table = [
            {
                "peer_group": "Automotive Peers",
                "pe_avg": round(auto_avg_pe, 1),
                "ps_avg": round(auto_avg_ps, 2),
                "ev_ebitda_avg": round(auto_avg_ev, 1),
                "margin_avg": round(auto_avg_margin, 1),
                "growth_avg": round(auto_avg_growth, 1),
                "premium_pe": f"{tsla_pe / auto_avg_pe:.1f}x",
                "premium_ps": f"{tsla_ps / auto_avg_ps:.1f}x",
                "premium_ev": f"{tsla_ev_ebitda / auto_avg_ev:.1f}x"
            },
            {
                "peer_group": "Tech & AI Peers",
                "pe_avg": round(tech_avg_pe, 1),
                "ps_avg": round(tech_avg_ps, 2),
                "ev_ebitda_avg": round(tech_avg_ev, 1),
                "margin_avg": round(tech_avg_margin, 1),
                "growth_avg": round(tech_avg_growth, 1),
                "premium_pe": f"{tsla_pe / tech_avg_pe:.1f}x",
                "premium_ps": f"{tsla_ps / tech_avg_ps:.1f}x",
                "premium_ev": f"{tsla_ev_ebitda / tech_avg_ev:.1f}x"
            }
        ]
        
        # 6. Sum-of-Parts (SOTP) Valuation Model for Tesla
        # Break Tesla into segments based on 2026/2027 revenue run-rate projections
        shares = 3.18 # Billions
        
        # Segment 1: Automotive (Core production)
        auto_revenue = 80.0 # Billions
        auto_multiple = 2.0  # Toyota/BMW premium multiple
        auto_value = auto_revenue * auto_multiple # 160B
        
        # Segment 2: Energy Storage & Utility Megapacks
        energy_revenue = 8.5 # Billions
        energy_multiple = 4.0 # High-growth utility supplier (ENPH premium)
        energy_value = energy_revenue * energy_multiple # 34B
        
        # Segment 3: FSD Software & Subscriptions
        fsd_revenue = 3.5 # Billions
        fsd_multiple = 10.0 # High-margin SaaS multiple
        fsd_value = fsd_revenue * fsd_multiple # 35B
        
        # Segment 4: speculative Option Value of Robotaxi Network
        robotaxi_option_value = 50.0 # Billions (speculative)
        
        total_enterprise_value = auto_value + energy_value + fsd_value + robotaxi_option_value # 279.0B
        sotp_fair_price = total_enterprise_value / shares # $87.74
        
        sotp_details = {
            "segments": [
                {"name": "Automotive Division", "revenue": auto_revenue, "multiple": f"{auto_multiple}x P/S", "fair_value": auto_value, "desc": "Valued at 2.0x P/S (toyota-class premium EV manufacturer)."},
                {"name": "Energy Storage (Megapacks)", "revenue": energy_revenue, "multiple": f"{energy_multiple}x P/S", "fair_value": energy_value, "desc": "Utility battery supply valued at a premium storage multiplier."},
                {"name": "FSD Software & Subscriptions", "revenue": fsd_revenue, "multiple": f"{fsd_multiple}x P/S", "fair_value": fsd_value, "desc": "High-margin autonomy software valued at standard enterprise SaaS multiples."},
                {"name": "Robotaxi Option Premium", "revenue": 0.0, "multiple": "Speculative Option", "fair_value": robotaxi_option_value, "desc": "Generous option value placed on driverless autonomous network deployment."}
            ],
            "total_value": total_enterprise_value,
            "shares_outstanding": shares,
            "fair_price_per_share": round(sotp_fair_price, 2)
        }
        
        # 7. Scenario Weighting (three investor narratives)
        # EPS matching today's trailing (220.0 / 65.0) = 3.38
        eps = tsla_fin.current_price / tsla_fin.current_pe if tsla_fin.current_pe > 0 else 3.38
        
        # Narrative 1: Car Company (trades at auto peers average multiple)
        car_multiple = 8.0 # typical premium auto multiple (GM=5.5, TM=9.8)
        car_fair_price = eps * car_multiple # $27.0
        
        # Narrative 2: Tech Giant (trades at tech peers average multiple)
        tech_multiple = 28.0 # typical tech average (GOOGL=27, UBER=35)
        tech_fair_price = eps * tech_multiple # $94.6
        
        # Narrative 3: Hybrid Disruptor (weighted average + FSD premium)
        # 60% automotive weight + 40% tech weight + speculative $20 option price
        weighted_base = 0.60 * car_fair_price + 0.40 * tech_fair_price
        hybrid_fair_price = weighted_base + 20.0 # $74.0
        
        scenario_weightings = {
            "narratives": [
                {
                    "name": "Narrative A: Pure Car Company",
                    "weight_pct": 100,
                    "applied_pe": car_multiple,
                    "fair_value": round(car_fair_price, 2),
                    "downside_risk": round(100.0 * (1.0 - car_fair_price / tsla_fin.current_price), 1),
                    "implication": "Tesla is valued purely as an automotive manufacturing company. Applying the auto peer P/E average of 8x yields a fair value of $27.04 (87% downside), highlighting the danger of using vehicle sales to support tech multiples."
                },
                {
                    "name": "Narrative B: Pure Tech/AI Giant",
                    "weight_pct": 100,
                    "applied_pe": tech_multiple,
                    "fair_value": round(tech_fair_price, 2),
                    "downside_risk": round(100.0 * (1.0 - tech_fair_price / tsla_fin.current_price), 1),
                    "implication": "Tesla is valued fully as an autonomous software and robotics company. Applying the tech peer P/E average of 28.0x yields a fair value of $94.64 (57% downside), proving that even in a best-case tech scenario, today's $220 price remains heavily overvalued."
                },
                {
                    "name": "Narrative C: Hybrid Disruptor Thesis",
                    "weight_pct": "60% Auto / 40% Tech + FSD Option",
                    "applied_pe": "Weighted avg (16.0x)",
                    "fair_value": round(hybrid_fair_price, 2),
                    "downside_risk": round(100.0 * (1.0 - hybrid_fair_price / tsla_fin.current_price), 1),
                    "implication": "An analytical weighted consensus. Blending 60% automotive hardware multiples and 40% premium software tech multiples, plus adding a generous $20.00/share speculative FSD option value, yields a realistic fair value of $74.08 per share (66% downside)."
                }
            ],
            "conclusion": f"Even under the most optimistic narrative where Tesla is treated 100% as a high-margin tech giant, its fair price is capped at ${tech_fair_price:.2f} per share. Today's market price of $220.00 represents a 'Requires New Paradigm Range'—an irrational valuation that cannot be supported by traditional business fundamentals."
        }
        
        # Prepare database record
        peer_data = PeerComparisonData(
            company="TSLA",
            peer_metrics={
                "auto_peers": auto_peers,
                "tech_peers": tech_peers,
                "comparison_matrix": peer_table
            },
            sotp_model=sotp_details,
            scenario_weightings=scenario_weightings
        )
        
        db.merge(peer_data)
        db.commit()
        print("Agent 10 successfully compiled Tesla SOTP and peer valuation models.")
        
    except Exception as e:
        db.rollback()
        print(f"Error executing Agent 10: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_peer_analyzer()
