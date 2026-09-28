# NLP-derived gene-selection data

These three workbooks support the gene-frequency figure used to explain the
RT-qPCR target-selection rationale:

- `nicotine_extraction.xlsx`: nicotine literature extractions.
- `heavy_metals_extraction.xlsx`: heavy-metal literature extractions.
- `pahs_extraction.xlsx`: polycyclic aromatic hydrocarbon extractions.

The publication workflow is documented in
`article/notebooks/01_nlp_gene_frequency.ipynb`. It counts a gene at most once
per literature record and preserves an audit table for comparison with the
legacy token-frequency calculation.
