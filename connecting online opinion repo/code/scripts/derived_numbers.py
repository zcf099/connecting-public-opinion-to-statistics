# Numbers cited in the WWW'27 draft that are not printed directly by the analysis notebook.
# Reads only saved results and the 38-city design file; writes derived/derived_numbers.txt and
# derived/admin_outcome_side_split.csv. Usage: python3 derived_numbers.py
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]
def resolve_confirmatory(root: Path) -> Path:
    c = root / 'results/www_short/confirmatory'
    if c.exists():
        return c
    runs = sorted((root / 'results/www_short').glob('confirmatory_*'))
    if not runs:
        raise FileNotFoundError('No confirmatory results folder found under results/www_short/')
    return runs[-1]
P = PROJECT / 'results/www_short'
R = resolve_confirmatory(PROJECT)
OUT = P / 'derived'
OUT.mkdir(exist_ok=True)
lines = []


def say(*a):
    s = ' '.join(str(x) for x in a)
    print(s)
    lines.append(s)


# ---------- 1. Urban-statistics side of RQ1: archived 11-indicator model of C, split on the outcome side
design = pd.read_csv(P / 'preprocessing/analysis_design_38_cities.csv').set_index('city')
ref = pd.read_csv(P / 'original/reference_models_6_outcomes.csv')
obj = ref[ref.branch.eq('objective_archived') & ref.term.ne('const')]
IND = obj[obj.outcome.eq('archived_composite')].term.tolist()          # the 11 archived predictors, archived order
C, S, N = (design[f'outcome__{k}'] for k in ['archived_composite', 'combined_group_share', 'normalized_composite'])
assert np.allclose(N, C / S)
X = np.column_stack([np.ones(len(C)), ((design[IND] - design[IND].mean()) / design[IND].std(ddof=0)).to_numpy()])
csd = C.std(ddof=0)
inter = (S - S.mean()) * (N - N.mean())
parts = {'C': C - C.mean(), 'U_share': N.mean() * (S - S.mean()), 'V_normalized': S.mean() * (N - N.mean()),
         'W_interaction': inter - inter.mean()}
split = pd.DataFrame({k: np.linalg.lstsq(X, (v / csd).to_numpy(), rcond=None)[0] for k, v in parts.items()},
                     index=['const'] + IND).drop(index='const')
archived = obj[obj.outcome.eq('archived_composite')].set_index('term')
assert np.allclose(split.C, archived.beta, atol=1e-10), 'C coefficients differ from the archived objective model'
assert np.allclose(split[['U_share', 'V_normalized', 'W_interaction']].sum(axis=1), split.C, atol=1e-10)
split['hc3_q_bh'] = archived.hc3_q_bh
split.to_csv(OUT / 'admin_outcome_side_split.csv', float_format='%.6f')
say('== 1. Archived urban-statistics model of C (R2 %.3f), outcome-side split' % archived.r_squared.iloc[0])
say(split.round(3).to_string())
say('\nAdjusted coefficients (HC3 q < .10) by outcome, urban-statistics model:')
for oc, g in obj.groupby('outcome', sort=False):
    hits = g[g.hc3_q_bh < .10]
    say(f'  {oc:22s} R2 {g.r_squared.iloc[0]:.3f}: ' + '; '.join(f'{t} {b:+.3f} (q {q:.3f})' for t, b, q in
                                                                zip(hits.term, hits.beta, hits.hc3_q_bh)))

# ---------- 2. Score-side 12-domain models: fit statistics and pairwise-D q values
ss = pd.read_csv(R / 'score_side_split.csv')
say('\n== 2. 12-domain models of C: R2 and adjusted R2 by design')
fit = ss[ss.outcome.eq('archived_composite')].groupby('design')[['r_squared', 'adjusted_r_squared']].first()
say(fit.round(3).to_string())
pw = ss[ss.outcome.str.startswith('d_') & ss.term.ne('const')]
say('Pairwise-D outcomes, smallest HC3 q by design:')
say(pw.groupby('design').hc3_q_bh.min().round(3).to_string())
say(f'Smallest HC3 q over all pairwise-D designs: {pw.hc3_q_bh.min():.3f}')

