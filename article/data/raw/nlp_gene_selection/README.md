# NLP-derived gene selection data

This directory contains the three extraction tables used to build the gene-frequency figure for the RT-qPCR target-selection rationale.

## Provenance

The source files are copied without modification from:

`github/cigarette-butt-toxicity-with-llm_fresh/bancos de dados/extracoes/`

The original analysis and plotting code is in `NLP/analise.ipynb` (notably cells 19, 29, 38, and 47–48). The reproducible, publication-oriented reconstruction is `article/notebooks/01_nlp_gene_frequency.ipynb`.

## Files

- `resultados_nicotina.xlsx`: nicotine literature extractions.
- `resultados_metais.xlsx`: heavy-metal literature extractions.
- `resultados_pahs.xlsx`: PAH literature extractions.

The source workbooks retain their original Portuguese filenames for traceability. The reconstructed notebook uses English labels in outputs.

## Integrity (SHA-256)

- `resultados_nicotina.xlsx`: `d9104c412def1534e0b37f14f7d34931587ec1173c26832ff7c4fddd62847dd7`
- `resultados_metais.xlsx`: `c164e0df0939e4f3427f6c0151ad670f8bbfab7ebf16ac04ea7394f29bcac7ad`
- `resultados_pahs.xlsx`: `9d3f4314bc8bde180a19ab8c7292eefe649811188d61edafb3bdea9a5d18be2d`

## Historical-analysis note

The legacy plot counted comma-separated gene tokens across rows. The reconstructed notebook calculates both that legacy count and a per-record count that deduplicates repeated gene symbols within each record. The publication plot uses the per-record result; the comparison table makes any difference explicit.
