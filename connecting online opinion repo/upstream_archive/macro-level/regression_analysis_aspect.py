# CANONICAL REPLACEMENT: the original draft OLS notebook is excluded.
# This entry point is the Table 4 reproduction implementation.

# -*- coding: utf-8 -*-
# Converted from table4_online_regression_reproduction.ipynb.
# Project role: canonical Table 4 online-opinion reproduction
# This standalone source contains the notebook code cells in order.
# Jupyter-only directives are retained as comments for provenance.
# IPython display has a print fallback for command-line execution.

# --- markdown cell 1 ---
# # Paper Table 4 reproduction: online opinion groups
#
# This notebook rebuilds the paper's 12 aspect groups from the preserved
# pre-grouping city scores. Missing city-by-group combinations are coded as zero,
# which exactly reproduces the published 38-city model.

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
DATA_DIR = locate_data_dir(require_aspects=True)
census = pd.read_csv(DATA_DIR / "census_cities.csv")
city_aspects = np.load(DATA_DIR / "city_aspects.npy", allow_pickle=True).item()

RACIAL_PROPORTION_COLUMNS = ('%Non Hispanic Black', '%Hispanic', '%Asian')
DISSIMILARITY_COLUMNS = ('White-Black dissimilarity index', 'White-Hispanic dissimilarity index', 'White-Asian dissimilarity index')
PAPER_GROUPS = {'Public Transportation': ('bus',
                           'buses',
                           'bus system',
                           'commuter rail',
                           'dart rail',
                           'mta',
                           'commute',
                           'light rail',
                           'train',
                           'trains',
                           'metro rail',
                           'marta',
                           'marta rail',
                           'metro',
                           'subway',
                           'transport',
                           'transportation',
                           'transit',
                           'transit plan',
                           'transit system',
                           'ferry',
                           'commuters'),
 'Driving and Traffic': ('drivers',
                         'driving',
                         'traffic',
                         'parking',
                         'distance',
                         'direction',
                         'vehicle',
                         'parking lot',
                         'highway',
                         'highways',
                         'ride sharing'),
 'Economy and Income': ('prices',
                        'economy',
                        'economies',
                        'income',
                        'investment',
                        'investments',
                        'revenue',
                        'salary',
                        'taxes',
                        'tax',
                        'salaries',
                        'capital gains',
                        'capital'),
 'Education': ('school', 'schools', 'school system', 'university', 'colleges'),
 'Culture and Art': ('concert', 'concerts', 'culture', 'museum', 'museums', 'movie', 'movies'),
 'Race/Immigration Discourse': ('hate crime',
               'foreigners',
               'asians',
               'blacks',
               'immigrant',
               'diversity',
               'race',
               'racism',
               'racist',
               'racists',
               'inequality',
               'majority',
               'minority'),
 'Recreation': ('nightlife',
                'clubs',
                'parks',
                'sports',
                'sport',
                'fans',
                'fan',
                'skiing',
                'football',
                'franchise',
                'baseball',
                'golf',
                'food',
                'foods'),
 'Social Problem': ('fraud',
                    'crime',
                    'crime problem',
                    'gun crime',
                    'firearms',
                    'criminals',
                    'drug addicts',
                    'drugs',
                    'guns',
                    'homeless',
                    'property crime',
                    'road rage',
                    'weed',
                    'violence',
                    'violence problem',
                    'murders',
                    'street crime',
                    'drug crime',
                    'murder',
                    'police brutality'),
 'Governing': ('cuomo',
               'mayor',
               'government',
               'officers',
               'governor',
               'law',
               'laws',
               'rent control',
               'rules',
               'policy',
               'policies',
               'regulations',
               'healthcare',
               'property taxes',
               'taxation'),
 'Policing': ('cops',
              'police',
              'speed limit',
              'speed limits',
              'justice',
              'enforcement',
              'policing',
              'nypd'),
 'Neighborhood': ('neighbors', 'neighborhoods', 'residents', 'environment', 'resources'),
 'City Development': ('business',
                      'building boom',
                      'planning',
                      'market',
                      'markets',
                      'growth',
                      'expansion',
                      'industry',
                      'construction',
                      'development',
                      'city limits',
                      'infrastructure')}

