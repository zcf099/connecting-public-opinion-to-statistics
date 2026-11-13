# Figure 1: city-to-city SD of the archived score, its keyword composition, and its tone (noise-corrected), by domain.
# Data: results/www_short/measurement/reliability_and_variance_shares.csv (all 145 keywords; main analysis).
import sys
from pathlib import Path
import pandas as pd
import matplotlib as mpl
mpl.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

PROJECT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT / 'figures/fig_sd_by_domain.pdf'
d = pd.read_csv(PROJECT / 'results/www_short/measurement/reliability_and_variance_shares.csv')

short = {
    'Public Transportation': 'Public transportation', 'Driving and Traffic': 'Driving/traffic',
    'Economy and Income': 'Economy/income', 'Education': 'Education', 'Culture and Art': 'Culture/art',
    'Race/Immigration Discourse': 'Race/immigration', 'Recreation': 'Recreation', 'Social Problem': 'Social problems',
    'Governing': 'Governing', 'Policing': 'Policing', 'Neighborhood': 'Neighborhood', 'City Development': 'City development',
}
d['label'] = d['domain'].map(short)
d = d.sort_values('sd_score').reset_index(drop=True)   # largest at top

mpl.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 7, 'axes.labelsize': 7, 'xtick.labelsize': 6.5, 'ytick.labelsize': 7,
    'pdf.fonttype': 42, 'axes.linewidth': 0.5,
})
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#e4e3df', '#ffffff'
C_SCORE, C_COMP, C_TONE = '#2a78d6', '#eb6834', '#1baf7a'   # validated categorical slots 1-3 (light, all pairs)

fig, ax = plt.subplots(figsize=(3.33, 2.6))
y = range(len(d))
for i, r in d.iterrows():
    lo, hi = min(r.sd_tone_corrected, r.sd_comp, r.sd_score), max(r.sd_tone_corrected, r.sd_comp, r.sd_score)
    ax.plot([lo, hi], [i, i], color=GRID, lw=1.6, zorder=1, solid_capstyle='round')
kw = dict(s=26, linewidths=0.9, edgecolors=SURF, zorder=3)
ax.scatter(d.sd_tone_corrected, y, marker='^', color=C_TONE, **kw)
ax.scatter(d.sd_comp, y, marker='s', color=C_COMP, s=22, linewidths=0.9, edgecolors=SURF, zorder=4)
ax.scatter(d.sd_score, y, marker='o', facecolors='none', edgecolors=C_SCORE, s=34, linewidths=1.1, zorder=5)

ax.set_yticks(list(y))
ax.set_yticklabels(d.label, color=INK)
ax.set_xlim(-0.005, 0.38)
ax.set_xticks([0, 0.1, 0.2, 0.3])
ax.set_xticklabels(['0', '.10', '.20', '.30'], color=INK2)
ax.set_xlabel('Standard deviation across cities', color=INK2)
ax.tick_params(axis='y', length=0, pad=3)
ax.tick_params(axis='x', length=2, width=0.5, color=INK2)
for s in ['top', 'right', 'left']:
    ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(INK2)
ax.xaxis.grid(True, color=GRID, lw=0.5, zorder=0)
ax.set_axisbelow(True)
ax.set_ylim(-0.6, len(d) - 0.4)

handles = [
    Line2D([], [], marker='o', ls='none', mfc='none', mec=C_SCORE, mew=1.1, ms=5.5, label='Archived score'),
    Line2D([], [], marker='s', ls='none', color=C_COMP, mec=SURF, ms=5, label='Composition'),
    Line2D([], [], marker='^', ls='none', color=C_TONE, mec=SURF, ms=5.5, label='Tone (noise-corrected)'),
]
fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=6.3,
           handletextpad=0.2, columnspacing=1.0, borderaxespad=0.15)
fig.tight_layout(pad=0.25, rect=(0, 0, 1, 0.93))
fig.savefig(OUT)
fig.savefig(OUT.with_suffix('.png'), dpi=300)
print('wrote', OUT)
