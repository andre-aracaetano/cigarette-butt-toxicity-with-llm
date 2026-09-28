# Article analysis files

## Folders

- `data/raw/`: compact source tables used by the analysis.
- `data/processed/`: cleaned tables, statistical results, and data notes.
- `data/nlp/`: literature-mining datasets cited in the Supplementary Information.
- `notebooks/`: documented exploratory and concentration-response workflows.
- `scripts/`: canonical scripts for publication figures and statistics.
- `results/`: generated locally; excluded from version control.

Run commands from the repository root or from `article/`. Original treatment
codes remain in source files; publication figures use SCB, SCF, and Control.

The NLP spreadsheets contain bibliographic metadata and structured derived
outputs. `species_frequency.xlsx` is the normalized article--species table used
to reproduce the supplementary frequency figure. Publisher PDFs and full-text
article files are intentionally excluded.
