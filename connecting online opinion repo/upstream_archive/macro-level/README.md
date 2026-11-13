# Archived Upstream Collection and Aspect-Scoring Pipeline

This directory preserves the upstream Python scripts and lexicons originally used to collect Reddit city-subreddit comments and build `city_aspects.npy`.

- `cities_reddit_colllection.py`: BigQuery collection query over `fh-bigquery.reddit_comments.*` (2015–2019), deduplicating comments (`body`, `subreddit`, `author`, `created_utc`) and applying a deterministic 50,000-row per-city cap sorted by `created_utc`. (The GCP project identifier has been replaced with a placeholder `'YOUR_GCP_PROJECT'`; the frozen archived array `data/city_aspects.npy` used in all paper analyses is preserved verbatim.)
- `opinion_mining.py`: contraction expansion, preprocessing, noun-chunk / keyword aspect extraction, and sentiment scoring using `data/pos_words.txt`, `data/neg_words.txt`, `data/contractions.txt`, and `data/keyword_feature.csv`.
- `regression_analysis_census.py` & `regression_analysis_aspect.py`: canonical reference OLS reproduction scripts matching the baseline urban-statistics and archived online-score models (mirrored in `code/table3_objective_regression_reproduction.py` and `code/table4_online_regression_reproduction.py`).
