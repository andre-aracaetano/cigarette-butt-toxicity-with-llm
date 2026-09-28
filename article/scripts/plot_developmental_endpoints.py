"""Publication figures for zebrafish developmental endpoints.

Raw treatment codes are retained in the source workbook. Display labels use SCB
for BCT and SCF for BST. Every significance symbol is generated from a stored
comparison against the shared control; no annotation is typed manually.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import fisher_exact, kruskal, rankdata
from scipy.special import ndtr
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.proportion import proportion_confint


def article_root() -> Path:
    here = Path.cwd().resolve()
    candidates = [here, here.parent, here / "article"]
    for candidate in candidates:
        if (candidate / "data" / "processed" / "zebrafish_endpoints.xlsx").exists():
            return candidate
    raise FileNotFoundError("Run from the repository root, article/, or article/notebooks/.")


ROOT = article_root()
DATA = ROOT / "data" / "processed" / "zebrafish_endpoints.xlsx"
FIGURES = ROOT / "results" / "figures"
TABLES = ROOT / "data" / "processed"
for folder in (FIGURES, TABLES):
    folder.mkdir(parents=True, exist_ok=True)

CONTROL = "Control"
ORDER = [CONTROL, "SCB 0.5", "SCB 1.0", "SCB 2.0", "SCF 0.5", "SCF 1.0", "SCF 2.0"]
COLORS = {CONTROL: "#7F7F7F", "SCB": "#2C7FB8", "SCF": "#D95F0E"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.labelsize": 13,
    "axes.titlesize": 13, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})


def clean_data() -> pd.DataFrame:
    df = pd.read_excel(DATA)
    df["treatment_raw"] = df["type"]
    df["treatment"] = df["type"].replace({"BCT": "SCB", "BST": "SCF", "control": CONTROL})
    df["group"] = np.where(
        df["concentration"].eq(0), CONTROL,
        df["treatment"] + " " + df["concentration"].map(lambda x: f"{float(x):.1f}"),
    )
    df["pigmented_area_normalized"] = df["pigmented_area"] / df["body_length"]
    return df[df["group"].isin(ORDER)].copy()


def holm_adjust(pvalues):
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty_like(p)
    running = 0.0
    m = len(p)
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adjusted[idx] = min(running, 1.0)
    return adjusted


def symbol(p):
    return "****" if p < 0.0001 else "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"


def dunn_vs_control(df, value, family):
    work = df[["group", value]].dropna()
    groups = [g for g in ORDER if g in set(work["group"])]
    arrays = [work.loc[work["group"].eq(g), value].to_numpy() for g in groups]
    h, omnibus_p = kruskal(*arrays)
    ranks = rankdata(work[value].to_numpy())
    work = work.assign(_rank=ranks)
    n = len(work)
    _, tie_counts = np.unique(work[value], return_counts=True)
    tie_correction = 1 - np.sum(tie_counts**3 - tie_counts) / (n**3 - n)
    variance = n * (n + 1) / 12 * tie_correction
    control = work.loc[work["group"].eq(CONTROL), "_rank"]
    raw = []
    rows = []
    for group in groups:
        if group == CONTROL:
            continue
        exposed = work.loc[work["group"].eq(group), "_rank"]
        z = (exposed.mean() - control.mean()) / np.sqrt(variance * (1 / len(exposed) + 1 / len(control)))
        p = 2 * ndtr(-abs(z))
        raw.append(p)
        rows.append({"figure": family, "endpoint": value, "test": "Kruskal-Wallis + Dunn-Bonferroni",
                     "omnibus_p": omnibus_p, "comparison": f"{group} vs Control", "p_raw": p})
    adjusted = np.minimum(np.asarray(raw) * len(raw), 1.0)
    for row, p_adj in zip(rows, adjusted):
        row["p_adjusted"] = p_adj
        row["symbol"] = symbol(p_adj)
    return pd.DataFrame(rows)


def tukey_vs_control(df, value, family):
    work = df[["group", value]].dropna()
    fit = pairwise_tukeyhsd(work[value], work["group"], alpha=0.05)
    rows = []
    for result in fit._results_table.data[1:]:
        g1, g2, difference, p_adj, lower, upper, reject = result
        if CONTROL not in (g1, g2):
            continue
        exposed = g2 if g1 == CONTROL else g1
        rows.append({"figure": family, "endpoint": value, "test": "One-way ANOVA + Tukey HSD",
                     "omnibus_p": np.nan, "comparison": f"{exposed} vs Control", "p_raw": np.nan,
                     "p_adjusted": float(p_adj), "symbol": symbol(float(p_adj))})
    return pd.DataFrame(rows)


def fisher_vs_control(df, value, family):
    work = df[["group", value]].dropna().copy()
    work["positive"] = work[value].astype(str).str.strip().str.lower().eq("yes")
    control = work.loc[work["group"].eq(CONTROL), "positive"]
    raw, rows = [], []
    for group in ORDER[1:]:
        exposed = work.loc[work["group"].eq(group), "positive"]
        table = [[int(exposed.sum()), int((~exposed).sum())], [int(control.sum()), int((~control).sum())]]
        odds, p = fisher_exact(table, alternative="two-sided")
        raw.append(p)
        rows.append({"figure": family, "endpoint": value, "test": "Fisher exact + Holm",
                     "omnibus_p": np.nan, "comparison": f"{group} vs Control", "p_raw": p,
                     "exposed_positive": table[0][0], "exposed_total": int(len(exposed)),
                     "control_positive": table[1][0], "control_total": int(len(control))})
    adjusted = holm_adjust(raw)
    for row, p_adj in zip(rows, adjusted):
        row["p_adjusted"] = p_adj
        row["symbol"] = symbol(p_adj)
    return pd.DataFrame(rows)


def save(fig, name):
    for folder in (FIGURES,):
        fig.savefig(folder / f"{name}.pdf", bbox_inches="tight")
        fig.savefig(folder / f"{name}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def group_color(group):
    return COLORS[CONTROL] if group == CONTROL else COLORS[group.split()[0]]


def add_stars(ax, stats, heights, offset):
    lookup = {row.comparison.split(" vs ")[0]: row.symbol for row in stats.itertuples()}
    for i, group in enumerate(ORDER):
        mark = lookup.get(group, "")
        if mark and mark != "ns":
            ax.text(i, heights[group] + offset, mark, ha="center", va="bottom", fontsize=11)


def continuous_boxplot(df, value, ylabel, name, stats):
    values = [df.loc[df["group"].eq(g), value].dropna().to_numpy() for g in ORDER]
    fig, ax = plt.subplots(figsize=(7.2, 4.1))
    boxes = ax.boxplot(values, positions=np.arange(len(ORDER)), widths=0.58, patch_artist=True,
                       showfliers=False, medianprops={"color": "black", "linewidth": 1.2},
                       whiskerprops={"linewidth": 0.9}, capprops={"linewidth": 0.9})
    rng = np.random.default_rng(20260823)
    for i, (group, vals, box) in enumerate(zip(ORDER, values, boxes["boxes"])):
        box.set(facecolor=group_color(group), edgecolor="black", alpha=0.82)
        ax.scatter(rng.normal(i, 0.055, len(vals)), vals, s=11, color="black", alpha=0.52, linewidth=0, zorder=3)
    ax.set_xticks(range(len(ORDER)), ORDER, rotation=35, ha="right")
    ax.set_xlabel("Treatment (CB/L)")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.3)
    span = max(df[value]) - min(df[value])
    heights = {g: max(v) if len(v) else np.nan for g, v in zip(ORDER, values)}
    add_stars(ax, stats, heights, max(span * 0.035, 0.01))
    ax.margins(y=0.16)
    fig.tight_layout()
    save(fig, name)


def binary_panels(df, endpoints, stats):
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.8), sharey=True)
    for panel, (ax, (value, title)) in enumerate(zip(axes, endpoints.items())):
        positives, totals, rates, low, high = [], [], [], [], []
        for group in ORDER:
            x = df.loc[df["group"].eq(group), value].dropna().astype(str).str.lower().eq("yes")
            k, n = int(x.sum()), len(x)
            lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
            positives.append(k); totals.append(n); rates.append(k / n); low.append(lo); high.append(hi)
        x = np.arange(len(ORDER))
        ax.bar(x, np.array(rates) * 100, color=[group_color(g) for g in ORDER],
               edgecolor="black", linewidth=0.7, width=0.68)
        ax.errorbar(x, np.array(rates) * 100,
                    yerr=[np.maximum((np.array(rates) - np.array(low)) * 100, 0),
                          np.maximum((np.array(high) - np.array(rates)) * 100, 0)],
                    fmt="none", ecolor="black", elinewidth=0.8, capsize=2.5)
        ax.set_title(title)
        ax.set_xticks(x, ORDER, rotation=45, ha="right")
        ax.set_xlabel("Treatment (CB/L)")
        ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.3)
        ax.text(-0.15, 1.05, f"({chr(97 + panel)})", transform=ax.transAxes, fontweight="bold", fontsize=11)
        subset = stats.loc[stats["endpoint"].eq(value)]
        heights = {g: hi_i * 100 for g, hi_i in zip(ORDER, high)}
        add_stars(ax, subset, heights, 3)
    axes[0].set_ylabel("Larvae with endpoint (%)")
    axes[0].set_ylim(0, 118)
    fig.tight_layout()
    save(fig, "developmental_abnormalities")


def main():
    df = clean_data()
    stats_body = dunn_vs_control(df, "body_length", "body_length")
    stats_yolk = dunn_vs_control(df, "yolk_sac_area", "yolk_sac_area")
    stats_heart = tukey_vs_control(df, "bpm", "heart_rate")
    stats_pigment = dunn_vs_control(df, "pigmented_area_normalized", "pigmented_area_normalized")
    binary_endpoints = {
        "open_swim_bladder": "Swim bladder inflation",
        "edema_present": "Edema",
        "deformation_present": "Deformation",
    }
    stats_binary = pd.concat([fisher_vs_control(df, endpoint, "developmental_abnormalities")
                              for endpoint in binary_endpoints], ignore_index=True)
    all_stats = pd.concat([stats_body, stats_yolk, stats_binary, stats_heart, stats_pigment], ignore_index=True)
    all_stats.to_csv(TABLES / "developmental_endpoint_statistics.csv", index=False)
    df[["group", "body_length", "yolk_sac_area", "bpm", "pigmented_area_normalized",
        "open_swim_bladder", "edema_present", "deformation_present"]].to_csv(
            TABLES / "developmental_endpoint_plot_data.csv", index=False)
    binary_rows = []
    for endpoint in binary_endpoints:
        for group in ORDER:
            values = df.loc[df["group"].eq(group), endpoint].dropna().astype(str).str.lower().eq("yes")
            k, n = int(values.sum()), len(values)
            lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
            binary_rows.append({"endpoint": endpoint, "group": group, "positive": k, "total": n,
                                "percent": 100 * k / n, "ci_low": 100 * lo, "ci_high": 100 * hi})
    pd.DataFrame(binary_rows).to_csv(TABLES / "developmental_binary_summary.csv", index=False)

    continuous_boxplot(df, "body_length", "Body length (mm)", "body_length", stats_body)
    continuous_boxplot(df, "yolk_sac_area", "Yolk sac area (mm²)", "yolk_sac_area", stats_yolk)
    binary_panels(df, binary_endpoints, stats_binary)
    continuous_boxplot(df, "bpm", "Heart rate (beats/min)", "heart_rate", stats_heart)
    continuous_boxplot(df, "pigmented_area_normalized", "Normalized pigmented area (µm²/mm)",
                       "pigmented_area_normalized", stats_pigment)
    print(all_stats[["figure", "comparison", "test", "p_adjusted", "symbol"]].to_string(index=False))


if __name__ == "__main__":
    main()
