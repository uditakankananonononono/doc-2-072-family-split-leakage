# DOC-2-072 RESULTS - review pending (independent gate has not cleared; no claim is final)

Label: **FAMILY-SHORTCUT CONFIRMED** (registered label set mechanically by analysis.py: LEAKAGE-CONFIRMED; G1 pass, G2 pass). Magnitude is not a benchmark estimate. G3 is report-only (registered tag EMBEDDING-ADDS, see below for what it does and does not mean).

Supported claim: under a design where EC level-1 is almost determined by Pfam family, random splits let the classifier exploit family identity: macro-F1 0.96 vs 0.37 when families are held out. Not supported: any size claim for real benchmarks, and any claim about homology or clan leakage (0.371 may itself be inflated by shared clans, so the gap may be a lower bound).

| item | value |
|---|---|
| data | UniProt release 2026_03, 5,000 proteins, 250 Pfam families x 20, 7 EC level-1 classes (counts 618/1709/1455/634/324/101/159) |
| G1 permuted-label macro-F1 (random split) | 0.132 (needed < 0.193; chance 0.143) - pass |
| E, random split macro-F1 | 0.959 |
| E, family-held-out macro-F1 | 0.371 |
| C (composition + log length), family-held-out | 0.223 |
| G2 gap (random minus family) | +0.587, 95% family-bootstrap CI [0.530, 0.647] (needed >= 0.15, CI lb > 0.05) - pass |
| G3 (E minus C, family split) | +0.148, CI [0.098, 0.193] - reported only. Meaning: ESM-2 mean-pooled features (480 dims) beat composition + log length (21 dims) under the same linear classifier and family split. Not an information-theoretic "adds beyond composition" claim |

## What this does and does not show
- Under the frozen design, a random split inflates macro-F1 by about 0.59 relative to a family-held-out split. This is the pre-stated criterion for LEAKAGE-CONFIRMED.
- The size of the gap is partly built into the design: every family contributes 20 proteins, and EC class is nearly determined by Pfam family, so a random split lets a classifier recognise the family. The result confirms that family identity carries the signal; it does not measure how much a real-world benchmark would be inflated.
- Family-held-out macro-F1 of 0.371 is above chance (0.143) and above composition (0.223, G3 +0.148), so embeddings carry some function signal that transfers across Pfam families. Clan-level leakage is not measured (Pfam clans not acquired), so 0.371 may still be inflated and the gap is a lower bound on leakage.
- G3 limits: 23x feature-size difference (480 vs 21 dims); composition is a weak baseline; no higher-capacity composition baseline (3-mer, dipeptide) was run.
- Design limit: near-perfect family-to-label purity (gate-reported: 217 of 250 families single EC class, mean within-family majority-label share 0.976), so the 0.15 G2 threshold was close to unfalsifiable under this design.
- Majority-class macro-F1 was not reported (PROTOCOL.md said to report both).
- sklearn version sensitivity at the third decimal: gate rerun with sklearn 1.9.1 vs 1.7.2 moved E_R 0.9585 -> 0.9574 and the gap 0.5875 -> 0.5867; all gate decisions unchanged.
- Not a verified leakage graph; single seed, single model (ESM-2 35M), single classifier; EC level-1 only.
- What the four earlier ESM-2 rho negatives ruled out is stated in PROTOCOL.md; this question is a different task (classification, not DMS rho).

## Disclosures and deviations
- AMENDMENT-1 (PROTOCOL.md prose "GroupKFold(5)" is superseded by the amendment, PROTOCOL.md was not edited; the round-robin family folds in code are the authority; analysis.py is as locked, md5 bf9132ffd409a1f9825a025904b27ac4 identical to the lock-1 file).
- Provenance: the locked acquire_data.py did not itself produce the data; acquire_data_retry.py (diff = retry loop + progress print only) did. The lock precedes everything; both amendments precede the analysis run by server time.
- AMENDMENT-2: the lock-1 acquire_data.py crashed with a UniProt ReadTimeout (crash_log_acquire.txt); acquire_data_retry.py adds retries only. Committed before any outcome. embed.py was run as locked.
- "Smoke test on synthetic data before the run" is a builder statement; no record was saved.
- raw row count in DATA_HASHES.tsv (165,484) is 331 more than UniProt X-Total-Results (165,153): the script counts one blank line per page. Does not affect the dataset (blank lines are dropped).
- Run environment: builder sandbox, CPU only, python 3.10.12, numpy 2.2.6, pandas 2.3.3, sklearn 1.7.2, torch 2.14.1+cpu, transformers 5.19.0. Run log: run_log.txt (UTC 15:26:53 to 15:28:02, exit 0). input_md5.txt holds md5 of dataset.tsv, emb.npy, uniprot_raw.tsv and analysis.py. tag_tree_check.txt records the lock-1 tag tree (4 files, the DOC-2-072 scripts).
- Large files (dataset.tsv, emb.npy, uniprot_raw.tsv) are on Drive only, not in the repo; md5s above.
- analysis.py was run once.
