"""DOC-2-072 data acquisition (PROTOCOL.md lock-1). Writes dataset.tsv (accession, family, label, length, sequence) and DATA_HASHES.tsv."""
import requests, hashlib, io, sys, numpy as np, pandas as pd
Q = "reviewed:true AND ec:* AND length:[100 TO 400] AND xref:pfam-*"
url = "https://rest.uniprot.org/uniprotkb/search"; params = dict(query=Q, fields="accession,ec,xref_pfam,length,sequence", format="tsv", size=500)
rows, rel = [], None; first = True
while url:
    r = requests.get(url, params=params if first else None, timeout=120); r.raise_for_status(); first = False
    rel = r.headers.get("x-uniprot-release", rel); lines = r.text.split("\n"); rows += lines[1:] if rows else lines
    url = r.links.get("next", {}).get("url")
raw = "\n".join(x for x in rows if x); open("uniprot_raw.tsv", "w").write(raw + "\n")
md5 = hashlib.md5((raw + "\n").encode()).hexdigest()
d = pd.read_csv(io.StringIO(raw), sep="\t"); d.columns = ["accession", "ec", "pfam", "length", "sequence"]
d["pf"] = d.pfam.fillna("").str.strip(";").str.split(";"); d = d[d.pf.str.len() == 1].copy(); d["family"] = d.pf.str[0]
d["lab"] = d.ec.fillna("").str.split(";").apply(lambda l: {x.strip().split(".")[0] for x in l if x.strip()})
d = d[d.lab.apply(len) == 1].copy(); d["label"] = d.lab.apply(lambda s: int(next(iter(s))))
d = d[d.label.between(1, 7) & ~d.sequence.str.contains("[XBZUO]")].sort_values("accession")
rng = np.random.default_rng(12345); cnt = d.family.value_counts(); fams = sorted(cnt[cnt >= 20].index)
if len(fams) > 250: fams = sorted(rng.choice(fams, 250, replace=False))
out = []
for f in fams:
    g = d[d.family == f]; out.append(g.iloc[np.sort(rng.choice(len(g), 20, replace=False))])
o = pd.concat(out)[["accession", "family", "label", "length", "sequence"]]; o.to_csv("dataset.tsv", sep="\t", index=False)
open("DATA_HASHES.tsv", "w").write(f"file\tmd5\tuniprot_release\tn_raw\nuniprot_raw.tsv\t{md5}\t{rel}\t{len(rows)-1}\n")
print("ACQ_DONE release", rel, "raw", len(rows) - 1, "families", len(fams), "n", len(o), "label_counts", o.label.value_counts().sort_index().to_dict())
