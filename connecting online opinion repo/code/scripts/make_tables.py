# Table bodies for the WWW'27 draft, generated from the confirmatory run so no number is typed by hand.
from pathlib import Path
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
ORDER = ['Public Transportation', 'Driving and Traffic', 'Economy and Income', 'Education', 'Culture and Art',
         'Race/Immigration Discourse', 'Recreation', 'Social Problem', 'Governing', 'Policing', 'Neighborhood',
         'City Development']
SHORT = {'Public Transportation': 'Public transportation', 'Driving and Traffic': 'Driving/traffic',
         'Economy and Income': 'Economy/income', 'Education': 'Education', 'Culture and Art': 'Culture/art',
         'Race/Immigration Discourse': 'Race/immigration', 'Recreation': 'Recreation',
         'Social Problem': 'Social problems', 'Governing': 'Governing', 'Policing': 'Policing',
         'Neighborhood': 'Neighborhood', 'City Development': 'City development'}


def f(x, nd=2):
    """APA-style: no leading zero, explicit minus."""
    s = f'{x:.{nd}f}'
    neg = s.startswith('-')
    s = s.lstrip('-')
    if s.startswith('0.'):
        s = s[1:]
    if neg and s.strip('0.') == '':
        neg = False
    return ('$-$' if neg else '') + s


out = []
# ---------------- Table 1
rel = pd.read_csv(P / 'measurement/reliability_and_variance_shares.csv').set_index('domain')
cov = pd.read_csv(P / 'diagnostics/coverage_size_and_vif.csv').set_index('domain')
re_ = pd.read_csv(P / 'measurement/random_effects_variance_components.csv').set_index('domain')
out.append('% Table 1 body')
for g in ORDER:
    r = rel.loc[g]
    med = r.keywords_per_city_median
    med = f'{med:.0f}' if med == int(med) else f'{med:.1f}'
    out.append(f"{SHORT[g]} & {int(r.keywords)} & {int(r.cities)} & {med} & {f(r.sd_score)} & {f(r.sd_comp)} & "
               f"{f(r.sd_tone_corrected)} & {f(r.reliability_tone)} & {f(re_.loc[g].p_boundary)} & {f(cov.loc[g].r_n_log_s)} \\\\")

# ---------------- Table 2
two = pd.read_csv(R / 'two_sided_decomposition_C.csv').set_index('domain')
re2 = pd.read_csv(R / 'score_side_split_RE_tone.csv')
re2 = re2[(re2.outcome == 'archived_composite') & (re2.term != 'const')].set_index('term').beta
scr = pd.read_csv(R / 'screened_score_side_split.csv')
scr = scr[(scr.outcome == 'archived_composite') & (scr.term != 'const')].pivot(index='term', columns='design', values='beta')
main = pd.read_csv(R / 'score_side_split.csv')
mq = main[(main.outcome == 'archived_composite') & (main.term != 'const')]
out.append('% Table 2 body')
for g in ORDER:
    t = two.loc[g]
    out.append(f"{SHORT[g]} & {f(t['score_side_a_zero_fill (original)'], 3)} & {f(t.outcome_side_U_share, 3)} & "
               f"{f(t.score_side_a_mean_fill, 3)} & {f(t.score_side_composition_mean_fill, 3)} & {f(t.score_side_tone_mean_fill, 3)} & "
               f"{f(re2[g], 3)} & {f(scr.loc[g, 'a_mean_fill'], 3)} & {f(scr.loc[g, 'composition_mean_fill'], 3)} & "
               f"{f(scr.loc[g, 'tone_mean_fill'], 3)} \\\\")
out.append(f"% min HC3 q, C models, main: {mq.hc3_q_bh.min():.3f}; screened: "
           f"{pd.read_csv(R / 'screened_score_side_split.csv').query('outcome==\"archived_composite\"').hc3_q_bh.min():.3f}; RE: "
           f"{pd.read_csv(R / 'score_side_split_RE_tone.csv').query('outcome==\"archived_composite\"').hc3_q_bh.min():.3f}")
r2 = main[main.outcome == 'archived_composite'].groupby('design').r_squared.first()
out.append('% R2 main: ' + ', '.join(f'{k} {v:.3f}' for k, v in r2.items()))

# ---------------- Table 3
m = pd.read_csv(R / 'rq2_partial_correlations.csv')
s = pd.read_csv(R / 'screened_rq2_partial_correlations.csv')
e = pd.read_csv(R / 'rq2_exploratory_transport.csv')
IND = ['commute_%drive', 'Walking Score', 'Driving Score']
EXP = ['Transit Score', 'commute_%public transit']


def cell(df, dom, sig, ind, meth='pearson'):
    r = df[(df.domain == dom) & (df.signal == sig) & (df.method == meth) & (df.indicator == ind)].iloc[0]
    v = f(r.partial_r)
    return (f'\\textbf{{{v}}}' if r.q_bh < .05 else v), r.q_bh


out.append('% Table 3 body (Pearson partial r | log s, log pop; bold q<.05 within family)')
for dom, sig, lab in [('Driving and Traffic', 'n', 'Driving/traffic coverage'), ('Driving and Traffic', 'tone', 'Driving/traffic tone'),
                      ('Public Transportation', 'n', 'Public transp.\\ coverage'), ('Public Transportation', 'tone', 'Public transp.\\ tone')]:
    a = [cell(m, dom, sig, i) for i in IND]
    b = [cell(e, dom, sig, i) for i in EXP]
    out.append(f"{lab} & " + ' & '.join(x[0] for x in a) + ' & ' + ' & '.join(x[0] for x in b) + ' \\\\'
               + '   % q: ' + ', '.join(f'{x[1]:.3f}' for x in a + b))
for dom, sig, lab in [('Driving and Traffic', 'n', 'Driving/traffic coverage'), ('Driving and Traffic', 'tone', 'Driving/traffic tone')]:
    a = [cell(s, dom, sig, i) for i in IND]
    out.append(f"\\quad screened: {lab.split()[1]} & " + ' & '.join(x[0] for x in a) + ' & -- & -- \\\\   % q: '
               + ', '.join(f'{x[1]:.3f}' for x in a))
for dom, sig, lab in [('Driving and Traffic', 'n', 'Driving/traffic coverage, Spearman')]:
    a = [cell(m, dom, sig, i, 'spearman') for i in IND]
    b = [cell(e, dom, sig, i, 'spearman') for i in EXP]
    out.append(f"% {lab}: " + ' & '.join(x[0] for x in a + b) + '   q: ' + ', '.join(f'{x[1]:.3f}' for x in a + b))
print('\n'.join(out))
