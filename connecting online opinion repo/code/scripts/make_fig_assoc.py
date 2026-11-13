# Figure 3 (replaces the RQ1 and RQ2 tables): (a) 12-domain models of the composite C for the two transport domains and
# social problems: archived score coefficient with its group-share part U, and the composition and tone coefficients;
# (b) partial correlations of coverage and tone with commuting and job-access indicators. Filled markers: BH q < .05
# within the family. Data: results/www_short/confirmatory/ (main analysis, all 145 keywords).
# Usage: python3 make_fig_assoc.py OUT.pdf   (also writes OUT.png)
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

PROJECT = Path(__file__).resolve().parents[2]
def resolve_confirmatory(root: Path) -> Path:
    c = root / 'results/www_short/confirmatory'
    if c.exists():
        return c
    runs = sorted((root / 'results/www_short').glob('confirmatory_*'))
    if not runs:
        raise FileNotFoundError('No confirmatory results folder found under results/www_short/')
    return runs[-1]
R = resolve_confirmatory(PROJECT)
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT / 'figures/fig_assoc.pdf'

mpl.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 7, 'axes.labelsize': 7, 'xtick.labelsize': 6.5, 'ytick.labelsize': 7,
    'pdf.fonttype': 42, 'axes.linewidth': 0.5,
})
INK, INK2, MUTED, GRID, SURF = '#0b0b0b', '#52514e', '#898781', '#e4e3df', '#ffffff'
C_SCORE, C_COMP, C_TONE, C_COV = '#2a78d6', '#eb6834', '#1baf7a', INK2   # as in Figure 2; coverage in ink
MK = {'score': 'o', 'comp': 's', 'tone': '^', 'cov': 'D'}
SZ = {'score': 4.6, 'comp': 4.0, 'tone': 4.6, 'cov': 3.6}


def point(ax, x, y, lo, hi, kind, color, filled):
    ax.plot([lo, hi], [y, y], color=color, lw=0.9, solid_capstyle='butt', zorder=2)
    ax.plot([x], [y], marker=MK[kind], ms=SZ[kind], mec=color, mew=0.9, mfc=color if filled else SURF,
            ls='none', zorder=3)


def style(ax, xlim, xticks, xlabel):
    ax.set_xlim(*xlim)
    ax.set_xticks(xticks)
    ax.set_xticklabels([('−' if t < 0 else '') + (f'{abs(t):g}'.lstrip('0') or '0') for t in xticks], color=INK2)
    ax.axvline(0, color=MUTED, lw=0.5, ls=(0, (2, 2)), zorder=0)
    ax.xaxis.grid(True, color=GRID, lw=0.5, zorder=0); ax.set_axisbelow(True)
    ax.tick_params(axis='y', length=0, pad=3); ax.tick_params(axis='x', length=2, width=0.5, color=INK2)
    for s in ['top', 'right', 'left']:
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(INK2)
    ax.set_xlabel(xlabel, color=INK2, labelpad=2)


# ---------------- data, panel (a)
DOM = [('Public Transportation', 'Public transportation'), ('Driving and Traffic', 'Driving/traffic'),
       ('Social Problem', 'Social problems')]
ss = pd.read_csv(R / 'score_side_split.csv')
ss = ss[ss.outcome.eq('archived_composite') & ss.term.ne('const')].set_index(['design', 'term'])
U = pd.read_csv(R / 'two_sided_decomposition_C.csv').set_index('domain').outcome_side_U_share
DES = {'score': 'a_zero_fill (original)', 'comp': 'composition_mean_fill', 'tone': 'tone_mean_fill'}

# ---------------- data, panel (b)
rq = pd.concat([pd.read_csv(R / 'rq2_partial_correlations.csv'), pd.read_csv(R / 'rq2_exploratory_transport.csv')])
rq = rq[rq.method.eq('pearson')].set_index(['domain', 'indicator', 'signal'])
IND = {'commute_%drive': 'Drive share', 'Walking Score': 'Walking access to jobs', 'Transit Score': 'Transit Score†',
       'commute_%public transit': 'Transit share†'}
ROWS = [('Driving and Traffic', 'Driving/traffic', ['commute_%drive', 'Walking Score', 'Transit Score',
                                                     'commute_%public transit']),
        ('Economy and Income', 'Economy/income', ['commute_%drive', 'Walking Score']),
        ('Governing', 'Governing', ['commute_%drive', 'Walking Score'])]


def fisher_ci(r, n, k=2):
    z, se = np.arctanh(r), 1 / np.sqrt(n - 3 - k)
    return np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)


