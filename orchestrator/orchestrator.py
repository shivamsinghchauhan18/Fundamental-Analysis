import sys
import os
import subprocess
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.seed_data import seed_database

def run_agent_script(script_path):
    print(f"\n==========================================")
    print(f"LAUNCHING AGENT SCRIPT: {os.path.basename(script_path)}")
    print(f"==========================================\n")
    
    start_time = time.time()
    
    # Run using the current python executable
    proc = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Read stdout and merged stderr in real time
    for line in proc.stdout:
        print(f"[{os.path.basename(script_path)[:12]}] {line.strip()}")
        
    proc.wait()
    elapsed = time.time() - start_time
    
    if proc.returncode != 0:
        print(f"\n[ERROR] Script {script_path} failed with exit code {proc.returncode}!")
        raise RuntimeError(f"Agent script failed: {script_path}")
        
    print(f"\n[SUCCESS] Completed {os.path.basename(script_path)} in {elapsed:.2f}s.\n")

def main():
    print("==================================================")
    print("  SENTIMENT VS REALITY ANALYZER ORCHESTRATOR")
    print("==================================================")
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Initialize and Seed Database
    print("\n[Step 1] Initializing and Seeding Database...")
    seed_database()
    
    # 2. Run Agent 1 (Financial Data Collector)
    agent1_path = os.path.join(root_dir, "agents", "financial_collector", "collector.py")
    run_agent_script(agent1_path)
    
    # 3. Run Agent 2 (Capacity & Backlog Analyzer)
    agent2_path = os.path.join(root_dir, "agents", "capacity_analyzer", "analyzer.py")
    run_agent_script(agent2_path)
    
    # 4. Run Agent 3 (Sentiment engine)
    agent3_path = os.path.join(root_dir, "agents", "sentiment_engine", "sentiment.py")
    run_agent_script(agent3_path)
    
    # 5. Run Agent 4 (PEG Valuation and simulations)
    agent4_path = os.path.join(root_dir, "agents", "valuation_modeler", "valuation.py")
    run_agent_script(agent4_path)
    
    # 6. Run Agent 6 (Statistical Foundation & EDA Engine)
    agent6_path = os.path.join(root_dir, "agents", "statistical_foundation", "eda_engine.py")
    run_agent_script(agent6_path)
    
    # 7. Run Agent 7 (Cross-Asset Correlation & Portfolio Risk Analyzer)
    agent7_path = os.path.join(root_dir, "agents", "correlation_analyzer", "risk_analyzer.py")
    run_agent_script(agent7_path)
    
    # 8. Run Agent 8 (Graph Network Analysis)
    agent8_path = os.path.join(root_dir, "agents", "graph_network", "graph_analyzer.py")
    run_agent_script(agent8_path)
    
    # 9. Run Agent 9 (Macroeconomic Indicator Integration)
    agent9_path = os.path.join(root_dir, "agents", "macro_indicators", "macro_engine.py")
    run_agent_script(agent9_path)
    
    # 10. Run Agent 10 (Automotive & Tech Peer Analysis)
    agent10_path = os.path.join(root_dir, "agents", "peer_comparison", "peer_analyzer.py")
    run_agent_script(agent10_path)
    
    print("\n==================================================")
    print("   ALL AGENTS IN SEQUENTIAL PIPELINE COMPLETED!")
    print("==================================================")

if __name__ == "__main__":
    main()
