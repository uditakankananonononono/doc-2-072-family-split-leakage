# DOC-2-072 "Protein grammar across families": how much does a random split inflate ESM-2 embedding function prediction relative to a family-held-out split? (frozen protocol, lock-1)

Written 2026-10-09 IST and committed BEFORE any data was downloaded or embedded.

## What the four prior negatives ruled out, and why this is not a re-ask
DOC-2-073, 077, 009-R3 and 009-R4 all asked whether per-assay ESM-2 zero-shot variant-effect rho (ProteinGym, 204 assays) varies with protein or assay features (annotation depth, length, WTLL, taxon, assay type, MSA depth). All four were HONEST NEGATIVES, and R4 found a split confound (selection type almost perfectly confounded with the year split). This study uses a different surface: not variant-effect rho and not ProteinGym, but frozen-embedding classification of enzyme function on Swiss-Prot. It asks about evaluation design (the random-vs-family split gap), the lesson R4 taught, and not about which features predict rho. Nothing from the four studies is reused.
Prior art disclosure: that random splits leak homology and inflate protein-function prediction is well known. This study does not claim novelty for the phenomenon. It measures the gap with frozen gates for one model, one label and one family definition.

## Data (frozen definitions; all downloaded after this lock)
- Source: UniProtKB REST, query `reviewed:true AND ec:* AND length:[100 TO 400] AND xref:pfam-*`, release recorded at download (current as of lock: 2026_03). Fields: accession, ec, xref_pfam, length, sequence.
- Keep proteins with exactly one Pfam id, all listed EC numbers sharing the same first digit (label = EC level-1 class 1-7), and no 'X'/'B'/'Z'/'U'/'O' residues.
- Family = that Pfam id. Keep families with >= 20 qualifying proteins. Seed 12345: from each kept family sample exactly 20 proteins (sorted by accession, numpy default_rng). Then sample families down to at most 250 with seed 12345 if more qualify. Final set expected about 5,000 proteins; the actual n is reported.
- Download md5 of the TSV and the UniProt release are recorded in DATA_HASHES.tsv.

## Features
- E: mean-pooled last-layer ESM-2 35M (esm2_t12_35M_UR50D) embeddings, fp32, CPU, residues only (no special tokens), max length 400.
- C (baseline): 20 amino-acid frequencies + log length.

## Models and splits
- Standardize then logistic regression (L2, C = 1, max_iter 2000, class_weight balanced). Macro-F1.
- Random scheme R: StratifiedKFold(5, shuffle, seed 12345) on proteins.
- Family scheme F: GroupKFold(5) by Pfam family (families never split across folds; fold assignment by sorted family id for reproducibility).
- Pooled out-of-fold predictions are scored. CI: family-cluster bootstrap over families (2,000 resamples, seed 12345, percentile 95%) of the pooled OOF macro-F1 difference.

## Gates
- G1 (pipeline control): macro-F1 of E under R with labels permuted across proteins (seed 12345) is < chance + 0.05 (chance = 1/7 = 0.143 or the best majority-class macro-F1; report both). A failed control invalidates the run; label = INVALID, not a result.
- G2 (leakage gap): macro-F1(E, R) - macro-F1(E, F) >= +0.15 and the bootstrap CI lower bound > +0.05.
- G3 (embedding adds beyond composition under F): macro-F1(E, F) - macro-F1(C, F) >= +0.05 and the CI lower bound > 0.
Labels (mechanical): INVALID if G1 fails. LEAKAGE-CONFIRMED if G1 and G2 pass. HONEST NEGATIVE (gap < 0.15 or CI too low) otherwise. G3 is reported as EMBEDDING-ADDS or EMBEDDING-DOES-NOT-ADD and cannot change the main label.

## Limits stated up front
- Family = Pfam family, not clan: related families in the same clan can still leak across folds, so the family scheme may understate true held-out difficulty. Pfam clans are not acquired.
- One model size (35M), one label (EC level-1, coarse), mean pooling only. Swiss-Prot sampling is not random over all proteins. No claim about other models, labels or splits.
- Compute: Colab CPU only (T4 refused earlier). No simulated data, no stubs. Smoke test on synthetic embeddings only. Scripts are run once with a run log (command, UTC times, versions, md5 check).
- Deviation budget: one tolerance line; amendments are new dated AMENDMENT-N.md files committed before outcomes exist.

## Execution note
Only analysis.py was smoke-tested (synthetic random embeddings, locally; the synthetic run left no record). acquire_data.py and embed.py could not be tested in the builder's sandbox (no transformers) and will first run in Colab. A crash there is fixed by a dated AMENDMENT-N.md limited to the bug, committed before outcomes exist; design, gates and thresholds do not change.
