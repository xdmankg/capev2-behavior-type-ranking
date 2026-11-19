"""Recalculate the journal tables from de-identified execution summaries."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import ast
import hashlib
import json
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEEDS = list(range(20260716, 20260721))
MODELS = ["M3_CI", "M_SEQ_CAND", "M_SEQ_CAND_PRESENCE", "M_SEQ_CAND_RES", "M1", "Conditional frequency"]
PAIRS = [(2, 1), (3, 2), (3, 1), (1, 0), (1, 4)]
def read(path):
    return pd.read_csv(ROOT / path)
def require(ok, message):
    if not ok:
        raise ValueError(message)
def group_metrics(frame):
    sums = frame.groupby("seed")[["rr_sum", "recall3_sum", "n_eligible", "n_target_positive"]].sum()
    return [(sums.rr_sum / sums.n_eligible).mean(), (sums.rr_sum / sums.n_target_positive).mean(), (sums.recall3_sum / sums.n_target_positive).mean()]
def main():
    manifest = (ROOT / "checksums.sha256").read_text().splitlines()
    names = [line.split("  ",1)[1] for line in manifest]
    static = {f.relative_to(ROOT).as_posix() for f in ROOT.rglob("*") if f.is_file() and f != ROOT/"checksums.sha256" and ".git" not in f.relative_to(ROOT).parts}
    require(len(names)==len(set(names)) and set(names)==static, "Static file inventory")
    for line in manifest:
        digest, name = line.split("  ", 1)
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, "Checksum: " + name)
    data = pd.read_parquet(ROOT / "data/executions.parquet")
    keys = ["split", "fold", "configuration", "seed", "execution_key"]
    require(not data[keys].isna().any().any() and not data.duplicated(keys).any(), "Duplicate or missing key")
    require((data.n_eligible > 0).all() and data.n_target_positive.between(0, data.n_eligible).all(), "Invalid denominator")
    require((data.in_primary_set == (data.split == "Test")).all(), "Primary set")
    require(np.isfinite(data[["rr_sum","recall3_sum"]]).all().all(), "Nonfinite sum")
    require(set(data.split)=={"OOF","Validation","Test"} and set(data[data.split=="OOF"].fold)=={"1","2","3"}, "Evaluation partitions")
    for (split, fold), group in data.groupby(["split","fold"]):
        ref = None
        for (model, seed), g in group.groupby(["configuration","seed"]):
            counts = g.set_index("execution_key")[["n_eligible","n_target_positive"]].sort_index()
            if ref is None:
                ref = counts
            require(counts.equals(ref), "Execution keys or case counts differ")
        for model in MODELS:
            expected = SEEDS if model in MODELS[:4] else [] if split=="OOF" and model=="M1" else [0]
            require(sorted(group.loc[group.configuration==model,"seed"].unique())==expected, "Configuration or seed coverage")
    output = []
    population = read("data/populations.csv").pivot(index="split",columns="quantity",values="direct")
    t4=read("data/table4_printed.csv")
    for i, split in enumerate(["Training","OOF","Validation","Test","Test auxiliary"]):
        p = population.loc[split]
        printed = [int(str(v).replace(",","")) for v in t4.iloc[i,1:]]
        require(printed==list(p[["executions","generated","eligible","positive","empty"]]), "Table 4 population")
        if split in ("OOF","Validation","Test"):
            unique=data[(data.split==split)&(data.configuration==MODELS[0])&(data.seed==SEEDS[0])]
            require((unique.n_eligible.sum(),unique.n_target_positive.sum())==(p.eligible,p.positive),"Table 4 denominators")
        output.append(dict(item="Table 4",split=split,eligible=int(p.eligible),positive=int(p.positive),empty=int(p["empty"])))
    t6=read("data/table6_printed.csv")
    for i, model in enumerate(MODELS):
        for j,(split,metric) in enumerate([("OOF",0),("Validation",0),("Test",0),("Test",1),("Test",2)]):
            sub=data[(data.configuration==model)&(data.split==split)]
            printed=str(t6.iloc[i,j+1])
            if sub.empty:
                require(printed=="—" and model=="M1" and split=="OOF","Unexpected missing result")
                output.append(dict(item="Table 6",model=model,split=split,printed=printed))
                continue
            actual=group_metrics(sub)[metric]
            require(f"{actual:.4f}"==f"{float(printed):.4f}","Table 6 "+model+" "+split)
            if model==MODELS[5] and metric==2:
                require(abs(actual-0.7945814313599178)<1e-14,"Conditional recall")
            output.append(dict(item="Table 6",model=model,split=split,metric=["MRR","positive MRR","positive Recall@3"][metric],printed=printed,actual=actual,difference=actual-float(printed),denominator=int(population.loc[split,"eligible" if metric==0 else "positive"])))
    test=data[data.in_primary_set]
    idx=test.execution_key.sort_values().unique()
    def matrix(model):
        pivot=test[test.configuration==model].pivot(index="execution_key",columns="seed",values="rr_sum").loc[idx]
        return pivot.to_numpy()
    cnt=test[(test.configuration==MODELS[0])&(test.seed==SEEDS[0])].set_index("execution_key").loc[idx,"n_eligible"].to_numpy(float)
    diffs=[matrix(MODELS[i])-matrix(MODELS[j]) for i,j in PAIRS]
    seed_delta=np.stack([d.sum(axis=0)/cnt.sum() for d in diffs])
    sums=np.stack([d.mean(axis=1) for d in diffs],axis=1)
    boot=[]; rng=np.random.Generator(np.random.PCG64(20260808))
    for first in range(0,2000,32):
        sampled=rng.choice(len(cnt),size=(min(32,2000-first),len(cnt)),replace=True)
        weights=np.stack([np.bincount(row,minlength=len(cnt)) for row in sampled]).astype(float)
        boot.extend((weights@sums)/(weights@cnt)[:,None])
    bounds=np.percentile(boot,[2.5,97.5],axis=0,method="linear")
    expected=read("data/table7_reference.csv")
    printed=read("data/table7_printed.csv")
    for j,(a,b) in enumerate(PAIRS):
        delta=seed_delta[j].mean(); low,high=bounds[:,j]; pos=int(sum(seed_delta[j]>0))
        decision=bool(delta>=.01 and low>0 and pos>=4)
        e=expected.iloc[j]; p=printed.iloc[j]
        actual=np.array([delta,low,high]); refs=np.array([e.delta,e.low,e.high])
        require(np.allclose(actual,refs,rtol=0,atol=1e-12) and pos==e.positive_seeds and decision==e.decision, "Table 7 reference")
        digits=[float(str(p.iloc[1]).replace("−","-"))]+[float(v) for v in re.findall(r"[-+]?\d+\.\d+",p.iloc[2].replace("−","-"))]
        require([round(float(x),6) for x in actual]==digits and p.iloc[3]==f"{pos}/5" and (p.iloc[4]=="Met")==decision,"Table 7 manuscript")
        output.append(dict(item="Table 7",contrast=e.contrast,denominator=int(cnt.sum()),expected=digits,actual=actual.tolist(),difference=(actual-refs).tolist(),positive_seeds=pos,decision=decision))
    fig=read("data/figure6_sums.csv").groupby(["configuration","condition","seed"])[["n","rr"]].sum()
    estimates=(fig.rr/fig.n).groupby(level=[0,1]).mean()
    for row in read("results/main/figure6_reference.csv").itertuples():
        value=estimates.loc[row.model,row.condition]
        require(abs(value-row.reference)<=0.0000051,"Figure 6")
    gaps=estimates.loc["Graph-correction model"]-estimates.loc["Pooled LR"]
    require(round(gaps["RAW_SCORE"],6)==0.277683 and round(gaps["OBSERVED_EXCLUDED"],6)==0.011500,"Figure 6 gap")
    from importlib.util import module_from_spec, spec_from_file_location
    spec = spec_from_file_location("check_figures", ROOT / "scripts/check_figures.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    output.extend(dict(item="Figure 8", **row) for row in module.check(ROOT))
    helper_spec = spec_from_file_location("check_components", ROOT / "scripts/check_components.py")
    helper = module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper)
    output.extend(helper.check_components(ROOT, MODELS, SEEDS))
    print(json.dumps(output,indent=2,ensure_ascii=True))
    print("PASS: Tables 6 and 7, evaluation populations, Figures 6, 8 and 10. Fixed-budget execution counts and nine MRR values checked against Section S4.")
if __name__=="__main__":
    main()
