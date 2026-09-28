"""Reproducible publication figures for ROS, comet assay, and RT-qPCR.

The script deliberately does not attach inferential significance to RT-qPCR
technical replicates or comet-assay cells whose biological-sample identifiers
were not retained. This avoids pseudoreplication in the manuscript.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import kruskal, rankdata
from scipy.special import ndtr


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
FIGURES = ROOT / "results" / "figures"
for folder in (FIGURES,):
    folder.mkdir(parents=True, exist_ok=True)

COLORS = {"Control": "#7F7F7F", "SCB": "#2C7FB8", "SCF": "#D95F0E",
          "Positive control": "#6A3D9A"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "pdf.fonttype": 42, "ps.fonttype": 42})


def save(fig, stem):
    for folder in (FIGURES,):
        fig.savefig(folder / f"{stem}.pdf", bbox_inches="tight")
        fig.savefig(folder / f"{stem}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def dunn_control(df, value, order):
    work = df[["group", value]].dropna()
    arrays = [work.loc[work.group.eq(g), value].to_numpy() for g in order]
    _, omnibus_p = kruskal(*arrays)
    work = work.assign(_rank=rankdata(work[value]))
    n = len(work)
    _, counts = np.unique(work[value], return_counts=True)
    tie = 1 - np.sum(counts**3 - counts) / (n**3 - n)
    variance = n * (n + 1) / 12 * tie
    control = work.loc[work.group.eq("Control"), "_rank"]
    rows = []
    for group in order[1:]:
        exposed = work.loc[work.group.eq(group), "_rank"]
        z = (exposed.mean() - control.mean()) / np.sqrt(variance * (1 / len(exposed) + 1 / len(control)))
        p = 2 * ndtr(-abs(z))
        rows.append({"endpoint": value, "test": "Kruskal-Wallis + Dunn-Bonferroni",
                     "omnibus_p": omnibus_p, "comparison": f"{group} vs Control",
                     "p_raw": p})
    out = pd.DataFrame(rows)
    out["p_adjusted"] = np.minimum(out.p_raw * len(out), 1)
    out["symbol"] = out.p_adjusted.map(lambda p: "****" if p < .0001 else "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else "ns")
    return out


def ros_figure():
    raw = pd.read_excel(DATA / "ros_intensity_22082025.xlsx")
    raw["treatment"] = raw.type.replace({"control": "Control", "BCT": "SCB", "BST": "SCF"})
    raw["group"] = np.where(raw.treatment.eq("Control"), "Control",
                            raw.treatment + " " + raw.concentration.astype(str))
    # Snap-19 is retained as missing: its displaced value is not reassigned without source verification.
    df = raw.dropna(subset=["intensity"])
    order = ["Control", "SCB 1", "SCB 2", "SCF 1", "SCF 2"]
    stats = dunn_control(df, "intensity", order)
    stats.to_csv(DATA / "ros_statistics.csv", index=False)
    df.groupby("group").intensity.agg(n="count", mean="mean", sd="std", median="median").reindex(order).to_csv(DATA / "ros_descriptive.csv")
    vals = [df.loc[df.group.eq(g), "intensity"] for g in order]
    fig, ax = plt.subplots(figsize=(6.7, 4.0))
    bp = ax.boxplot(vals, patch_artist=True, showfliers=False, widths=.58,
                    medianprops={"color": "black", "linewidth": 1.2})
    rng = np.random.default_rng(42)
    for i, (g, v, b) in enumerate(zip(order, vals, bp["boxes"])):
        key = "Control" if g == "Control" else g.split()[0]
        b.set(facecolor=COLORS[key], edgecolor="black", alpha=.82)
        ax.scatter(rng.normal(i + 1, .055, len(v)), v, s=14, color="black", alpha=.55, linewidth=0)
    lookup = dict(zip(stats.comparison.str.replace(" vs Control", "", regex=False), stats.symbol))
    for i, (g, v) in enumerate(zip(order[1:], vals[1:]), 2):
        mark = lookup[g]
        if mark != "ns": ax.text(i, v.max() + 9000, mark, ha="center")
    ax.set_xticks(range(1, 6), order, rotation=30, ha="right")
    ax.set_ylabel("ROS-associated fluorescence (a.u.)")
    ax.set_xlabel("Treatment (CB/L)")
    ax.grid(axis="y", ls="--", lw=.6, alpha=.3)
    fig.tight_layout(); save(fig, "ros_intensity")


def comet_figure():
    raw = pd.read_excel(DATA / "comet_assay_clean.xlsx")
    labels = {"control_negative": "Control", "control_positive": "Positive control", "BCT": "SCB", "BST": "SCF"}
    raw["treatment"] = raw.type.replace(labels)
    raw["group"] = np.where(raw.treatment.isin(["Control", "Positive control"]), raw.treatment,
                            raw.treatment + " " + raw.concentration.map(lambda x: f"{x:.1f}"))
    order = ["Control", "SCB 0.5", "SCB 1.0", "SCB 2.0", "SCF 0.5", "SCF 1.0", "SCF 2.0"]
    desc = raw.loc[raw.group.isin(order)].groupby("group").tail_moment.agg(cells="count", mean="mean", sd="std", median="median", q1=lambda x:x.quantile(.25), q3=lambda x:x.quantile(.75)).reindex(order)
    desc.to_csv(DATA / "comet_descriptive.csv")
    vals = [raw.loc[raw.group.eq(g), "tail_moment"] for g in order]
    fig, ax = plt.subplots(figsize=(7.2, 4.1))
    bp = ax.boxplot(vals, patch_artist=True, showfliers=False, widths=.58,
                    medianprops={"color":"black", "linewidth":1.2})
    rng = np.random.default_rng(43)
    for i, (g, v, b) in enumerate(zip(order, vals, bp["boxes"])):
        key = "Control" if g == "Control" else g.split()[0]
        b.set(facecolor=COLORS[key], edgecolor="black", alpha=.82)
        sample = v.sample(min(len(v), 80), random_state=43)
        ax.scatter(rng.normal(i + 1, .06, len(sample)), sample, s=8, color="black", alpha=.25, linewidth=0)
    ax.set_yscale("symlog", linthresh=.5)
    ax.set_xticks(range(1, len(order)+1), order, rotation=32, ha="right")
    ax.set_ylabel("Olive tail moment")
    ax.set_xlabel("Treatment (CB/L)")
    ax.grid(axis="y", ls="--", lw=.6, alpha=.3)
    fig.tight_layout(); save(fig, "comet_assay")


def qpcr_figure():
    raw = pd.read_excel(DATA / "rt_qpcr_expression.xlsx").rename(columns={"il1":"il1b", "tnf":"tnfa"})
    raw["treatment"] = raw.type.replace({"controle":"Control", "bct":"SCB", "bst":"SCF"})
    genes = ["nestin", "gfap", "il1b", "tnfa", "casp9"]
    long = raw.melt(id_vars="treatment", value_vars=genes, var_name="gene", value_name="expression").dropna()
    summary = long.groupby(["gene", "treatment"]).expression.agg(technical_n="count", mean="mean", sd="std").reset_index()
    summary.to_csv(DATA / "rt_qpcr_descriptive.csv", index=False)
    order_t = ["Control", "SCB", "SCF"]
    x = np.arange(len(genes)); width=.24
    fig, ax = plt.subplots(figsize=(7.2, 4.1))
    rng = np.random.default_rng(44)
    for j, treatment in enumerate(order_t):
        means=[]; sds=[]
        for gene in genes:
            v=long.loc[(long.gene.eq(gene)) & (long.treatment.eq(treatment)), "expression"]
            means.append(v.mean()); sds.append(v.std())
        positions=x+(j-1)*width
        ax.bar(positions, means, width, yerr=sds, capsize=2.5, label=treatment,
               color=COLORS[treatment], edgecolor="black", linewidth=.7, alpha=.85)
        for i,gene in enumerate(genes):
            v=long.loc[(long.gene.eq(gene)) & (long.treatment.eq(treatment)), "expression"]
            ax.scatter(rng.normal(positions[i], .018, len(v)), v, s=14, color="black", alpha=.6, zorder=3)
    ax.axhline(1, color="0.4", lw=1, ls="--")
    ax.set_xticks(x, [r"$nestin$", r"$gfap$", r"$il1b$", r"$tnfa$", r"$casp9$"])
    ax.set_ylabel("Relative expression")
    ax.legend(frameon=False, ncol=3)
    ax.grid(axis="y", ls="--", lw=.6, alpha=.3)
    fig.tight_layout(); save(fig, "rt_qpcr_expression")


if __name__ == "__main__":
    ros_figure(); comet_figure(); qpcr_figure()
