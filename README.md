# Cigarette-butt leachate toxicity in zebrafish

Code and selected datasets for a study of smoked cigarette-butt (SCB) and
smoked cigarette-filter (SCF) leachates in zebrafish embryos. The project
combines literature mining with developmental, physiological, oxidative-stress,
genotoxicity, and exploratory gene-expression endpoints.

## Repository layout

- `article/`: data, notebooks, and scripts used for the manuscript figures.
- `script_llm_extracao.py`: original local-LLM extraction workflow.
- `analisador_pigmentacao/`: image-processing workflow for larval pigmentation.
- `bancos de dados/` and `tratamento/`: legacy project datasets and analyses.
- `modelo3D_robo_fumante.stl`: smoking-device component.

## Reproducing the article analyses

```bash
python -m pip install -r article/requirements.txt
python article/scripts/plot_developmental_endpoints.py
python article/scripts/plot_molecular_endpoints.py
python article/scripts/plot_nlp_species_frequency.py
```

The scripts write figures and statistical summaries under `article/results/`.
The notebooks in `article/notebooks/` document the NLP gene-frequency and
concentration-response workflows.

Raw microscopy images, videos, and copyright-protected article full texts are
not distributed in this repository.

## Data notes

Source treatment codes are retained where needed for traceability: `BCT` is
displayed as SCB and `BST` as SCF. Files containing RT-qPCR technical
replicates or comet-assay cells without biological-replicate identifiers are
used descriptively to avoid pseudoreplication.

## License

Code is released under the MIT License. Dataset reuse remains subject to the
terms of the original data sources and publications.
