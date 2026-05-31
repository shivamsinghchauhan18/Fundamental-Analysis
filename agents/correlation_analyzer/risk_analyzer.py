import sys
import os
import json
import math
from datetime import datetime

# Enable import from shared module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import SessionLocal
from shared.models import HistoricalStockSeries, CorrelationRiskData

# Pearson Correlation coefficient formula
def pearson_correlation(x, y):
    n = len(x)
    if n == 0:
        return 0.0
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    den_x = sum((x[i] - mean_x)**2 for i in range(n))
    den_y = sum((y[i] - mean_y)**2 for i in range(n))
    
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / math.sqrt(den_x * den_y)

def run_risk_analyzer():
    db = SessionLocal()
    try:
        print("Starting Agent 7: Cross-Asset Correlation & Portfolio Risk Analyzer...")
        
        tickers = ["TSLA", "NVDA", "PLTR", "SPY", "QQQ", "IWM", "GLD", "USO", "COPX", "VIX", "TLT"]
        
        # 1. Fetch price records and organize by date
        data_by_date = {} # date -> symbol -> close
        
        for symbol in tickers:
            records = db.query(HistoricalStockSeries).filter(HistoricalStockSeries.symbol == symbol).all()
            for r in records:
                date_str = r.date.strftime("%Y-%m-%d")
                if date_str not in data_by_date:
                    data_by_date[date_str] = {}
                data_by_date[date_str][symbol] = r.close
                
        # Filter for dates where ALL 11 assets have data to ensure perfect date synchronization
        aligned_dates = sorted([d for d, syms in data_by_date.items() if len(syms) == len(tickers)])
        n_days = len(aligned_dates)
        
        if n_days < 2:
            print("[Warning] Insufficient synchronized date records. Seeding may have failed.")
            return
            
        print(f"Analyzing {n_days} days of synchronized price records...")
        
        # 2. Extract price matrices and calculate daily returns
        prices = {ticker: [data_by_date[d][ticker] for d in aligned_dates] for ticker in tickers}
        returns = {ticker: [] for ticker in tickers}
        
        for ticker in tickers:
            p_series = prices[ticker]
            for i in range(1, n_days):
                ret = (p_series[i] - p_series[i-1]) / p_series[i-1]
                returns[ticker].append(ret)
                
        n_ret = len(returns["SPY"])
        
        # 3. Compute 11x11 Pearson Correlation Matrix over full 5-year horizon
        corr_matrix = {}
        for t1 in tickers:
            corr_matrix[t1] = {}
            for t2 in tickers:
                corr_matrix[t1][t2] = round(pearson_correlation(returns[t1], returns[t2]), 4)
                
        # 4. CAPM Beta & Alpha vs. S&P 500 (SPY)
        # Risk-free rate assumptions
        rf_annual = 0.042 # 4.2%
        rf_daily = rf_annual / 252.0
        
        spy_rets = returns["SPY"]
        mean_spy = sum(spy_rets) / n_ret
        var_spy = sum((r - mean_spy)**2 for r in spy_rets) / (n_ret - 1)
        
        betas = {}
        alphas = {}
        
        # Annualized SPY return
        spy_annualized_ret = (prices["SPY"][-1] / prices["SPY"][0]) ** (252.0 / n_days) - 1.0
        
        for stock in ["TSLA", "NVDA", "PLTR"]:
            stock_rets = returns[stock]
            mean_stock = sum(stock_rets) / n_ret
            cov_stock_spy = sum((stock_rets[i] - mean_stock) * (spy_rets[i] - mean_spy) for i in range(n_ret)) / (n_ret - 1)
            
            # Beta = Covariance(Stock, Market) / Variance(Market)
            beta = cov_stock_spy / var_spy if var_spy > 0 else 1.0
            betas[stock] = round(beta, 3)
            
            # Annualized stock return
            stock_annualized_ret = (prices[stock][-1] / prices[stock][0]) ** (252.0 / n_days) - 1.0
            
            # Alpha = Stock Return - [Risk-Free Rate + Beta * (Market Return - Risk-Free Rate)]
            alpha = stock_annualized_ret - (rf_annual + beta * (spy_annualized_ret - rf_annual))
            alphas[stock] = round(alpha * 100.0, 2) # in percentage
            
        # 5. Rolling 90-day correlation trend chart data
        # Track rolling correlation of TSLA vs NVDA, TSLA vs PLTR, and NVDA vs PLTR
        # To make it performant, we sample every 5 days
        rolling_90 = {"dates": [], "TSLA_NVDA": [], "TSLA_PLTR": [], "NVDA_PLTR": []}
        window = 90
        
        for i in range(window, n_ret, 5):
            date_label = aligned_dates[i + 1] # mapped to dates
            tsla_w = returns["TSLA"][i - window : i]
            nvda_w = returns["NVDA"][i - window : i]
            pltr_w = returns["PLTR"][i - window : i]
            
            rolling_90["dates"].append(date_label)
            rolling_90["TSLA_NVDA"].append(round(pearson_correlation(tsla_w, nvda_w), 4))
            rolling_90["TSLA_PLTR"].append(round(pearson_correlation(tsla_w, pltr_w), 4))
            rolling_90["NVDA_PLTR"].append(round(pearson_correlation(nvda_w, pltr_w), 4))
            
        # 6. Specific Commodity Correlations
        # TSLA vs Copper (COPX) and Gold (GLD)
        # NVDA vs Gold (GLD)
        # All vs VIX (risk-off indicator)
        commodity_correlations = {
            "TSLA_COPX": corr_matrix["TSLA"]["COPX"],
            "TSLA_GLD": corr_matrix["TSLA"]["GLD"],
            "NVDA_GLD": corr_matrix["NVDA"]["GLD"],
            "PLTR_GLD": corr_matrix["PLTR"]["GLD"],
            "TSLA_VIX": corr_matrix["TSLA"]["VIX"],
            "NVDA_VIX": corr_matrix["NVDA"]["VIX"],
            "PLTR_VIX": corr_matrix["PLTR"]["VIX"]
        }
        
        # 7. Concentration Risk Detection & Regime Flags
        risk_warnings = []
        
        # Check if the overall TSLA-NVDA-PLTR rolling correlation ever spiked above 0.8
        high_corr_days = 0
        for idx in range(len(rolling_90["dates"])):
            c1 = rolling_90["TSLA_NVDA"][idx]
            c2 = rolling_90["TSLA_PLTR"][idx]
            c3 = rolling_90["NVDA_PLTR"][idx]
            if c1 > 0.8 or c2 > 0.8 or c3 > 0.8:
                high_corr_days += 1
                
        if high_corr_days > 0:
            risk_warnings.append(
                f"DIVERSIFICATION THREAT: Rolling 90-day correlation among growth assets spiked above 0.8 during market stress. Your hypothetical 'diversified' tech holdings are highly concentrated in systemic risk."
            )
            
        # Check if overall betas are very high
        for stock, beta_val in betas.items():
            if beta_val > 1.4:
                risk_warnings.append(
                    f"HIGH MARKET BETA SENSITIVITY: {stock} has a CAPM Beta of {beta_val:.2f}, indicating excessive amplification of market corrections. Combined with high P/E ratios, risk-adjusted multiples are dangerously expanded."
                )
                
        # Commodity warnings
        if abs(corr_matrix["TSLA"]["COPX"]) > 0.4:
            risk_warnings.append(
                f"SUPPLY CHAIN SENSITIVITY: Tesla shows significant correlation ({corr_matrix['TSLA']['COPX']:.2f}) with Copper prices, indicating that profit margins are highly vulnerable to commodity inflation (lithium/copper price surges)."
            )
            
        # VIX correlation warnings
        if corr_matrix["TSLA"]["VIX"] < -0.4:
            risk_warnings.append(
                f"TAIL RISK SHIELD DECAY: High negative correlation with VIX means market crash tail risk is extremely elevated. Price drop will be violent when market volatility spikes."
            )
            
        # Prepare database record
        risk_data = CorrelationRiskData(
            id="main",
            correlation_matrix=corr_matrix,
            rolling_correlations=rolling_90,
            betas=betas,
            alphas=alphas,
            commodity_correlations=commodity_correlations,
            risk_warnings=risk_warnings
        )
        
        db.merge(risk_data)
        db.commit()
        print("Agent 7 successfully saved asset correlations and CAPM metrics to database.")
        
    except Exception as e:
        db.rollback()
        print(f"Error executing Agent 7: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_risk_analyzer()
