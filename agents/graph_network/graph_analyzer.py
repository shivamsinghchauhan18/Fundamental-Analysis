import sys
import os
import json
import math
from datetime import datetime

# Enable import from shared module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import SessionLocal
from shared.models import GraphNetworkData

# Pure Python graph algorithms for total offline failsafe reliability
class PurePythonGraph:
    def __init__(self, nodes, edges):
        self.nodes = nodes # List of dicts: {"id": "...", "label": "..."}
        self.edges = edges # List of dicts: {"source": "...", "target": "...", "weight": 0.5}
        
        # Build adjacency list
        self.adj = {node["id"]: set() for node in self.nodes}
        self.in_edges = {node["id"]: set() for node in self.nodes}
        self.neighbors = {node["id"]: set() for node in self.nodes} # Undirected neighbors
        
        for edge in self.edges:
            src, tgt = edge["source"], edge["target"]
            if src in self.adj and tgt in self.adj:
                self.adj[src].add(tgt)
                self.in_edges[tgt].add(src)
                self.neighbors[src].add(tgt)
                self.neighbors[tgt].add(src)
                
    def degree_centrality(self):
        n = len(self.nodes)
        if n <= 1:
            return {node["id"]: 0.0 for node in self.nodes}
        
        # Undirected degree divided by (n-1)
        return {node_id: len(neighs) / (n - 1) for node_id, neighs in self.neighbors.items()}
        
    def clustering_coefficient(self):
        cc = {}
        for node in self.nodes:
            node_id = node["id"]
            neighs = list(self.neighbors[node_id])
            k = len(neighs)
            if k <= 1:
                cc[node_id] = 0.0
                continue
                
            # Count edges between neighbors
            links = 0
            for i in range(k):
                for j in range(i + 1, k):
                    n1, n2 = neighs[i], neighs[j]
                    if n2 in self.neighbors[n1]:
                        links += 1
            cc[node_id] = (2.0 * links) / (k * (k - 1))
        return cc
        
    def pagerank(self, d=0.85, max_iter=100, tol=1e-6):
        n = len(self.nodes)
        if n == 0:
            return {}
            
        pr = {node["id"]: 1.0 / n for node in self.nodes}
        
        # Out-degree list
        out_degrees = {node_id: len(self.adj[node_id]) for node_id in self.adj}
        
        for _ in range(max_iter):
            new_pr = {node_id: (1.0 - d) / n for node_id in pr}
            
            # Distribute PageRank
            dangling_sum = sum(pr[node_id] for node_id in pr if out_degrees[node_id] == 0)
            dangling_share = d * dangling_sum / n
            
            for node_id in new_pr:
                new_pr[node_id] += dangling_share
                
            for node_id in pr:
                if out_degrees[node_id] > 0:
                    share = d * pr[node_id] / out_degrees[node_id]
                    for target in self.adj[node_id]:
                        new_pr[target] += share
                        
            # Check convergence
            err = sum(abs(new_pr[node_id] - pr[node_id]) for node_id in pr)
            pr = new_pr
            if err < tol:
                break
                
        return pr
        
    def betweenness_centrality(self):
        # Implementation of Brandes' algorithm in pure Python
        bc = {node["id"]: 0.0 for node in self.nodes}
        
        for s in bc.keys():
            # S = Stack
            S = []
            # P = Predecessors list
            P = {node_id: [] for node_id in bc}
            # sigma = number of shortest paths from s to v
            sigma = {node_id: 0.0 for node_id in bc}
            sigma[s] = 1.0
            # d = distance from s
            d = {node_id: -1 for node_id in bc}
            d[s] = 0
            
            # Queue for BFS
            Q = [s]
            
            while Q:
                v = Q.pop(0)
                S.append(v)
                for w in self.neighbors[v]:
                    # Path discovery
                    if d[w] < 0:
                        Q.append(w)
                        d[w] = d[v] + 1
                    # Path counting
                    if d[w] == d[v] + 1:
                        sigma[w] += sigma[v]
                        P[w].append(v)
                        
            # Accumulation (backwards)
            delta = {node_id: 0.0 for node_id in bc}
            while S:
                w = S.pop()
                for v in P[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    bc[w] += delta[w]
                    
        # Normalize betweenness (undirected, divide by (n-1)(n-2)/2)
        n = len(self.nodes)
        if n > 2:
            scale = 2.0 / ((n - 1) * (n - 2))
            for node_id in bc:
                bc[node_id] = bc[node_id] * scale
                
        return bc

def run_graph_analyzer():
    db = SessionLocal()
    try:
        print("Starting Agent 8: Graph Network Analysis...")
        
        # 1. Define Nodes: growth companies, suppliers, customers, and competitors
        nodes = [
            # Primary Core Nodes
            {"id": "TSLA", "label": "Tesla, Inc. (TSLA)", "category": "core", "market_cap": 700.0, "pe": 65.0},
            {"id": "NVDA", "label": "NVIDIA Corp. (NVDA)", "category": "core", "market_cap": 2200.0, "pe": 72.0},
            {"id": "PLTR", "label": "Palantir Tech (PLTR)", "category": "core", "market_cap": 55.0, "pe": 160.0},
            
            # Supplier Nodes
            {"id": "TSMC", "label": "TSMC (Semiconductor Fab)", "category": "supplier", "market_cap": 650.0, "pe": 22.0},
            {"id": "PANASONIC", "label": "Panasonic (Batteries)", "category": "supplier", "market_cap": 30.0, "pe": 11.0},
            {"id": "AWS", "label": "Amazon AWS (Cloud Infra)", "category": "supplier", "market_cap": 800.0, "pe": 30.0},
            
            # Customer / Partner Nodes
            {"id": "MSFT", "label": "Microsoft Corp. (Customer)", "category": "customer", "market_cap": 3100.0, "pe": 36.0},
            {"id": "AMZN", "label": "Amazon.com (Customer)", "category": "customer", "market_cap": 1800.0, "pe": 40.0},
            {"id": "GOOGL", "label": "Alphabet Inc. (Customer)", "category": "customer", "market_cap": 2100.0, "pe": 27.0},
            {"id": "GOVT", "label": "US & Allied Govs (Customer)", "category": "customer", "market_cap": 1000.0, "pe": 0.0},
            {"id": "AUTOMAKERS", "label": "Global Auto OEM Customers", "category": "customer", "market_cap": 400.0, "pe": 8.5},
            
            # Competitor Nodes
            {"id": "RIVN", "label": "Rivian Automotive", "category": "competitor", "market_cap": 12.0, "pe": -4.0},
            {"id": "LCID", "label": "Lucid Group", "category": "competitor", "market_cap": 8.0, "pe": -3.0},
            {"id": "AMD", "label": "Advanced Micro Devices", "category": "competitor", "market_cap": 280.0, "pe": 68.0},
            {"id": "INTC", "label": "Intel Corp.", "category": "competitor", "market_cap": 140.0, "pe": 28.0},
            {"id": "SNOW", "label": "Snowflake Inc.", "category": "competitor", "market_cap": 50.0, "pe": -120.0},
            {"id": "DBX", "label": "Dropbox Inc.", "category": "competitor", "market_cap": 10.0, "pe": 18.0}
        ]
        
        # 2. Define Weighted Relationship Edges
        # weight represents relationship strength (dependency/importance, 0.0 to 1.0)
        edges = [
            # Nvidia dependencies
            {"source": "NVDA", "target": "TSMC", "type": "supply_chain", "weight": 0.95, "desc": "NVIDIA depends 95% on TSMC for advanced GPU CoWoS packaging. Zero fallback."},
            {"source": "NVDA", "target": "MSFT", "type": "customer", "weight": 0.22, "desc": "Microsoft is Nvidia's largest GPU customer (22% of Data Center sales)."},
            {"source": "NVDA", "target": "AMZN", "type": "customer", "weight": 0.15, "desc": "Amazon AWS is a primary chip buyer and cloud deployment partner."},
            {"source": "NVDA", "target": "GOOGL", "type": "customer", "weight": 0.12, "desc": "Google Cloud buys Nvidia chips while building internal TPU competitors."},
            {"source": "NVDA", "target": "AMD", "type": "competitor", "weight": 0.70, "desc": "AMD is Nvidia's largest competitor in AI hardware and high-performance computing."},
            {"source": "NVDA", "target": "INTC", "type": "competitor", "weight": 0.40, "desc": "Intel Gaudi chips compete with NVIDIA Hopper/Blackwell lineups."},
            
            # Tesla dependencies
            {"source": "TSLA", "target": "PANASONIC", "type": "supply_chain", "weight": 0.65, "desc": "Panasonic is Tesla's primary lithium battery cell supplier in the US."},
            {"source": "TSLA", "target": "AUTOMAKERS", "type": "competitor", "weight": 0.85, "desc": "Traditional OEMs GM, Ford, and Toyota aggressively expanding EV volume."},
            {"source": "TSLA", "target": "RIVN", "type": "competitor", "weight": 0.50, "desc": "Rivian is a high-end EV competitor in SUVs and trucks."},
            {"source": "TSLA", "target": "LCID", "type": "competitor", "weight": 0.40, "desc": "Lucid group competes directly in luxury EV sedan space."},
            
            # Palantir dependencies
            {"source": "PLTR", "target": "AWS", "type": "supply_chain", "weight": 0.45, "desc": "Palantir hosts a substantial portion of AIP cloud storage on AWS."},
            {"source": "PLTR", "target": "GOVT", "type": "customer", "weight": 0.54, "desc": "Government agencies represent 54% of Palantir's revenue base. Concentrated risk."},
            {"source": "PLTR", "target": "MSFT", "type": "customer", "weight": 0.10, "desc": "Microsoft Azure partnership integrates Palantir AIP for defense networks."},
            {"source": "PLTR", "target": "SNOW", "type": "competitor", "weight": 0.75, "desc": "Snowflake competes directly with Palantir in enterprise data cataloging & storage."},
            {"source": "PLTR", "target": "DBX", "type": "competitor", "weight": 0.20, "desc": "Dropbox operates in basic enterprise storage, posing low competitive risk."},
            
            # Inter-node cross dependencies
            {"source": "AMD", "target": "TSMC", "type": "supply_chain", "weight": 0.85, "desc": "AMD relies fully on TSMC manufacturing, competing for CoWoS allocation."},
            {"source": "MSFT", "target": "AMD", "type": "customer", "weight": 0.15, "desc": "Microsoft partners with AMD for alternative MI300 GPU hosting in Azure."},
            {"source": "GOOGL", "target": "TSLA", "type": "competitor", "weight": 0.60, "desc": "Google Waymo competes directly with Tesla FSD in the robotaxi space."}
        ]
        
        # 3. Calculate Graph Metrics using our PurePythonGraph engine
        graph = PurePythonGraph(nodes, edges)
        
        deg_centrality = graph.degree_centrality()
        clustering_coeff = graph.clustering_coefficient()
        pageranks = graph.pagerank()
        betweenness_cent = graph.betweenness_centrality()
        
        # 4. Bind metrics back to nodes JSON list for frontend rendering
        enhanced_nodes = []
        centrality_metrics = {}
        
        for node in nodes:
            node_id = node["id"]
            node_metrics = {
                "degree_centrality": round(deg_centrality[node_id], 4),
                "betweenness_centrality": round(betweenness_cent[node_id], 4),
                "clustering_coefficient": round(clustering_coeff[node_id], 4),
                "pagerank": round(pageranks[node_id], 4)
            }
            
            # Append metrics to node dictionary for vis.js
            node_copy = node.copy()
            node_copy["metrics"] = node_metrics
            enhanced_nodes.append(node_copy)
            
            centrality_metrics[node_id] = node_metrics
            
        # 5. Graph Risk Scanning: Vulnerabilities and concentration paths
        risk_paths = []
        
        # NVDA Single Point of Failure (TSMC)
        risk_paths.append({
            "vulnerability_type": "single_point_of_failure",
            "source": "NVDA",
            "bridge": "TSMC",
            "severity": "critical",
            "analysis": "CRITICAL RISK: Nvidia depends 95% on TSMC for wafer fabrication and advanced CoWoS packaging. Any geopolitical shutdown in Taiwan would instantly wipe out Nvidia's production capacity, rendering its P/E multiple of 72.0x completely unjustifiable."
        })
        
        # Palantir Government Concentration
        risk_paths.append({
            "vulnerability_type": "customer_concentration",
            "source": "PLTR",
            "target": "GOVT",
            "severity": "high",
            "analysis": "REVENUE CONCENTRATION: Palantir derives 54% of its revenue from government contracts. While stable, government budget cuts or shifts in procurement can lead to massive revenue volatility, indicating that pricing PLTR as a high-margin recurring SaaS product is risky."
        })
        
        # CoWoS Allocation Competition Encirclement
        risk_paths.append({
            "vulnerability_type": "competitive_encirclement",
            "source": "NVDA",
            "supplier": "TSMC",
            "competitor": "AMD",
            "severity": "medium",
            "analysis": "SUPPLY CHAIN ENCIRCLEMENT: Both Nvidia and AMD fully depend on TSMC for advanced silicon packaging. As AMD increases its MI300 production, it squeezes Nvidia's packaging allocation, posing margin pressure and volume constraints on Nvidia by 2027."
        })
        
        # Autonomous Vehicle Competitive Threat
        risk_paths.append({
            "vulnerability_type": "disruption_risk",
            "source": "TSLA",
            "competitor": "GOOGL",
            "severity": "high",
            "analysis": "AUTONOMY COMPETITION: Tesla's valuation premium is fully predicated on its FSD software and Robotaxi networks. However, Alphabet's Waymo has completed millions of fully driverless commercial miles and holds regulatory approvals, posing a severe competitive threat to Tesla's expected software multiples."
        })
        
        # Prepare database record
        network_data = GraphNetworkData(
            id="main",
            nodes=enhanced_nodes,
            edges=edges,
            centrality_metrics=centrality_metrics,
            risk_paths=risk_paths
        )
        
        db.merge(network_data)
        db.commit()
        print("Agent 8 successfully committed relationship graph networks and centralities to database.")
        
    except Exception as e:
        db.rollback()
        print(f"Error executing Agent 8: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_graph_analyzer()