grouped_rows = []
zero_coded = []
for city, aspects in city_aspects.items():
    if city in {"Washington", "Birmingham"}:
        continue
    row = {"city": city}
    for group, keywords in PAPER_GROUPS.items():
        values = [aspects[keyword] for keyword in keywords if keyword in aspects]
        if values:
            row[group] = float(np.mean(values))
        else:
            row[group] = 0.0
            zero_coded.append((city, group))
    grouped_rows.append(row)

grouped = pd.DataFrame(grouped_rows)
assert len(grouped) == 38
assert len(zero_coded) == 27
assert not grouped[list(PAPER_GROUPS)].isna().any().any()

census_short = census["Metro"].str.split(r"-|,|/", n=1, regex=True).str[0]
assert not census_short.duplicated().any()
short_lookup = {name: int(index) for index, name in census_short.items()}
aliases = {"NYC": "New York", "Salt Lake": "Salt Lake City"}
crosswalk = {}
for city in grouped["city"]:
    census_name = aliases.get(city, city)
    assert census_name in short_lookup, city
    crosswalk[city] = short_lookup[census_name]
assert len(set(crosswalk.values())) == len(crosswalk)

racial_proportions = census[list(RACIAL_PROPORTION_COLUMNS)].to_numpy(float)
dissimilarity = census[list(DISSIMILARITY_COLUMNS)].to_numpy(float)
all_scores = pd.Series(
    np.sum(racial_proportions * dissimilarity, axis=1),
    index=census.index,
    name="Seg_level",
)

sample_cities = grouped["city"].reset_index(drop=True)
X_raw = grouped[list(PAPER_GROUPS)].reset_index(drop=True)
y_raw = pd.Series(
    [all_scores.loc[crosswalk[city]] for city in sample_cities],
    name="Seg_level",
)
X = zscore(X_raw)
y = zscore(y_raw)
assert np.allclose(X.mean(), 0.0, atol=1e-12)
assert np.allclose(X.std(ddof=0), 1.0, atol=1e-12)

model = sm.OLS(y, sm.add_constant(X)).fit()

# --- code cell 4 ---
print(f"Data directory: {DATA_DIR}")
print(f"Paper sample size: {len(sample_cities)}")
print(f"Zero-coded city-by-group cells: {len(zero_coded)}")
display(pd.DataFrame(zero_coded, columns=["city", "group"]))
display(grouped)

# --- code cell 5 ---
vif_table = pd.DataFrame({
    "predictor": X.columns,
    "VIF": [variance_inflation_factor(X.to_numpy(), i) for i in range(X.shape[1])],
})
print("Variance inflation factors")
display(vif_table.round(3))

# --- code cell 6 ---
expected_coefficients = [0.0, -0.3242, -0.3741, -0.3834, 0.0541, 0.1066, 0.1191, 0.1472, -0.4213, -0.3741, 0.0866, -0.1861, -0.2482]
expected_standard_errors = [0.135, 0.151, 0.17, 0.214, 0.197, 0.167, 0.158, 0.176, 0.174, 0.183, 0.177, 0.198, 0.167]
expected_pvalues = [1.0, 0.042, 0.038, 0.085, 0.786, 0.529, 0.459, 0.41, 0.023, 0.051, 0.63, 0.356, 0.151]
assert int(model.nobs) == 38
assert np.array_equal(np.round(np.asarray(model.params), 4), expected_coefficients)
assert np.array_equal(np.round(np.asarray(model.bse), 3), expected_standard_errors)
assert np.array_equal(np.round(np.asarray(model.pvalues), 3), expected_pvalues)
assert round(float(model.rsquared), 3) == 0.545
assert model.cov_type == "nonrobust"
print("Published Table 4 values reproduced at displayed precision.")
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
