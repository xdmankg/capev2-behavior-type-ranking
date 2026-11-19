"""Cross-check the published Figure 8 labels and training records."""
from pathlib import Path
import json
import pandas as pd

def check(root):
    def number(v):
        return float(str(v).replace("−", "-").replace(",", ""))
    def read(name):
        return pd.read_csv(root/name, dtype=str)
    a=read("data/tableS23_printed.csv")
    b=read("data/tableS26_printed.csv")
    c=read("data/tableS54_printed.csv")
    labels=read("data/figure8_labels.csv")
    rows=[]
    for panel, split, ratio, condition, n, delta in labels.itertuples(index=False,name=None):
        if panel=="a":
            source=b[(b.iloc[:,0]=="Target observation ratio")&(b.iloc[:,1]==ratio)].iloc[0]
            expected_n, value=number(source.iloc[2]), number(source.iloc[4])
            grouped=c[(c.iloc[:,0]==split)&(c.iloc[:,1]==ratio)]
            if sum(map(number,grouped.iloc[:,3]))!=expected_n:
                raise ValueError("Figure 8(a) group sizes")
        else:
            source=c[(c.iloc[:,0]==split)&(c.iloc[:,1]==ratio)&(c.iloc[:,2]==condition)].iloc[0]
            expected_n,value=number(source.iloc[3]),number(source.iloc[5])
            text="Satisfied" if condition=="1" else "Not satisfied"
            if split=="Validation":
                other=a[(a.iloc[:,0]==ratio)&(a.iloc[:,1]==text)].iloc[0]
            else:
                other=b[b.iloc[:,1]==ratio+"|"+text].iloc[0]
            if (number(other.iloc[2]),number(other.iloc[3]))!=(expected_n,value):
                raise ValueError("Figure 8(b) supplement")
        if expected_n!=number(n) or round(value,4)!=number(delta):
            raise ValueError("Figure 8 label")
        rows.append(dict(panel=panel, split=split, ratio=ratio, condition=condition, cases=int(expected_n), source_delta=value, printed_delta=number(delta)))
    if len(rows)!=20:
        raise ValueError("Missing Figure 8 label")
    records=json.loads((root/"results/reproduction/training_records.json").read_text())
    c=records["model_C"]
    if not (c["generated_cases"]*c["types"]==c["score_elements"]==499120 and c["max_abs"]==0 and c["seed"]==20260716):
        raise ValueError("Model C record")
    d=pd.read_csv(root/"results/reproduction/indicator_inputs.csv").query("partition=='final' and branch!='constant'")
    if list(d[["B1_C0","B0_C1"]].sum())!=[56493,0] or records["model_B"]["final_classifiers"]!=85:
        raise ValueError("Model B record")
    return rows
