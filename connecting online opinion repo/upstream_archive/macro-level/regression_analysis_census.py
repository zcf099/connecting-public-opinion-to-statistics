# CANONICAL REPLACEMENT: the original draft OLS notebook is excluded.
# This entry point is the Table 3 reproduction implementation.

# -*- coding: utf-8 -*-
# Converted from table3_objective_regression_reproduction.ipynb.
# Project role: canonical Table 3 objective-model reproduction
# This standalone source contains the notebook code cells in order.
# Jupyter-only directives are retained as comments for provenance.
# IPython display has a print fallback for command-line execution.

# --- markdown cell 1 ---
# # Paper Table 3 reproduction: objective urban-development metrics
#
# This notebook reconstructs the published 38-city, 11-predictor OLS model.
# It uses visible preparation code, population-standardized variables (`ddof=0`),
# an intercept, and conventional nonrobust standard errors.

# --- code cell 2 ---
# Notebook directive (not executed): %matplotlib inline
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.graphics.regressionplots import plot_partregress_grid
try:
    from IPython.display import display
except ImportError:
    display = print

pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 180)
plt.style.use("seaborn-v0_8-whitegrid")

def locate_data_dir(require_aspects=False):
    cwd = Path.cwd().resolve()
    candidates = []
    for base in (cwd, *cwd.parents):
        candidates.extend([
            base / "data",
            base / "share_data",
            base / "macro-level" / "data",
        ])
    for candidate in candidates:
        census_ok = (candidate / "census_cities.csv").exists()
        aspects_ok = (candidate / "city_aspects.npy").exists()
        if census_ok and (aspects_ok or not require_aspects):
            return candidate
    needed = "census_cities.csv and city_aspects.npy" if require_aspects else "census_cities.csv"
    raise FileNotFoundError(f"Could not locate {needed} from {cwd}")

def zscore(values):
    return (values - values.mean()) / values.std(ddof=0)

# --- code cell 3 ---
DATA_DIR = locate_data_dir(require_aspects=False)
census = pd.read_csv(DATA_DIR / "census_cities.csv")

RACIAL_PROPORTION_COLUMNS = ('%Non Hispanic Black', '%Hispanic', '%Asian')
DISSIMILARITY_COLUMNS = ('White-Black dissimilarity index', 'White-Hispanic dissimilarity index', 'White-Asian dissimilarity index')
TABLE3_PREDICTORS = ('urban land area_sq mi', 'urban_pop_den_sq mi', 'poverty rate', 'median household income', 'commute_%carpool', 'commute_%drive', '%home ownership', 'Black_White income inequality', 'Hispanic_White income inequality', 'Driving Score', 'Walking Score')
EXCLUDED_METROS = ('Birmingham-Hoover, AL', 'Hartford-East Hartford-Middletown, CT', 'Indianapolis-Carmel-Anderson, IN', 'Jacksonville, FL', 'Las Vegas-Henderson-Paradise, NV', 'Oklahoma City, OK', 'Providence-Warwick, RI-MA', 'Richmond, VA', 'Riverside-San Bernardino-Ontario, CA', 'Virginia Beach-Norfolk-Newport News, VA-NC', 'Washington-Arlington-Alexandria, DC-VA-MD-WV')

required_columns = (
    ("Metro",) + RACIAL_PROPORTION_COLUMNS + DISSIMILARITY_COLUMNS + TABLE3_PREDICTORS
)
missing_columns = [column for column in required_columns if column not in census]
assert not missing_columns, f"Missing columns: {missing_columns}"

excluded_counts = census["Metro"].value_counts().reindex(EXCLUDED_METROS, fill_value=0)
assert (excluded_counts == 1).all(), excluded_counts[excluded_counts != 1].to_dict()
paper_rows = ~census["Metro"].isin(EXCLUDED_METROS)
assert int(paper_rows.sum()) == 38

racial_proportions = census[list(RACIAL_PROPORTION_COLUMNS)].to_numpy(float)
dissimilarity = census[list(DISSIMILARITY_COLUMNS)].to_numpy(float)
segregation_score = pd.Series(
    np.sum(racial_proportions * dissimilarity, axis=1),
    index=census.index,
    name="Seg_level",
)

sample_cities = census.loc[paper_rows, "Metro"].reset_index(drop=True)
X_raw = census.loc[paper_rows, list(TABLE3_PREDICTORS)].reset_index(drop=True)
y_raw = segregation_score.loc[paper_rows].reset_index(drop=True)
X = zscore(X_raw)
y = zscore(y_raw)
assert np.allclose(X.mean(), 0.0, atol=1e-12)
assert np.allclose(X.std(ddof=0), 1.0, atol=1e-12)

model = sm.OLS(y, sm.add_constant(X)).fit()

# --- code cell 4 ---
print(f"Data directory: {DATA_DIR}")
print(f"Paper sample size: {len(sample_cities)}")
display(pd.DataFrame({"metro": sample_cities}))
display(pd.concat([y_raw.describe().rename("segregation_score"), X_raw.describe().T], axis=1))

# --- code cell 5 ---
vif_table = pd.DataFrame({
    "predictor": X.columns,
    "VIF": [variance_inflation_factor(X.to_numpy(), i) for i in range(X.shape[1])],
})
print("Variance inflation factors")
display(vif_table.round(3))

# --- code cell 6 ---
expected_coefficients = [0.0, 0.5812, 0.6174, 0.3602, 0.3009, 0.1307, 0.6015, -0.007, 0.2348, -0.1384, -0.2758, 0.367]
expected_standard_errors = [0.087, 0.194, 0.184, 0.222, 0.241, 0.106, 0.211, 0.174, 0.128, 0.125, 0.191, 0.239]
expected_pvalues = [1.0, 0.006, 0.002, 0.117, 0.222, 0.231, 0.008, 0.968, 0.079, 0.278, 0.161, 0.137]
assert int(model.nobs) == 38
assert np.array_equal(np.round(np.asarray(model.params), 4), expected_coefficients)
assert np.array_equal(np.round(np.asarray(model.bse), 3), expected_standard_errors)
assert np.array_equal(np.round(np.asarray(model.pvalues), 3), expected_pvalues)
assert round(float(model.rsquared), 3) == 0.805
assert model.cov_type == "nonrobust"
print("Published Table 3 values reproduced at displayed precision.")
print(model.summary())

# --- code cell 7 ---
coef = model.params.drop("const")
ci = model.conf_int().loc[coef.index]
lower = coef - ci[0]
upper = ci[1] - coef

fig, ax = plt.subplots(figsize=(9, max(5, 0.42 * len(coef))))
positions = np.arange(len(coef))
ax.errorbar(coef, positions, xerr=np.vstack([lower, upper]), fmt="o", capsize=3, color="#225ea8")
ax.axvline(0, color="black", linewidth=1)
ax.set_yticks(positions, coef.index)
ax.set_xlabel("Standardized OLS coefficient with conventional 95% CI")
ax.set_title("Coefficient estimates")
ax.invert_yaxis()
fig.tight_layout()
plt.show()

# --- code cell 8 ---
fig = plt.figure(figsize=(12, 12))
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    plot_partregress_grid(model, fig=fig)
fig.suptitle("Partial-regression grid", y=1.01, fontsize=14)
fig.tight_layout()
plt.show()
