#!/usr/bin/env python3
"""Merge sectioned RTE ingredient lists (rtesec/out_*.json) into the seed.

For each RTE recipe, replace its ingredient list with the freshly-fetched one
that carries a `section` (dish-part heading). Quantities are parsed (fractions,
ranges, blanks), prices assigned from the known price map, and step_index is
re-derived by matching each ingredient to the step that first mentions it.
Everything else on the recipe (title, times, nutrition, method) is untouched.
"""
import json, glob, os, re
from collections import Counter

HERE = "/home/claude"
SEEDJS = os.path.join(HERE, "meal-planner-iphone", "seed.js")
UNITS = {"g","ml","tsp","tbsp","clove","whole","can","bunch","sprig","slice","pinch",""}
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
        q = q.strip().replace("–", "-").replace("½", "0.5").replace("¼", "0.25").replace("¾", "0.75")
        if q == "": return 0.0
        m = re.match(r"^([\d./ ]+)\s*-\s*([\d./ ]+)$", q)   # range -> midpoint
        if m:
            a, b = num(m.group(1)), num(m.group(2))
            return round((a + b) / 2, 3) if a is not None and b is not None else None
        try:
            if " " in q:
                a, rest = q.split(" ", 1); nb = num(rest)
                return float(a) + nb if nb is not None else None
            if "/" in q:
                a, b = q.split("/"); return float(a) / float(b)
            return float(q)
        except Exception:
            return None
    return None

_STOP = set(("the and of with for fresh ground tinned dried baby extra light plain free range reduced fat "
             "large small medium whole grated chopped finely roughly sliced diced minced crushed thinly halved "
             "red green white brown boneless bone skinless mild hot sweet to serve").split())
def assign_step(ing, lower_steps):
    kws = []
    for k in (ing.get("meat_cut"), ing.get("meat_type")):
        if k: kws.append(k.lower())
    for w in re.findall(r"[a-z]+", ing["name"].lower()):
        if len(w) > 2 and w not in _STOP: kws.append(w)
    for si, text in enumerate(lower_steps):
        if any(kw in text for kw in kws): return si
    return 0

by_index = {}
for f in sorted(glob.glob(os.path.join(HERE, "rtesec", "out_*.json"))):
    for x in json.load(open(f)):
        by_index[x["index"]] = x

def valid_ings(ov):
    ings = ov.get("ingredients")
    if not isinstance(ings, list) or len(ings) < 2: return False
    for i in ings:
        if i.get("unit") not in UNITS or i.get("category") not in CATS: return False
        if (i.get("meat_type") or "") not in MTYPES: return False
        if num(i.get("quantity")) is None: return False
    return True

updated, out = 0, []
for idx, r in enumerate(seed):
    ov = by_index.get(idx)
    if r.get("source_name") == "RecipeTinEats" and ov and valid_ings(ov):
        lower = [s.lower() for s in r["method_steps"]]
        ings = []
        for i in ov["ingredients"]:
            ings.append({"name": i["name"], "quantity": round(num(i["quantity"]), 3), "unit": i["unit"],
                "category": i["category"], "is_meat": bool(i.get("is_meat")),
                "meat_type": i.get("meat_type","") or "", "meat_cut": i.get("meat_cut","") or "",
                "optional": bool(i.get("optional", False)), "section": (i.get("section") or "").strip(),
                "price_per_unit": round(price_for(i), 4), "step_index": assign_step(i, lower)})
        nr = dict(r); nr["ingredients"] = ings
        out.append(nr); updated += 1
    else:
        out.append(r)

js = ("// Curated recipe library (build_seed.py + apply_overhaul.py + apply_rte.py + apply_sections.py).\n"
      "// Australian family dinners, metric, serve as-sourced. Energy kJ, prices AUD. '(RTE)' = RecipeTinEats.\n"
      "const SEED_RECIPES = " + json.dumps(out, ensure_ascii=False) + ";\n")
open(SEEDJS, "w").write(js)
print(f"recipes given sectioned ingredients: {updated}")
withsec = sum(1 for r in out if any(i.get("section") for i in r["ingredients"]))
print(f"recipes now showing >=1 section heading: {withsec}")
bad = [r["title"] for r in out if any(i["step_index"] >= len(r["method_steps"]) for i in r["ingredients"])]
print("out-of-range step_index:", len(bad))