# ---------------- layout (inches)
W, H = 3.33, 3.36
left, pw = 1.07, 2.16             # left margin fits the longest row label, 'Walking access to jobs'
fig = plt.figure(figsize=(W, H))
ax_a = fig.add_axes([left / W, 2.06 / H, pw / W, 0.84 / H])
ax_b = fig.add_axes([left / W, 0.30 / H, pw / W, 1.36 / H])

# panel (a)
log = []
for g, (dom, lab) in enumerate(DOM):
    yc = len(DOM) - 1 - g
    for kind, dy, col in [('score', 0.28, C_SCORE), ('comp', 0.0, C_COMP), ('tone', -0.28, C_TONE)]:
        r = ss.loc[(DES[kind], dom)]
        point(ax_a, r.beta, yc + dy, r.hc3_ci_low, r.hc3_ci_high, kind, col, r.hc3_q_bh < .05)
        log.append(f'a {lab:22s} {kind:5s} {r.beta:+.3f} [{r.hc3_ci_low:+.3f}, {r.hc3_ci_high:+.3f}] q {r.hc3_q_bh:.3f}')
    ax_a.plot([U[dom]], [yc + 0.28], marker='|', ms=7, mew=1.1, color=INK, ls='none', zorder=4)
    log.append(f'a {lab:22s} U     {U[dom]:+.3f}')
ax_a.set_yticks(range(len(DOM))); ax_a.set_yticklabels([lab for _, lab in DOM][::-1], color=INK)
ax_a.set_ylim(-0.55, len(DOM) - 0.45)
style(ax_a, (-1.4, 1.1), [-1, -0.5, 0, 0.5, 1], 'Standardized coefficient (HC3 95% interval)')
ax_a.set_title('a   RQ1: 12-domain models of the composite C', loc='left', fontsize=6.6, color=INK, pad=3,
               x=-left / pw + 0.01)

# panel (b)
y, ticks, labels, bold = 0, [], [], []
ypos = {}
for dom, lab, inds in ROWS[::-1]:
    for ind in inds[::-1]:
        ypos[(dom, ind)] = y; ticks.append(y); labels.append(IND[ind]); bold.append(False); y += 1
    ticks.append(y - 0.15); labels.append(lab); bold.append(True); y += 1.0
for (dom, ind), yy in ypos.items():
    for sig, dy, col, kind in [('n', 0.17, C_COV, 'cov'), ('tone', -0.17, C_TONE, 'tone')]:
        r = rq.loc[(dom, ind, sig)]
        lo, hi = fisher_ci(r.partial_r, r.n)
        point(ax_b, r.partial_r, yy + dy, lo, hi, kind, col, r.q_bh < .05)
        log.append(f'b {dom:20s} {IND[ind]:15s} {sig:4s} r {r.partial_r:+.3f} [{lo:+.2f}, {hi:+.2f}] n {r.n} q {r.q_bh:.3f}')
ax_b.set_yticks(ticks); ax_b.set_yticklabels(labels, color=INK)
for t, bb in zip(ax_b.get_yticklabels(), bold):
    if bb:
        t.set_fontfamily('Arial'); t.set_fontweight('bold')
ax_b.set_ylim(-0.6, y - 0.6)
style(ax_b, (-1, 1), [-1, -0.5, 0, 0.5, 1], 'Partial correlation (95% interval)')
ax_b.set_title('b   RQ2: correlations with urban indicators', loc='left', fontsize=6.6, color=INK, pad=3,
               x=-left / pw + 0.01)

handles = [
    Line2D([], [], marker='o', ls='none', ms=SZ['score'], mfc=SURF, mec=C_SCORE, mew=0.9, label='Archived score'),
    Line2D([], [], marker='|', ls='none', ms=7, mew=1.1, color=INK, label='U: group-share part'),
    Line2D([], [], marker='s', ls='none', ms=SZ['comp'], mfc=SURF, mec=C_COMP, mew=0.9, label='Composition'),
    Line2D([], [], marker='^', ls='none', ms=SZ['tone'], mfc=SURF, mec=C_TONE, mew=0.9, label='Tone'),
    Line2D([], [], marker='D', ls='none', ms=SZ['cov'], mfc=SURF, mec=C_COV, mew=0.9, label='Coverage'),
    Line2D([], [], marker='D', ls='none', ms=SZ['cov'], mfc=C_COV, mec=C_COV, mew=0.9, label='Filled: q < .05'),
]
fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.01, 0.995), ncol=3, frameon=False, fontsize=6.2,
           handletextpad=0.3, columnspacing=0.9, borderaxespad=0.1, labelspacing=0.35)
fig.savefig(OUT)
fig.savefig(OUT.with_suffix('.png'), dpi=300)
print('\n'.join(log))
print('wrote', OUT)
