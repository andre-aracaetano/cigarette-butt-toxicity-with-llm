"""Plot the species most often identified by the literature-mining workflow.

Counts are based on distinct article--species pairs, so repeated mentions of a
species within the same publication do not inflate its frequency.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "nlp" / "species_frequency.xlsx"
OUTPUTS = [
    ROOT / "results" / "figures",
]

PHYLUM = {
    "Daphnia magna": "Arthropoda",
    "Hediste diversicolor": "Annelida",
    "Aedes aegypti": "Arthropoda",
    "Aliivibrio fischeri": "Proteobacteria",
    "Mytilus edulis": "Mollusca",
    "Periophthalmus waltoni": "Chordata",
    "Phaeodactylum tricornutum": "Ochrophyta",
    "Dunaliella tertiolecta": "Chlorophyta",
    "Mytilus galloprovincialis": "Mollusca",
    "Aedes albopictus": "Arthropoda",
    "Lolium perenne": "Tracheophyta",
    "Trifolium repens": "Tracheophyta",
    "Austrocochlea porcata": "Mollusca",
    "Nerita atramentosa": "Mollusca",
    "Bembicium nanum": "Mollusca",
    "Ulva lactuca": "Chlorophyta",
    "Atherinops affinis": "Chordata",
    "Raphidocelis subcapitata": "Chlorophyta",
    "Anguispira alternata": "Mollusca",
    "Eisenia fetida": "Annelida",
    "Escherichia coli": "Proteobacteria",
    "Dreissena polymorpha": "Mollusca",
    "Polycelis nigra": "Platyhelminthes",
    "Planorbis planorbis": "Mollusca",
    "Bithynia tentaculata": "Mollusca",
}

COLORS = {
    "Arthropoda": "#2C7FB8",
    "Annelida": "#7FCDBB",
    "Proteobacteria": "#D95F0E",
    "Mollusca": "#FDAE6B",
    "Chordata": "#31A354",
    "Ochrophyta": "#9ECAE1",
    "Chlorophyta": "#74C476",
    "Tracheophyta": "#BDBDBD",
    "Platyhelminthes": "#756BB1",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.labelsize": 13,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def main() -> None:
    raw = pd.read_excel(DATA)
    unique = raw.dropna(subset=["article_id", "species"]).drop_duplicates(
        subset=["article_id", "species"]
    )
    # The original thesis figure used 25 taxa. This also avoids splitting the
    # large tie at two articles that would make a top-15 cutoff arbitrary.
    counts = unique["species"].value_counts().head(25).sort_values()
    phyla = [PHYLUM[name] for name in counts.index]

    # Extra horizontal space keeps the phylum legend outside the plotting area
    # instead of covering the shorter bars.
    fig, ax = plt.subplots(figsize=(9.0, 8.0))
    bars = ax.barh(
        range(len(counts)), counts.values,
        color=[COLORS[p] for p in phyla], edgecolor="black", linewidth=0.7,
    )
    ax.set_yticks(
        range(len(counts)),
        [rf"$\it{{{name.replace(' ', r'\ ')}}}$" for name in counts.index],
    )
    ax.set_xlabel("Number of articles")
    ax.set_ylabel("Species")
    ax.set_xticks(range(0, int(counts.max()) + 1))
    ax.grid(axis="x", linestyle="--", linewidth=0.6, alpha=0.3)
    ax.set_axisbelow(True)

    for bar, value in zip(bars, counts.values):
        ax.text(value + 0.06, bar.get_y() + bar.get_height() / 2, str(value),
                va="center", ha="left", fontsize=10)
    ax.set_xlim(0, counts.max() + 0.65)

    legend_order = list(dict.fromkeys(phyla[::-1]))
    handles = [mpatches.Patch(facecolor=COLORS[p], edgecolor="black", label=p)
               for p in legend_order]
    ax.legend(handles=handles, title="Phylum", frameon=False, ncol=1,
              loc="center left", bbox_to_anchor=(1.02, 0.5),
              borderaxespad=0, fontsize=10, title_fontsize=11)
    fig.tight_layout(rect=(0, 0, 0.79, 1))

    for folder in OUTPUTS:
        folder.mkdir(parents=True, exist_ok=True)
        fig.savefig(folder / "nlp_species_frequency.pdf", bbox_inches="tight")
        fig.savefig(folder / "nlp_species_frequency.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
