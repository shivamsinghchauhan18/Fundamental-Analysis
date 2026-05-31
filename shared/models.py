from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON
from datetime import datetime
from shared.database import Base

class HistoricalFinancials(Base):
    __tablename__ = "historical_financials"
    
    company = Column(String, primary_key=True, index=True)
    current_price = Column(Float, nullable=False)
    current_pe = Column(Float, nullable=False)
    forward_pe = Column(Float, nullable=True)
    current_peg = Column(Float, nullable=False)
    revenue_cagr_5y = Column(Float, nullable=False)
    gross_margin_trend = Column(JSON, nullable=False)        # List[float] over 5 years
    operating_margin_trend = Column(JSON, nullable=False)    # List[float] over 5 years
    net_margin_trend = Column(JSON, nullable=False)          # List[float] over 5 years
    fcf_margin = Column(Float, nullable=False)
    sector_median_pe = Column(Float, nullable=False)
    revenue_5y = Column(JSON, nullable=False)                # List[float] (annual)
    ebitda_5y = Column(JSON, nullable=False)                 # List[float] (annual)
    net_income_5y = Column(JSON, nullable=False)             # List[float] (annual)
    fcf_5y = Column(JSON, nullable=False)                    # List[float] (annual)
    roe = Column(Float, nullable=False)
    roa = Column(Float, nullable=False)
    alert = Column(String, nullable=False)
    educational_note = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CapacityAnalysis(Base):
    __tablename__ = "capacity_analysis"
    
    company = Column(String, primary_key=True, index=True)
    production_capacity = Column(JSON, nullable=False)      # Custom key-value pairs per company
    backlog_trends = Column(JSON, nullable=False)           # Custom backlog data
    implied_revenue_required = Column(Float, nullable=False)
    realistic_achievable_revenue = Column(Float, nullable=False)
    valuation_gap = Column(Float, nullable=False)
    waterfall_data = Column(JSON, nullable=False)           # {current: float, required: float, realistic: float, gap: float}
    educational_note = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SentimentData(Base):
    __tablename__ = "sentiment_data"
    
    company = Column(String, primary_key=True, index=True)
    sentiment_momentum_score = Column(Float, nullable=False)
    news_sentiment_score = Column(Float, nullable=False)
    news_sentiment_distribution = Column(JSON, nullable=False) # {positive: int, neutral: int, negative: int}
    analyst_upgrades = Column(Integer, nullable=False)
    analyst_downgrades = Column(Integer, nullable=False)
    price_target_avg = Column(Float, nullable=False)
    price_target_high = Column(Float, nullable=False)
    price_target_low = Column(Float, nullable=False)
    earnings_beat_frequency = Column(Float, nullable=False)
    ownership_institutional = Column(Float, nullable=False)
    ownership_retail = Column(Float, nullable=False)
    short_interest_pct = Column(Float, nullable=False)
    options_call_put_ratio = Column(Float, nullable=False)
    insider_selling_trend = Column(JSON, nullable=False)     # Custom JSON for insider sales
    red_flags = Column(JSON, nullable=False)                 # List[str]
    educational_note = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ValuationModels(Base):
    __tablename__ = "valuation_models"
    
    company = Column(String, primary_key=True, index=True)
    fair_pe_base = Column(Float, nullable=False)
    fair_price_bull = Column(Float, nullable=False)
    fair_price_base = Column(Float, nullable=False)
    fair_price_bear = Column(Float, nullable=False)
    downside_risk_pct = Column(Float, nullable=False)
    growth_rate_bull = Column(Float, nullable=False)
    growth_rate_base = Column(Float, nullable=False)
    growth_rate_bear = Column(Float, nullable=False)
    monte_carlo_distribution = Column(JSON, nullable=False) # Dictionary summarizing distribution and sample points
    value_at_risk_95 = Column(Float, nullable=False)
    stress_test_recession = Column(JSON, nullable=False)     # {growth: float, margin: float, price: float, downside: float}
    stress_test_competition = Column(JSON, nullable=False)   # {growth: float, margin: float, price: float, downside: float}
    stress_test_margin_pressure = Column(JSON, nullable=False) # {growth: float, margin: float, price: float, downside: float}
    sensitivity_matrix = Column(JSON, nullable=False)        # List[Dict[str, float]]
    breakeven_growth_years = Column(JSON, nullable=False)    # {growth_needed: float, years_needed: int}
    educational_note = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EarningsAlert(Base):
    __tablename__ = "earnings_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String, nullable=False)
    event_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    growth_rate_expected = Column(Float, nullable=False)
    growth_rate_actual = Column(Float, nullable=False)
    deviation_pct = Column(Float, nullable=False)
    action_taken = Column(String, nullable=False)
    alert_message = Column(String, nullable=False)
    is_active = Column(Integer, default=1)

