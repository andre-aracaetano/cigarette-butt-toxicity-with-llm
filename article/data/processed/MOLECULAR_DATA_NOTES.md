# ROS, comet assay, and RT-qPCR data notes

## ROS

Analysis file: `ros_intensity_22082025.xlsx`.

Columns: `sample`, `type`, `concentration`, and `intensity`. Row `Snap-19` has
no value in the expected `intensity` column; the value `220784` appears in an
adjacent column. This must be checked against the original QuantiFish export
before the final analysis. Missing values must not be silently moved.

Raw treatment labels BCT/BST are displayed in the manuscript as SCB/SCF.

## Comet assay

Analysis file: `comet_assay_clean.xlsx`.

Columns: `type`, `concentration`, and `tail_moment`. The processed table does not
retain a stable image/cell identifier or experimental date. The main figure
excludes positive and negative controls; the complete figure in the SI retains
the controls and outliers, following the monograph.

## RT-qPCR

Analysis file: `rt_qpcr_expression.xlsx`.

Columns called `il1` and `tnf` represent `il1b` and `tnfa`, respectively. The
rows appear to represent technical triplicates derived from one pooled biological
sample per treatment. Confirm this design. Technical replicates alone cannot be
used as independent biological replicates for population-level inference.

The plotted values are normalized relative expression values. Confirm the exact
calculation method (for example, 2^-DeltaDeltaCt), reference-gene processing, and
whether amplification efficiencies were assumed equal.

