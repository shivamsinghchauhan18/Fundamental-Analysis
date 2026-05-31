import sys
import os
import json
import math
import random
from datetime import datetime

# Enable import from shared module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import SessionLocal
from shared.models import HistoricalStockSeries, StatisticalFoundationData

# Rational approximation for the inverse standard normal CDF (Acklam's algorithm)
def inv_normal_cdf(p):
    if p <= 0 or p >= 1:
        return 0.0
    
    # Coefficients in rational approximations
    a = [-3.969683028665376e+01,  2.209460984040017e+02, -2.759285104469687e+02,
          1.383577518672690e+02, -3.066479808861652e+01,  2.506628277459239e+00]
    b = [-5.447609879822406e+01,  1.615858368580409e+02, -1.556989798598866e+02,
          6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00,  4.374664141464968e+00,  2.938163982698783e+00]
    d = [ 7.784695709041462e-03,  3.224671290700398e-01,  2.445134137142993e+00,
          3.754408661907416e+00]
    
    p_low = 0.02425
    p_high = 1 - p_low
    
    if p < p_low:
        # Rational approximation for lower tail
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
               ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)
    elif p > p_high:
        # Rational approximation for upper tail
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0]*q + c[1])*q + c[2])*q + c[3])*q + c[4])*q + c[5]) / \
                ((((d[0]*q + d[1])*q + d[2])*q + d[3])*q + 1.0)
    else:
        # Rational approximation for central region
        q = p - 0.5
        r = q * q
        return (((((a[0]*r + a[1])*r + a[2])*r + a[3])*r + a[4])*r + a[5]) * q / \
               (((((b[0]*r + b[1])*r + b[2])*r + b[3])*r + b[4])*r + 1.0)

# Matrix transposition
def transpose(X):
    return [list(row) for row in zip(*X)]

# Matrix multiplication
def matmul(A, B):
    if not isinstance(A[0], list): # Vector to matrix-compatible
        A = [A]
    if not isinstance(B[0], list):
        B = [[x] for x in B]
    
    n_a_rows = len(A)
    n_a_cols = len(A[0])
    n_b_cols = len(B[0])
    
    result = [[0.0 for _ in range(n_b_cols)] for _ in range(n_a_rows)]
    for i in range(n_a_rows):
        for j in range(n_b_cols):
            result[i][j] = sum(A[i][k] * B[k][j] for k in range(n_a_cols))
            
    # Flatten if input was vector
    if len(result) == 1:
        return [row[0] for row in result] if n_b_cols == 1 else result[0]
    return result

# 2x2 Matrix Inverse (Self-contained for OLS Dickey-Fuller)
def invert2x2(A):
    det = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    if abs(det) < 1e-12:
        raise ValueError("Matrix is singular and cannot be inverted.")
    inv_det = 1.0 / det
    return [
        [A[1][1] * inv_det, -A[0][1] * inv_det],
        [-A[1][0] * inv_det, A[0][0] * inv_det]
    ]

# Ordinary Least Squares (OLS) Dickey-Fuller Test on a 1D series
def dickey_fuller_test(series):
    n = len(series)
    if n < 5:
        return 0.0, 1.0
    
    # Calculate differences (Delta y_t = y_t - y_{t-1})
    dy = [series[i] - series[i-1] for i in range(1, n)]
    
    # Lagged series (y_{t-1})
    ylag = series[:-1]
    
    # Construct OLS matrices: dy = alpha + beta * ylag + e
    # X matrix has columns [1, ylag_t]
    X = [[1.0, ylag[i]] for i in range(n-1)]
    Y = dy
    
    # Compute X^T * X and X^T * Y
    XT = transpose(X)
    XTX = [[sum(XT[i][k] * X[k][j] for k in range(n-1)) for j in range(2)] for i in range(2)]
    XTY = [sum(XT[i][k] * Y[k] for k in range(n-1)) for i in range(2)]
    
    try:
        invXTX = invert2x2(XTX)
    except ValueError:
        return 0.0, 1.0
        
    # Solve for coefficients B = (X^T * X)^-1 * X^T * Y
    # B = [alpha, beta]
    B = [
        invXTX[0][0] * XTY[0] + invXTX[0][1] * XTY[1],
        invXTX[1][0] * XTY[0] + invXTX[1][1] * XTY[1]
    ]
    
    alpha, beta = B[0], B[1]
    
    # Compute residuals e
    residuals = [Y[i] - (alpha + beta * ylag[i]) for i in range(n-1)]
    rss = sum(r * r for r in residuals)
    
    # Degrees of freedom: (n-1) - 2 parameters
    df = (n - 1) - 2
    s2 = rss / df
    
    # Standard error of beta (index 1 of invXTX)
    var_beta = s2 * invXTX[1][1]
    se_beta = math.sqrt(max(1e-15, var_beta))
    
    # Dickey-Fuller test statistic (t-stat of beta)
    df_stat = beta / se_beta
    
    # Critical value at 5% for no trend (standard DF table is around -2.87)
    # Approximate p-value using a standard logistic/normal approximation for DF distribution
    # Dickey-Fuller p-value approximation:
    # If df_stat < -2.87, p < 0.05
    # A simple sigmoid approximation for p-value:
    p_val = 1.0 / (1.0 + math.exp(-1.5 * (df_stat + 2.87)))
    
    return float(df_stat), float(p_val)