class HistoricalStockSeries(Base):
    __tablename__ = "historical_stock_series"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

class StatisticalFoundationData(Base):
    __tablename__ = "statistical_foundation_data"
    
    company = Column(String, primary_key=True, index=True)
    missing_values_pct = Column(Float, nullable=False)
    outliers_detected = Column(Integer, nullable=False)
    distribution_type = Column(String, nullable=False)
    is_stationary = Column(Integer, nullable=False) # 1 if stationary, 0 if non-stationary
    jarque_bera_p_value = Column(Float, nullable=False)
    
    # Statistical summaries
    mean = Column(Float, nullable=False)
    median = Column(Float, nullable=False)
    std_dev = Column(Float, nullable=False)
    skewness = Column(Float, nullable=False)
    kurtosis = Column(Float, nullable=False)
    
    # ADF stats
    adf_statistic = Column(Float, nullable=False)
    adf_p_value = Column(Float, nullable=False)
    
    # Dynamic JSON data for plotting return distributions, QQ, and ACF
    returns_distribution = Column(JSON, nullable=False) # {bins: List[float], counts: List[int], normal_curve: List[float]}
    qq_plot_data = Column(JSON, nullable=False)          # {theoretical: List[float], sample: List[float]}
    acf_data = Column(JSON, nullable=False)              # {lags: List[int], values: List[float]}
    outliers_data = Column(JSON, nullable=False)          # {dates: List[str], prices: List[float], volumes: List[float]}
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CorrelationRiskData(Base):
    __tablename__ = "correlation_risk_data"
    
    id = Column(String, primary_key=True, default="main") # "main"
    correlation_matrix = Column(JSON, nullable=False)     # Pairwise Pearson matrix (11x11 dict)
    rolling_correlations = Column(JSON, nullable=False)   # Rolling 90-day correlation timelines
    betas = Column(JSON, nullable=False)                  # Betas vs S&P 500 for stocks
    alphas = Column(JSON, nullable=False)                 # CAPM Alphas vs S&P 500
    commodity_correlations = Column(JSON, nullable=False) # Specific asset vs commodity correlations
    risk_warnings = Column(JSON, nullable=False)          # List of correlation/concentration warnings
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GraphNetworkData(Base):
    __tablename__ = "graph_network_data"
    
    id = Column(String, primary_key=True, default="main") # "main"
    nodes = Column(JSON, nullable=False)                  # List[Dict[str, Any]] (vis.js/d3 structure)
    edges = Column(JSON, nullable=False)                  # List[Dict[str, Any]] (vis.js/d3 structure)
    centrality_metrics = Column(JSON, nullable=False)     # Centralities & clustering
    risk_paths = Column(JSON, nullable=False)             # Vulnerabilities & points of failure
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MacroIndicatorsData(Base):
    __tablename__ = "macro_indicators_data"
    
    id = Column(String, primary_key=True, default="main") # "main"
    historical_series = Column(JSON, nullable=False)      # Inflation, yields, M2, economic growth timelines
    regime_analysis = Column(JSON, nullable=False)        # Regime classifications and stats
    macro_adjusted_valuations = Column(JSON, nullable=False) # Macro-adjusted multiples for TSLA, NVDA, PLTR
    interest_rate_scenarios = Column(JSON, nullable=False) # Fair values under varying yields (+1%, +2%, etc.)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PeerComparisonData(Base):
    __tablename__ = "peer_comparison_data"
    
    company = Column(String, primary_key=True, index=True) # e.g. "TSLA"
    peer_metrics = Column(JSON, nullable=False)           # Detailed comparative metrics table
    sotp_model = Column(JSON, nullable=False)             # Sum of the Parts models
    scenario_weightings = Column(JSON, nullable=False)    # Tech vs Auto weighted fair values
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


