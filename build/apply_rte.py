#!/usr/bin/env python3
"""Apply matched RecipeTinEats recipes (rte/out_*.json) onto the current seed.

For each dish that matched a real RTE recipe (and passes strict validation), the
recipe is replaced in place (same position/id): title becomes Nagi's title with
" (RTE)", and times / nutrition / ingredients / method come from RTE. The app's
own classification fields (leftover rating, dairy, tags, weight-loss, kid flag)
are kept. Prices are assigned deterministically from the known price map with
per-category defaults. Unmatched or invalid dishes keep their existing recipe.
"""
import json, glob, os
from collections import Counter

HERE = "/home/claude"
SEEDJS = os.path.join(HERE, "meal-planner-iphone", "seed.js")
UNITS = {"g","ml","tsp","tbsp","clove","whole","can","bunch","sprig","slice","pinch"}
CATS = {"meat","veg","fruit","dairy","pantry","sauce","spice","bakery"}
MTYPES = {"beef","chicken","lamb","pork","sausage","smallgoods","fish","salmon",""}

txt = open(SEEDJS).read()
seed = json.loads(txt[txt.index("["):txt.rindex("]")+1])
price_map = json.load(open(os.path.join(HERE, "rewrite2", "price_map.json")))
DEF = {
    ("spice","tsp"):0.05,("spice","tbsp"):0.15,("spice","g"):0.03,("spice","pinch"):0.02,("spice","whole"):0.1,
    ("sauce","tbsp"):0.15,("sauce","tsp"):0.05,("sauce","ml"):0.004,("sauce","g"):0.01,("sauce","can"):1.20,
    ("pantry","g"):0.003,("pantry","ml"):0.004,("pantry","tbsp"):0.10,("pantry","tsp"):0.04,("pantry","can"):1.20,("pantry","whole"):0.30,("pantry","slice"):0.15,
    ("veg","whole"):0.60,("veg","g"):0.006,("veg","clove"):0.08,("veg","bunch"):2.00,("veg","can"):1.20,("veg","sprig"):0.20,("veg","tbsp"):0.05,
    ("dairy","g"):0.014,("dairy","ml"):0.003,("dairy","tbsp"):0.10,("dairy","whole"):0.40,("dairy","slice"):0.30,
    ("bakery","whole"):0.40,("bakery","slice"):0.15,("bakery","g"):0.006,
    ("fruit","whole"):0.50,("fruit","g"):0.008,("fruit","clove"):0.08,
    ("meat","g"):0.020,("meat","whole"):3.00,("meat","slice"):0.40,("meat","can"):2.50,
}
def price_for(ing):
    return price_map.get(f"{ing['name'].strip().lower()}|{ing['unit']}", DEF.get((ing["category"], ing["unit"]), 0.0))

def num(q):
    if isinstance(q, bool): return None
    if isinstance(q, (int, float)): return float(q)
    if isinstance(q, str):
        q = q.strip()
        try:
            if " " in q:  # mixed number like "1 1/2"
                a, b = q.split(" ", 1); nb = num(b); return float(a) + nb if nb is not None else None
            if "/" in q:
                a, b = q.split("/"); return float(a) / float(b)
            return float(q)
        except Exception:
            return None
    return None

def valid(ov):
    if not ov.get("matched"): return False
    if "recipetineats.com" not in (ov.get("rte_url") or ""): return False
    if not (ov.get("new_title") or "").strip(): return False
    if not isinstance(ov.get("ingredients"), list) or not ov["ingredients"]: return False
    if not isinstance(ov.get("method_steps"), list) or not ov["method_steps"]: return False
    for i in ov["ingredients"]:
        if i.get("unit") not in UNITS or i.get("category") not in CATS: return False
        if (i.get("meat_type") or "") not in MTYPES: return False
        if i.get("is_meat") and not (i.get("meat_type") or ""): return False
        q = num(i.get("quantity"))
        if q is None or q < 0: return False
    for k in ("servings","prep_min","cook_min","kj","protein_g","carbs_g","fat_g"):
        if num(ov.get(k)) is None: return False
    if not (500 <= num(ov["kj"]) <= 6000): return False
    return True

by_index = {}
for f in sorted(glob.glob(os.path.join(HERE, "rte", "out_*.json"))):
    for x in json.load(open(f)):
        by_index[x["index"]] = x

applied, out = 0, []
for idx, orig in enumerate(seed):
    ov = by_index.get(idx)
    if ov and valid(ov):
        ns = len(ov["method_steps"])
        ings = []
        for i in ov["ingredients"]:
            si = i.get("step_index", 0)
            if not isinstance(si, int) or si < 0 or si >= ns: si = 0
            ings.append({"name": i["name"], "quantity": round(num(i["quantity"]), 3), "unit": i["unit"],
                "category": i["category"], "is_meat": bool(i.get("is_meat")),
                "meat_type": i.get("meat_type","") or "", "meat_cut": i.get("meat_cut","") or "",
                "optional": bool(i.get("optional", False)),
                "price_per_unit": round(price_for(i), 4), "step_index": si})
        out.append({
            "title": ov["new_title"].strip(), "source_name": "RecipeTinEats", "source_url": ov["rte_url"],
            "servings": int(num(ov["servings"])) or 4, "prep_min": int(num(ov["prep_min"])), "cook_min": int(num(ov["cook_min"])),
            "leftover": orig["leftover"], "weight_loss_rating": orig.get("weight_loss_rating", 3),
            "kid_friendly": orig.get("kid_friendly", True),
            "kj": int(round(num(ov["kj"]))), "protein_g": int(round(num(ov["protein_g"]))),
            "carbs_g": int(round(num(ov["carbs_g"]))), "fat_g": int(round(num(ov["fat_g"]))),
            "dairy": orig["dairy"], "tags": orig["tags"],
            "method_steps": ov["method_steps"], "ingredients": ings})
        applied += 1
    else:
        out.append(orig)

js = ("// Curated recipe library (generated by build_seed.py + apply_overhaul.py + apply_rte.py).\n"
      "// Australian family dinners, metric, serve 4. Energy kJ, prices AUD. '(RTE)' = RecipeTinEats source.\n"
      "const SEED_RECIPES = " + json.dumps(out, ensure_ascii=False) + ";\n")
open(SEEDJS, "w").write(js)

rte_count = sum(1 for r in out if r.get("source_name") == "RecipeTinEats")
print(f"RTE recipes applied: {applied}   total recipes: {len(out)}   now tagged (RTE): {rte_count}")
bad = [r["title"] for r in out if any(i["step_index"] >= len(r["method_steps"]) for i in r["ingredients"])]
print("out-of-range step_index:", len(bad))
