# Figure 1: how a city's domain score is built from Web text, and why it mixes what is discussed with how it is evaluated.
# Top: the measurement pipeline. Bottom: two illustrative communities with the same tone, using the estimated
# public-transportation keyword baselines (results/www_short/measurement/keyword_baselines.csv).
# Usage: python3 make_fig_mechanism.py OUT.pdf   (also writes OUT.png)
import sys
from pathlib import Path
import pandas as pd
import matplotlib as mpl
mpl.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

PROJECT = Path(__file__).resolve().parents[2]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT / 'figures/fig_mechanism.pdf'
b = pd.read_csv(PROJECT / 'results/www_short/measurement/keyword_baselines.csv')
KW = ['transit', 'transportation', 'commute', 'light rail', 'commuter rail']   # descending baseline
base = b[b.domain.eq('Public Transportation')].set_index('keyword').baseline_beta.loc[KW]
kept = {'Smaller': KW[:3], 'Larger': KW}
comp = {k: base[v].mean() for k, v in kept.items()}
print('baselines', base.round(3).to_dict(), 'composition', {k: round(v, 3) for k, v in comp.items()},
      'gap', round(comp['Smaller'] - comp['Larger'], 3))


def num(v):
    """+.57 / −.06 style."""
    return f'{v:+.2f}'.replace('0.', '.').replace('-', '−')


mpl.rcParams.update({
    'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 7, 'axes.labelsize': 7, 'xtick.labelsize': 6.5, 'ytick.labelsize': 7,
    'pdf.fonttype': 42, 'axes.linewidth': 0.5,
})
INK, INK2, MUTED, GRID, SURF, FILL = '#0b0b0b', '#52514e', '#898781', '#e4e3df', '#ffffff', '#f3f2ee'
C_COMP = '#eb6834'          # composition, as in Figures 2 and 3

W, H = 3.33, 2.34
fig = plt.figure(figsize=(W, H))

# ---------------- top: pipeline (axes in inch units)
top_h = 0.58
axp = fig.add_axes([0, 1 - top_h / H, 1, top_h / H])
axp.set_xlim(0, W); axp.set_ylim(0, top_h); axp.axis('off')
boxes = [
    (0.62, "Comments in\neach city's\nsubreddit"),
    (0.78, 'Keyword mentions\nscored; a keyword\ncounts if >10'),
    (0.62, 'City × keyword\ntable of\nmean scores'),
    (0.90, 'Domain score =\ntone + composition;\ncoverage = # counted'),
]
gap, x, y0, bh = 0.115, 0.03, 0.04, 0.50
for i, (bw, txt) in enumerate(boxes):
    key = i in (1, 3)                       # the threshold and the split carry the argument
    axp.add_patch(FancyBboxPatch((x, y0), bw, bh, boxstyle='round,pad=0,rounding_size=0.05',
                                 fc=FILL, ec=INK2 if key else MUTED, lw=0.7 if key else 0.5))
    axp.text(x + bw / 2, y0 + bh / 2, txt, ha='center', va='center', fontsize=6.1, color=INK, linespacing=1.15)
    if i < len(boxes) - 1:
        axp.add_patch(FancyArrowPatch((x + bw + 0.012, y0 + bh / 2), (x + bw + gap - 0.012, y0 + bh / 2),
                                      arrowstyle='-|>', mutation_scale=6, lw=0.6, color=INK2))
    x += bw + gap

# ---------------- bottom: keyword baselines, kept sets, and composition
left, plot_w = 0.74, 1.62                     # inches
bot, plot_h = 0.30, 1.04
ax = fig.add_axes([left / W, bot / H, plot_w / W, plot_h / H])
y = list(range(len(KW)))[::-1]               # transit at top
for yi, k in zip(y, KW):
    ax.plot([0, base[k]], [yi, yi], color=GRID, lw=1.4, solid_capstyle='round', zorder=1)
ax.scatter(base.values, y, s=16, color=INK2, edgecolors=SURF, linewidths=0.6, zorder=3)
for name in ['Smaller', 'Larger']:
    ax.plot([comp[name]] * 2, [-0.45, len(KW) - 0.55], color=C_COMP, lw=1.3, zorder=2)
ax.axvline(0, color=MUTED, lw=0.5, ls=(0, (2, 2)), zorder=0)
ax.set_xlim(-1.32, 1.0); ax.set_ylim(-0.6, len(KW) - 0.4)
ax.set_xticks([-1, -0.5, 0, 0.5]); ax.set_xticklabels(['−1', '−.5', '0', '.5'], color=INK2)
ax.set_yticks(y); ax.set_yticklabels(KW, color=INK, fontfamily='Arial', fontstyle='italic')
ax.tick_params(axis='y', length=0, pad=3); ax.tick_params(axis='x', length=2, width=0.5, color=INK2)
for s in ['top', 'right', 'left']:
    ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color(INK2)
ax.set_xlabel('Keyword baseline (public transportation)', color=INK2, labelpad=2)
ytop = len(KW) - 0.42                         # composition labels sit above the lines, pointing away from each other
ax.text(comp['Larger'] - 0.04, ytop, 'larger\n' + num(comp['Larger']), ha='right', va='bottom',
        fontsize=6.1, color=INK, linespacing=1.1)
ax.text(comp['Smaller'] + 0.04, ytop, 'smaller\n' + num(comp['Smaller']), ha='left', va='bottom',
        fontsize=6.1, color=INK, linespacing=1.1)

# kept sets, one column per community (same rows as the keywords)
axr = fig.add_axes([(left + plot_w + 0.12) / W, bot / H, 0.78 / W, plot_h / H], sharey=ax)
axr.axis('off'); axr.set_xlim(0, 1)
for xi, name in zip([0.27, 0.75], ['Smaller', 'Larger']):
    for yi, k in zip(y, KW):
        on = k in kept[name]
        axr.scatter([xi], [yi], s=20, marker='o', color=INK2 if on else SURF,
                    edgecolors=INK2 if on else MUTED, linewidths=0.7, zorder=3)
    axr.text(xi, ytop, name.lower() + '\nkeeps', ha='center', va='bottom', fontsize=6.1, color=INK, linespacing=1.1)
    axr.text(xi, -0.62, f'{len(kept[name])}', ha='center', va='top', fontsize=6.1, color=INK2)
axr.text(0.27 - 0.13, -0.62, 'coverage', ha='right', va='top', fontsize=6.1, color=INK2)
fig.text(0.03 / W, (bot + plot_h + 0.255) / H,
         'Two communities with the same tone; orange lines mark their compositions',
         ha='left', va='bottom', fontsize=5.9, color=INK2)
fig.savefig(OUT)
fig.savefig(OUT.with_suffix('.png'), dpi=300)
print('wrote', OUT)