def run_eda():
    db = SessionLocal()
    try:
        print("Starting Agent 6: Statistical Foundation & EDA Engine...")
        
        companies = ["TSLA", "NVDA", "PLTR"]
        
        for symbol in companies:
            print(f"Executing EDA & Stationarity tests for {symbol}...")
            
            # 1. Fetch Price/Volume series
            records = db.query(HistoricalStockSeries).filter(HistoricalStockSeries.symbol == symbol).order_by(HistoricalStockSeries.date.asc()).all()
            
            if not records:
                print(f"[Warning] No stock price series found for {symbol}. Make sure database is seeded first.")
                continue
                
            prices = [r.close for r in records]
            volumes = [r.volume for r in records]
            dates = [r.date.strftime("%Y-%m-%d") for r in records]
            
            n = len(prices)
            
            # Failsafe: Impute missing values (forward fill)
            missing_count = 0
            for i in range(n):
                if prices[i] is None or math.isnan(prices[i]):
                    missing_count += 1
                    prices[i] = prices[i-1] if i > 0 else 100.0
                if volumes[i] is None or math.isnan(volumes[i]):
                    volumes[i] = volumes[i-1] if i > 0 else 1e6
            
            missing_pct = (missing_count / n) * 100.0
            
            # 2. Daily returns for distribution analysis
            returns = []
            for i in range(1, n):
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
                
            n_ret = len(returns)
            
            # 3. Descriptive Summary Statistics on Prices
            mean_p = sum(prices) / n
            sorted_prices = sorted(prices)
            median_p = sorted_prices[n // 2] if n % 2 != 0 else (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2.0
            
            var_p = sum((p - mean_p)**2 for p in prices) / (n - 1)
            std_p = math.sqrt(var_p)
            
            # Skewness & Kurtosis on returns (distribution of returns represents financial risk)
            mean_r = sum(returns) / n_ret
            var_r = sum((r - mean_r)**2 for r in returns) / (n_ret - 1)
            std_r = math.sqrt(var_r)
            
            m3_r = sum((r - mean_r)**3 for r in returns) / n_ret
            m4_r = sum((r - mean_r)**4 for r in returns) / n_ret
            
            skew_r = m3_r / (std_r**3) if std_r > 0 else 0.0
            kurt_r = m4_r / (std_r**4) if std_r > 0 else 0.0 # Excess kurtosis is kurt_r - 3.0
            
            # 4. Outlier Detection (using IQR method on returns)
            # Find Q1 and Q3 of returns
            sorted_returns = sorted(returns)
            idx_q1 = int(n_ret * 0.25)
            idx_q3 = int(n_ret * 0.75)
            q1_r = sorted_returns[idx_q1]
            q3_r = sorted_returns[idx_q3]
            iqr_r = q3_r - q1_r
            
            lower_bound_iqr = q1_r - 1.5 * iqr_r
            upper_bound_iqr = q3_r + 1.5 * iqr_r
            
            # Outlier detection on Price Series (Z-score > 3.0)
            price_outliers = []
            price_outliers_dates = []
            price_outliers_prices = []
            
            outliers_detected = 0
            for i in range(n):
                z_score = abs(prices[i] - mean_p) / std_p
                if z_score > 3.0:
                    outliers_detected += 1
                    price_outliers_dates.append(dates[i])
                    price_outliers_prices.append(prices[i])
            
            # 5. Stationarity Testing (Augmented Dickey-Fuller test on price series)
            df_stat, df_p_val = dickey_fuller_test(prices)
            # Dickey-Fuller critical values: -2.86 at 5% level
            is_stationary = 1 if df_stat < -2.86 else 0
            
            # 6. Return distribution normality test (Jarque-Bera)
            # JB = (n / 6) * (S^2 + (K - 3)^2 / 4)
            jb_stat = (n_ret / 6.0) * (skew_r**2 + ((kurt_r - 3.0)**2 / 4.0))
            # Chi-square with 2 degrees of freedom p-value approximation
            jb_p_val = math.exp(-jb_stat / 2.0)
            
            # Classify returns distribution
            if jb_p_val > 0.05:
                dist_type = "normal"
            elif kurt_r > 3.0:
                dist_type = "leptokurtic" # Fat tails (high crash risk)
            else:
                dist_type = "platykurtic" # Thin tails
                
            # 7. Time Series Decomposition (30-day moving average trend + residuals)
            trend_prices = []
            residual_prices = []
            window = 30
            for i in range(n):
                # Calculate SMA 30
                start_w = max(0, i - window + 1)
                sma_sum = sum(prices[start_w : i + 1])
                sma_count = i - start_w + 1
                trend = sma_sum / sma_count
                trend_prices.append(trend)
                # Residual is price minus trend
                residual_prices.append(prices[i] - trend)
                
            # 8. Generate QQ-plot points (daily returns vs theoretical normal)
            # Sort returns
            sorted_rets = sorted(returns)
            qq_theoretical = []
            qq_sample = []
            # Subsample 100 points for chart smoothness and performance
            sample_step = max(1, n_ret // 100)
            for idx in range(0, n_ret, sample_step):
                # Percentile rank
                p = (idx + 0.5) / n_ret
                # Theoretical normal quantile
                z_theo = inv_normal_cdf(p)
                # Standardized return
                z_sample = (sorted_rets[idx] - mean_r) / std_r
                
                qq_theoretical.append(z_theo)
                qq_sample.append(z_sample)
                
            # 9. Autocorrelation Function (ACF) up to lag 30
            acf_lags = list(range(1, 31))
            acf_values = []
            for lag in acf_lags:
                numerator = 0.0
                denominator = 0.0
                for t in range(lag, n_ret):
                    numerator += (returns[t] - mean_r) * (returns[t - lag] - mean_r)
                for t in range(n_ret):
                    denominator += (returns[t] - mean_r)**2
                
                acf_val = numerator / denominator if denominator > 0 else 0.0
                acf_values.append(acf_val)
                
            # 10. Generate returns distribution histogram data
            # Bin returns into 30 bins
            min_r, max_r = min(returns), max(returns)
            bin_width = (max_r - min_r) / 30
            bins = [min_r + i * bin_width for i in range(31)]
            counts = [0] * 30
            for r in returns:
                for b_idx in range(30):
                    if bins[b_idx] <= r < bins[b_idx+1]:
                        counts[b_idx] += 1
                        break
                if r == max_r: # Boundary condition
                    counts[-1] += 1
                    
            # Compute theoretical normal probability curve values for these bins
            normal_curve = []
            for b in bins[:-1]:
                # Standard normal density
                z = (b - mean_r) / std_r
                density = (1.0 / (std_r * math.sqrt(2.0 * math.pi))) * math.exp(-0.5 * z**2)
                # Scale density by sample size and bin width to overlay on frequency histogram
                normal_curve.append(density * n_ret * bin_width)
                
            # Prepare database record
            eda_data = StatisticalFoundationData(
                company=symbol,
                missing_values_pct=missing_pct,
                outliers_detected=outliers_detected,
                distribution_type=dist_type,
                is_stationary=is_stationary,
                jarque_bera_p_value=jb_p_val,
                mean=mean_p,
                median=median_p,
                std_dev=std_p,
                skewness=skew_r,
                kurtosis=kurt_r,
                adf_statistic=df_stat,
                adf_p_value=df_p_val,
                returns_distribution={
                    "bins": [round(b, 5) for b in bins],
                    "counts": counts,
                    "normal_curve": [round(c, 5) for c in normal_curve]
                },
                qq_plot_data={
                    "theoretical": [round(t, 5) for t in qq_theoretical],
                    "sample": [round(s, 5) for s in qq_sample]
                },
                acf_data={
                    "lags": acf_lags,
                    "values": [round(v, 4) for v in acf_values]
                },
                outliers_data={
                    "dates": price_outliers_dates,
                    "prices": [round(p, 2) for p in price_outliers_prices]
                }
            )
            
            db.merge(eda_data)
            
        db.commit()
        print("Agent 6 successfully saved EDA and statistical results to database.")
        
    except Exception as e:
        db.rollback()
        print(f"Error executing Agent 6: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_eda()
