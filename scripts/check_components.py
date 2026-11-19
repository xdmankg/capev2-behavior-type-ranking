"""Check exact combinations and published descriptions of the derived results."""
from itertools import product
import ast
import json
import pandas as pd

def exact_keys(frame, columns, expected, label):
    actual = list(frame[columns].itertuples(index=False, name=None))
    if len(actual) != len(expected) or set(actual) != set(expected):
        raise ValueError(label + ": duplicate, missing or unexpected combination")

def check_components(root, models, seeds):
    read = lambda path: pd.read_csv(root / path)
    order = json.loads((root / "configs/type_order.json").read_text("utf8"))
    types = [entry["type_id"] for entry in order["types"]]
    if order["position_base"] != 1 or [e["position"] for e in order["types"]] != list(range(1,18)) or len(set(types)) != 17:
        raise ValueError("Invalid candidate order")
    f = read("results/main/figure10.csv")
    exact_keys(f, ["case","model","seed"], set(product("ACD",models[:4],seeds[:1])), "Figure 10 keys")
    out = []
    for case, rows in f.groupby("case"):
        targets_by_model = set()
        for row in rows.itertuples():
            top = row.top5.split("|")
            target_list = ast.literal_eval(row.targets)
            targets = set(target_list)
            targets_by_model.add(frozenset(targets))
            if len(top)!=5 or len(set(top))!=5 or not set(top)<=set(types) or not targets<=set(types) or len(targets)!=len(target_list):
                raise ValueError("Figure 10 type identifiers")
            flags = [c in targets for c in top]
            if flags != ast.literal_eval(row.target_at_top5):
                raise ValueError("Figure 10 target flags")
            if targets:
                if not any(flags):
                    raise ValueError("First target rank not established by this list")
                first = flags.index(True)+1
                if first != row.first or 1/first != row.RR:
                    raise ValueError("Figure 10 first target or reciprocal rank")
            elif not pd.isna(row.first) or row.RR != 0:
                raise ValueError("Figure 10 empty target")
            if case=="A" and row.model==models[0] and row.module_load_rank!=8:
                raise ValueError("Figure 10 A additional rank")
            if case=="C" and (row.network_resolve_connect_rank!=12 or len(targets)!=6):
                raise ValueError("Figure 10 C additional rank")
            if case=="D" and targets:
                raise ValueError("Figure 10 D targets")
            out.append(dict(item="Figure 10",case=case,model=row.model,stored_top5=top,first=int(row.first) if targets else None,RR=row.RR))
        if len(targets_by_model)!=1:
            raise ValueError("Figure 10 target set differs across models")
    labels=pd.read_csv(root/"data/figure8_labels.csv",dtype=str)
    ratios=["0.10","0.20","0.30","0.50"]
    exact_keys(labels,["panel","split","ratio","condition"],set(product(["a"],["Test"],ratios,["all"]))|set(product(["b"],["Validation","Test"],ratios,["0","1"])),"Figure 8 keys")
    s26=read("data/tableS26_printed.csv")
    s54=read("data/tableS54_printed.csv")
    if s26.columns[4]!="[Type-specific LR] − [Pooled LR]" or s54.columns[5]!="[Type-specific LR + relation indicator] − [Type-specific LR]":
        raise ValueError("Figure 8 contrast direction")
    six=read("data/figure6_sums.csv")
    reference=read("results/main/figure6_reference.csv")
    configs=set(reference.model)
    conditions=["RAW_SCORE","OBSERVED_EXCLUDED"]
    if len(configs)!=8:
        raise ValueError("Figure 6 configuration count")
    exact_keys(reference,["model","condition"],set(product(configs,conditions)),"Figure 6 points")
    exact_keys(six,["configuration","condition","fold","seed"],set(product(configs,conditions,[1,2,3],seeds)),"Figure 6 inputs")
    s4=read("data/section_s4_printed.csv")
    budgets=read("results/posthoc/fixed_budgets.csv")
    cells=budgets[(budgets.population=="eligible") & budgets.model.isin(models[:3])]
    expected=set(product([353,762,1667],models[:3]))
    exact_keys(cells,["k","model"],expected,"S4 eligible budget keys")
    exact_keys(s4,["k","model"],expected,"S4 expected cells")
    joined=cells.merge(s4,on=["k","model"],validate="one_to_one")
    for row in joined.itertuples():
        if row.executions!=row.printed_executions or round(row.rr,4)!=row.printed_mrr:
            raise ValueError("S4 fixed-budget count or MRR")
        out.append(dict(item="Section S4",budget=row.k,model=row.model,executions=row.executions,stored_MRR=row.rr,printed_MRR=row.printed_mrr))
    return out