# ---------- 3. Single-domain grid: observed BH families with a hit vs permutation expectation
grid = pd.read_csv(R / 'single_domain_grid_864.csv')
foc = grid[grid.term.eq(grid.focal_domain)]
assert len(foc) == 864
fams = foc.groupby('family').hc3_q_bh.min()
hits = foc[foc.hc3_q_bh < .05]
say(f'\n== 3. Single-domain grid: {len(foc)} focal coefficients in {fams.size} families; '
    f'{len(hits)} pass BH in {(fams < .05).sum()} families')
say(hits[['outcome', 'focal_domain', 'signal', 'controls', 'beta', 'hc3_q_bh']].round(3).to_string(index=False))
perm = pd.read_csv(P / 'diagnostics/permutation_dry_run.csv')
say('Permutation expectation of families with >=1 BH hit (6 outcomes per row): '
    f'{6 * perm.bh12_any_min.sum():.2f} to {6 * perm.bh12_any_max.sum():.2f} of {fams.size}')

# ---------- 4. Public transportation: tone, composition, coverage across cities
sig = {k: pd.read_csv(P / f'measurement/signal_{k}.csv').set_index('city') for k in ['a', 'comp', 'tone', 'n']}
g = 'Public Transportation'
t = pd.DataFrame({k: v[g] for k, v in sig.items()}).dropna()
say(f'\n== 4. {g} across {len(t)} cities with a score')
say(f"r(a, comp) {t.a.corr(t.comp):.3f}; r(a, tone) {t.a.corr(t.tone):.3f}; r(tone, comp) {t.tone.corr(t.comp):.3f}; "
    f"r(comp, n) {t.comp.corr(t.n):.3f}; r(a, n) {t.a.corr(t.n):.3f}")
say(f"SD a {t.a.std(ddof=0):.3f}, SD comp {t.comp.std(ddof=0):.3f}, SD tone (uncorrected) {t.tone.std(ddof=0):.3f}")
base = pd.read_csv(P / 'measurement/keyword_baselines.csv')
cells = pd.read_csv(P / 'preprocessing/city_keyword_cells.csv')
size = pd.read_csv(P / 'preprocessing/corpus_size_proxy.csv').set_index('city').terms_in_dictionary
say(f'Median dictionary size, all 38 cities: {size.median():.0f}')
for kw in ['transit', 'transportation', 'commute', 'light rail', 'commuter rail']:
    b = base[(base.domain == g) & (base.keyword == kw)].iloc[0]
    cities = cells[(cells.domain == g) & (cells.keyword == kw)].city
    say(f'  {kw:15s} baseline {b.baseline_beta:+.3f}, retained in {int(b.cities)} cities, '
        f'median dictionary size there {size.loc[cities].median():.0f}')

# ---------- 5. RQ2: adjusted comparisons by signal and method
say('\n== 5. RQ2 partial correlations passing BH (q < .05), 132-test families')
for tag, f in [('main', 'rq2_partial_correlations.csv'), ('screened', 'screened_rq2_partial_correlations.csv')]:
    d = pd.read_csv(R / f)
    h = d[d.q_bh < .05]
    say(f'  {tag}: ' + ', '.join(f'{s} {m} {k}' for (s, m), k in h.groupby(['signal', 'method']).size().items())
        + f' (total {len(h)})')
    say(h[['signal', 'method', 'domain', 'indicator', 'partial_r', 'q_bh']].round(3).to_string(index=False))

(OUT / 'derived_numbers.txt').write_text('\n'.join(lines) + '\n')
print('\nwrote', OUT / 'derived_numbers.txt')
