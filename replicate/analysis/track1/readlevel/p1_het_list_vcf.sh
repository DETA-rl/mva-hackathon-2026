#!/usr/bin/env bash
# P1 step 2 (ported): list the VCF records between the two candidate sites.
# Inputs from the harness: REPL_VCF, REPL_P1_CHROM (contig name without chr), REPL_P1_START, REPL_P1_END.
zcat "$REPL_VCF" | awk "\$1==\"$REPL_P1_CHROM\" || \$1==\"chr$REPL_P1_CHROM\"" | awk -F"\t" "\$2>=$REPL_P1_START && \$2<=$REPL_P1_END {print \$2,\$4,\$5,\$10}" | head -40
