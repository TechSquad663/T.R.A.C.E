# TRACE Machine Learning Methodology

## 1. Rationale for Model Selection

### Primary Supervised Detector: XGBoost (Extreme Gradient Boosting)
- **Why Selected:** Financial transaction traffic features are tabular, heterogeneous, and exhibit non-linear interactions and heavy-tailed distributions. Tree-based gradient boosting models consistently outperform neural architectures on structured tabular telemetry without requiring extensive normalization.
- **Role:** Evaluates an entity's behavioral profile against known anomaly archetypes (e.g., rapid bursts, high fan-out dispersion, multi-hop chains, proxy relaying).
- **Output:** Calibrated `model_probability` between 0.0 and 1.0 (labeled as mathematical probability, never legal proof).

### Secondary Unsupervised Detector: Isolation Forest
- **Why Selected:** Criminal financial behavior frequently diverges from established baseline traffic without resembling known attack templates. Isolation Forest isolates anomalies by randomly partitioning feature dimensions; outliers require significantly fewer splits to isolate than normal points.
- **Independence:** Operates without labels. An entity can be statistically anomalous but have low supervised risk, or vice versa.
- **Output:** `anomaly_score` normalized to [0, 1] and boolean `is_anomaly`.

### Behavioral Clustering: DBSCAN
- **Why Selected:** Density-Based Spatial Clustering of Applications with Noise (DBSCAN) discovers arbitrary-shaped behavioral cohorts and explicitly segregates noise (`cluster_id = -1`). Unlike k-Means, it does not force anomalous outliers into synthetic centroids or require an a priori count of clusters.

---

## 2. Feature Vector Engineering

The model inputs 28 quantitative features spanning four forensic dimensions:

### Behavioral Flow Features
- `tx_count`: Total transaction occurrences.
- `total_in`, `total_out`: Aggregated BTC volume.
- `avg_amount`, `max_amount`, `std_amount`: Dispersion and volatility of transfers.
- `unique_counterparties`: Count of distinct interacting peer wallets.
- `fan_in_ratio`: Inbound consolidation transfers / Total transfers.
- `fan_out_ratio`: Outbound dispersion transfers / Total transfers.

### Temporal Dynamics Features
- `tx_velocity_per_hour`: Transaction frequency per unit time.
- `burst_score`: Standardized burstiness coefficient $B = \frac{\sigma - \mu}{\sigma + \mu}$.
- `avg_interval_seconds`, `std_interval_seconds`: Inter-transaction timing distribution.
- `active_span_hours`: Duration from first to last observation.

### Network Layer Features
- `unique_source_ips`: Number of distinct P2P nodes broadcasting entity transactions.
- `unique_countries`, `unique_asns`: Geographic and autonomous system distribution.
- `ip_reuse_rate`: Ratio of observations to unique endpoints.
- `port_diversity`: Variance in TCP source ports.

### Graph Topological Features
- `graph_degree`, `graph_in_degree`, `graph_out_degree`: Multigraph connectivity.
- `graph_pagerank`: Prominence and influence in fund circulation.
- `graph_betweenness`: Brokerage positioning along transaction paths.
- `graph_clustering_coeff`: Triadic peer clustering.

---

## 3. Strict Ground Truth Isolation

Ground truth scenario labels (`scenario`, `is_suspicious`, `ground_truth_label`) are strictly isolated from the feature generation pipeline. Ground truth data is maintained in an independent evaluation container and is only utilized for holdout metric computation (`precision`, `recall`, `F1-score`, `ROC-AUC`).
