#!/usr/bin/env python3
"""Apply the recipe-data overhaul (rewrite2/out_*.json) on top of the current seed.

Keeps each recipe's metadata (source, servings, leftover rating, dairy, tags,
weight-loss rating, kid flag) and replaces ingredients / method / nutrition /
times with the improved version — but only if the override passes strict
validation AND preserves the original protein. Anything that fails validation
falls back to the existing recipe so nothing breaks. Deterministic prices are
assigned from the known-good price map, with sensible per-category defaults for
new ingredients (e.g. the spices that blends were broken into).
"""
import json, glob, os, re
from collections import Counter

HERE = "/home/claude"
SEEDJS = os.path.join(HERE, "meal-planner-iphone", "seed.js")

UNITS = {"g","ml","tsp","tbsp","clove","whole","can","bunch","sprig","slice","pinch"}
CATS = {"meat","veg","fruit","dairy","pantry","sauce","spice","bakery"}
MTYPES = {"beef","chicken","lamb","pork","sausage","smallgoods","fish","salmon",""}

def load_seed():
    txt = open(SEEDJS).read()
    return json.loads(txt[txt.index("["):txt.rindex("]")+1])

seed = load_seed()
by_title = {r["title"]: r for r in seed}
price_map = json.load(open(os.path.join(HERE, "rewrite2", "price_map.json")))

# per-(category,unit) fallback price for ingredients not in the known price map
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
    key = f"{ing['name'].strip().lower()}|{ing['unit']}"
    if key in price_map:
        return price_map[key]
    return DEF.get((ing["category"], ing["unit"]), 0.0)

def validate(ov, orig):
    if not isinstance(ov.get("ingredients"), list) or not ov["ingredients"]: return "no ingredients"
    if not isinstance(ov.get("method_steps"), list) or not ov["method_steps"]: return "no steps"
    ns = len(ov["method_steps"])
    for i in ov["ingredients"]:
        if i.get("unit") not in UNITS: return f"unit {i.get('unit')}"
        if i.get("category") not in CATS: return f"cat {i.get('category')}"
        mt = i.get("meat_type","") or ""
        if mt not in MTYPES: return f"mtype {mt}"
        if i.get("is_meat") and not mt: return "meat missing type"
        if not i.get("is_meat") and mt: return "nonmeat has type"
        if not isinstance(i.get("quantity"), (int,float)) or i["quantity"] < 0: return "bad qty"
    # preserve protein: multiset of meat types must match the original
    def mtset(r): return Counter(i.get("meat_type","") for i in r["ingredients"] if i.get("is_meat"))
    if mtset(ov) != mtset(orig): return f"protein changed {dict(mtset(ov))} vs {dict(mtset(orig))}"
    for k in ("kj","protein_g","carbs_g","fat_g","prep_min","cook_min"):
        if not isinstance(ov.get(k), (int,float)): return f"missing {k}"
    if not (500 <= ov["kj"] <= 6000): return f"kj {ov['kj']}"
    return None

# merge overrides
overrides = {}
for f in sorted(glob.glob(os.path.join(HERE, "rewrite2", "out_*.json"))):
    for r in json.load(open(f)):
        overrides[r["title"]] = r

applied, fallbacks, reasons = 0, [], []
out = []
for orig in seed:
    ov = overrides.get(orig["title"])
    reason = validate(ov, orig) if ov else "no override"
    if ov and reason is None:
        ings = []
        ns = len(ov["method_steps"])
        for i in ov["ingredients"]:
            si = i.get("step_index", 0)
            if not isinstance(si, int) or si < 0 or si >= ns: si = 0
            ings.append({
                "name": i["name"], "quantity": i["quantity"], "unit": i["unit"],
                "category": i["category"], "is_meat": bool(i.get("is_meat")),
                "meat_type": i.get("meat_type","") or "", "meat_cut": i.get("meat_cut","") or "",
                "optional": bool(i.get("optional", False)),
                "price_per_unit": round(price_for(i), 4), "step_index": si,
            })
        out.append({
            "title": orig["title"], "source_name": orig.get("source_name","House recipe"),
            "servings": orig["servings"], "prep_min": int(ov["prep_min"]), "cook_min": int(ov["cook_min"]),
            "leftover": orig["leftover"], "weight_loss_rating": orig.get("weight_loss_rating",3),
            "kid_friendly": orig.get("kid_friendly", True),
            "kj": int(round(ov["kj"])), "protein_g": int(round(ov["protein_g"])),
            "carbs_g": int(round(ov["carbs_g"])), "fat_g": int(round(ov["fat_g"])),
            "dairy": orig["dairy"], "tags": orig["tags"],
            "method_steps": ov["method_steps"], "ingredients": ings,
        })
        applied += 1
    else:
        out.append(orig); fallbacks.append(orig["title"]); reasons.append((orig["title"], reason))

js = ("// Curated recipe library (generated by build_seed.py + apply_overhaul.py).\n"
      "// Australian family dinners, metric, serve 4. Energy kJ, prices AUD.\n"
      "const SEED_RECIPES = " + json.dumps(out, ensure_ascii=False) + ";\n")
open(SEEDJS, "w").write(js)

print(f"applied overhaul: {applied}/{len(seed)}   fallbacks: {len(fallbacks)}")
for t, why in reasons[:20]:
    print(f"  fallback: {t}  <- {why}")
# quick integrity check
bad = [r["title"] for r in out if any(i["step_index"] >= len(r["method_steps"]) for i in r["ingredients"])]
print("out-of-range step_index:", len(bad))
print("total ingredient lines:", sum(len(r["ingredients"]) for r in out))
