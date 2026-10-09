"""DOC-2-072 frozen analysis (PROTOCOL.md lock-1). Run once. Needs dataset.tsv, emb.npy."""
import json, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
rng = np.random.default_rng(12345)
d = pd.read_csv("dataset.tsv", sep="\t"); E = np.load("emb.npy"); y = d.label.values; fam = d.family.values; n = len(d)
AA = "ACDEFGHIKLMNPQRSTVWY"; C = np.array([[s.count(a) / len(s) for a in AA] + [np.log(len(s))] for s in d.sequence])
def clf(): return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000, class_weight="balanced"))
def oof(X, yy, folds):
    p = np.zeros(n, dtype=int)
    for tr, te in folds: p[te] = clf().fit(X[tr], yy[tr]).predict(X[te])
    return p
rand_folds = list(StratifiedKFold(5, shuffle=True, random_state=12345).split(E, y))
uf = sorted(set(fam)); fold_of = {f: i % 5 for i, f in enumerate(uf)}; fid = np.array([fold_of[f] for f in fam])
fam_folds = [(np.where(fid != k)[0], np.where(fid == k)[0]) for k in range(5)]
mf = lambda yy, pp: f1_score(yy, pp, average="macro")
P = {"E_R": oof(E, y, rand_folds), "E_F": oof(E, y, fam_folds), "C_F": oof(C, y, fam_folds)}
yperm = rng.permutation(y); pperm = oof(E, yperm, rand_folds)
res = {"n": n, "n_families": len(uf), "label_counts": {int(k): int(v) for k, v in pd.Series(y).value_counts().sort_index().items()}}
maj = max(pd.Series(y).value_counts()) / n
res["G1"] = dict(perm_macroF1=mf(yperm, pperm), chance_1_over_7=1 / 7, pass_=bool(mf(yperm, pperm) < 1 / 7 + 0.05))
f = {k: mf(y, p) for k, p in P.items()}; res["macroF1"] = f
members = {u: np.where(fam == u)[0] for u in uf}; bs = {"gap": [], "emb": []}
for _ in range(2000):
    idx = np.concatenate([members[u] for u in rng.choice(uf, len(uf))])
    bs["gap"].append(mf(y[idx], P["E_R"][idx]) - mf(y[idx], P["E_F"][idx])); bs["emb"].append(mf(y[idx], P["E_F"][idx]) - mf(y[idx], P["C_F"][idx]))
ci = lambda k: list(np.percentile(bs[k], [2.5, 97.5]))
gap = f["E_R"] - f["E_F"]; emb = f["E_F"] - f["C_F"]
res["G2"] = dict(gap=gap, ci=ci("gap"), pass_=bool(gap >= 0.15 and ci("gap")[0] > 0.05))
res["G3"] = dict(delta=emb, ci=ci("emb"), pass_=bool(emb >= 0.05 and ci("emb")[0] > 0), label="EMBEDDING-ADDS" if (emb >= 0.05 and ci("emb")[0] > 0) else "EMBEDDING-DOES-NOT-ADD")
res["LABEL"] = "INVALID" if not res["G1"]["pass_"] else ("LEAKAGE-CONFIRMED" if res["G2"]["pass_"] else "HONEST NEGATIVE")
print("RESULT_JSON", json.dumps(res, default=float)); open("results.json", "w").write(json.dumps(res, default=float, indent=1))
