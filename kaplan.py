import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl
import seaborn as sns
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

# --- styling ---
def setup_plot_style():
    """Set up publication-style plotting parameters"""
    sns.set(style='whitegrid')
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    arial_font = next((f for f in ['Arial', 'DejaVu Sans', 'Liberation Sans']
                      if f in available_fonts), 'sans-serif')
    mpl.rcParams.update({
        "font.family": arial_font,
        "font.size": 16,
        "axes.titlesize": 20,
        "axes.labelsize": 18,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
        "legend.fontsize": 16,
        "axes.linewidth": 0.8,
        "axes.edgecolor": "black",
        "axes.facecolor": "white",
        "axes.axisbelow": True,
        "axes.grid": True,
        "grid.color": "gray",
        "grid.linestyle": "-",
        "grid.linewidth": 0.3,
        "grid.alpha": 0.3,
        "figure.facecolor": "white",
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "mathtext.fontset": "cm",
    })

# --- label + color maps ---
RAW_TO_DISPLAY = {
    "repurposed": "Repurposed",
    "unchanged": "Listed but not repurposed",
}

COLOR_MAP = {
    "Repurposed": "#d8b365",
    "Listed but not repurposed": "#5ab4ac",
}

# --- helpers for lifelines version differences ---
def _survival_at_time(kmf: KaplanMeierFitter, t: float) -> float:
    try:
        return float(kmf.survival_function_at_times(t))
    except AttributeError:
        sf = kmf.survival_function_
        col = sf.columns[0]
        val = sf.reindex(sf.index.union([t])).sort_index().ffill().loc[t, col]
        return float(val)

def _ci_at_time(kmf: KaplanMeierFitter, t: float):
    try:
        ci = kmf.confidence_interval_at_times(t).iloc[0]
        return float(ci.min()), float(ci.max())
    except AttributeError:
        ci_df = getattr(kmf, "confidence_interval_", None)
        if ci_df is None:
            ci_df = getattr(kmf, "confidence_interval_survival_function_", None)
        if ci_df is None:
            return None, None
        row = ci_df.reindex(ci_df.index.union([t])).sort_index().ffill().loc[t]
        return float(row.min()), float(row.max())

# --- plotting ---
def plot_km_from_df(df, group_col="group", save_path='./output/kaplan.png', show=True):
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(8, 6))

    # map raw groups to display labels
    df = df.copy()
    df[group_col] = df[group_col].astype(str).str.lower().map(RAW_TO_DISPLAY).fillna(df[group_col])

    groups = [g for g in ["Repurposed", "Listed but not repurposed"]
              if g in set(df[group_col].dropna())]
    if not groups:  # fallback
        groups = list(df[group_col].dropna().unique())

    kmf_by_group = {}

    for g in groups:
        sub = df.loc[df[group_col] == g]
        label = f"{g} (n={len(sub)})"
        kmf = KaplanMeierFitter(label=label)
        kmf.fit(durations=sub["duration"], event_observed=sub["event"])
        color = COLOR_MAP.get(g, None)
        kmf.plot_survival_function(ax=ax, ci_show=True, color=color)
        kmf_by_group[g] = kmf

    if len(groups) == 2:
        d1, d2 = df[df[group_col] == groups[0]], df[df[group_col] == groups[1]]
        res = logrank_test(d1["duration"], d2["duration"], d1["event"], d2["event"])
        ax.text(0.03, 0.03, f"Log-rank p = {res.p_value:.4g}",
                transform=ax.transAxes,
                fontsize=16,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    ax.set_title("")
    ax.set_xlabel("Duration (Days)")
    ax.set_ylabel("Survival Probability")
    ax.legend(loc="upper right")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    return ax, kmf_by_group

# --- external benchmark annotation ---
def annotate_km_benchmark(ax, kmf_by_group, t=90, surv=0.967,
                          label="Empirical Suspensions @90days"):
    ax.axvline(t, linestyle="--", alpha=0.4)
    ax.axhline(surv, linestyle="--", alpha=0.4)
    ax.text(t, surv, f"  {label}", va="center", ha="left", fontsize=16)

    for g, kmf in kmf_by_group.items():
        s_hat = _survival_at_time(kmf, t)
        lo, hi = _ci_at_time(kmf, t)
        ax.plot([t], [s_hat], marker="o", ms=6,
                color=COLOR_MAP.get(g.replace(" (n=", "").split()[0], None))
        ax.text(t, s_hat, f"  {g.split(' (n=')[0]}: {s_hat:.3f}",
                va="center", fontsize=16)
        if lo is not None and hi is not None:
            print(f"{g}: Ŝ({t})={s_hat:.3f} [{lo:.3f}, {hi:.3f}] vs {surv:.3f}")
        else:
            print(f"{g}: Ŝ({t})={s_hat:.3f} (CI unavailable) vs {surv:.3f}")

# --- example usage ---
kaplan_df = pd.read_parquet('./data/kaplan_data.parquet')
ax, kmfits = plot_km_from_df(kaplan_df, group_col="group", show=False)
annotate_km_benchmark(ax, kmfits, t=90, surv=0.967)
plt.tight_layout(); plt.show()
