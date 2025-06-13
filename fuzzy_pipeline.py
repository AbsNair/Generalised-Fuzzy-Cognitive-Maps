
import numpy as np
import pandas as pd
import re

def parse_interval(cell):
    # Handle if already sequence
    if isinstance(cell, (list, tuple, np.ndarray)):
        vals = list(cell)
    else:
        s = str(cell)
        # Split on commas or whitespace
        parts = re.split(r'[,\s]+', s.strip('()[]'))
        vals = [p for p in parts if p != '']
        # Convert to floats
        try:
            vals = [float(v) for v in vals]
        except ValueError:
            raise ValueError(f"Cannot parse interval from cell: {cell}")
    # Determine TFN components
    if len(vals) == 1:
        return (vals[0], vals[0], vals[0])
    if len(vals) == 2:
        lo, hi = vals
        return (lo, (lo + hi) / 2.0, hi)
    if len(vals) >= 3:
        return (vals[0], vals[1], vals[2])
    raise ValueError(f"Unexpected number of values in interval: {vals}")

def fuzzy_multiply(a, b):
    # Interval multiplication: all products of endpoints
    prods = [a[i] * b[j] for i in range(3) for j in range(3)]
    lo = min(prods)
    hi = max(prods)
    mid = np.median(prods)
    return (lo, mid, hi)

def defuzzify(tfn):
    # Centroid of triangular fuzzy number
    lo, mid, hi = tfn
    return (lo + mid + hi) / 3.0

def fuzzy_pipeline(W_df, I_df, clamp_concepts=None, lam=1.0, iterations=15):
    n = len(W_df)
    names = list(W_df.index)
    # Initialize fuzzy weight matrix
    W_fuzz = np.empty((n, n), dtype=object)
    for i, row in enumerate(names):
        for j, col in enumerate(names):
            if row == col:
                W_fuzz[i, j] = (1.0, 1.0, 1.0)
            else:
                W_fuzz[i, j] = parse_interval(W_df.loc[row, col])
    # Initialize fuzzy state
    C = [None] * (iterations + 1)
    C[0] = [parse_interval(I_df.iloc[0, j]) for j in range(n)]
    # Simulation
    crisp_hist = []
    for t in range(iterations + 1):
        # Defuzzify for analysis (centroids)
        crisp_hist.append([defuzzify(x) for x in C[t]])
        if t == iterations:
            break
        # Next state computation
        next_state = []
        for i in range(n):
            # sum of fuzzy multiplications
            sum_tfn = (0.0, 0.0, 0.0)
            for j in range(n):
                prod = fuzzy_multiply(W_fuzz[i, j], C[t][j])
                sum_tfn = (sum_tfn[0] + prod[0],
                           sum_tfn[1] + prod[1],
                           sum_tfn[2] + prod[2])
            # activation
            activated = tuple(np.tanh(lam * np.array(sum_tfn)))
            # clamp if needed
            if clamp_concepts and names[i] in clamp_concepts:
                next_state.append(C[0][i])
            else:
                next_state.append(activated)
        C[t+1] = next_state
    return C, crisp_hist, names


import networkx as nx
import numpy as np

def compute_graph_metrics(G):
    """Compute a variety of network metrics on graph G."""
    metrics = {}
    try:
        metrics["density"] = nx.density(G)
        metrics["avg_degree"] = np.mean([deg for _, deg in G.degree()])
        metrics["assortativity"] = nx.degree_assortativity_coefficient(G)
        metrics["clustering_coeff"] = nx.average_clustering(G.to_undirected())
        metrics["betweenness"] = nx.betweenness_centrality(G)
        metrics["closeness"] = nx.closeness_centrality(G)
        try:
            if nx.is_connected(G.to_undirected()):
                metrics["eigenvector"] = nx.eigenvector_centrality_numpy(G)
            else:
                metrics["eigenvector"] = "Graph not connected — eigenvector centrality skipped"
        except Exception as e:
            metrics["eigenvector"] = f"Error: {str(e)}"
        metrics["pagerank"] = nx.pagerank(G)
    except Exception as e:
        metrics["error"] = str(e)
    return metrics
