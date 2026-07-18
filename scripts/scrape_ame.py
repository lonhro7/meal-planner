#!/usr/bin/env python3
"""Scrape Australian Meat Emporium (Shopify) prices and write data/ame-prices.json.

Runs on GitHub Actions Mon/Wed/Fri. Reads the public Shopify products feed, maps
each product to a (meat type | cut) key, keeps the cheapest $/kg per key, and
writes the JSON the app loads for default meat pricing. On any failure or a
suspiciously small result it leaves the existing file untouched.
"""
import json, os, re, sys, urllib.request, datetime

BASE = "https://www.meatemporium.com.au/products.json"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "ame-prices.json")
UA = {"User-Agent": "Mozilla/5.0 (meal-planner price updater)"}

SKIP = ("pet", "dog ", " cat", "gift", "voucher", "bundle", "box", "hamper",
        "subscription", "sample", "truffle", "each", "marinated", "pack of")

# plausible $/kg range per meat type — anything outside is treated as a bad parse
# (e.g. a per-each pack price, a per-100g price, or a mislabelled premium product)
BANDS = {
    "beef": (10, 130), "chicken": (5, 26), "lamb": (12, 60), "pork": (8, 36),
    "sausage": (8, 30), "smallgoods": (12, 60), "fish": (14, 60), "salmon": (24, 75),
}

def fetch_all():
    products = []
    for page in range(1, 21):
        url = f"{BASE}?limit=250&page={page}"
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
        ps = data.get("products", [])
        if not ps:
            break
        products.extend(ps)
    return products

def detect_type(t):
    if "salmon" in t: return "salmon"
    if any(w in t for w in ("barramundi","snapper","prawn","cod","flathead","whiting","fish","marinara","seafood","basa","hoki")): return "fish"
    if "sausage" in t or "chipolata" in t or "bratwurst" in t: return "sausage"
    if any(w in t for w in ("bacon","ham","prosciutto","salami","chorizo","kransky","pancetta","pastrami")): return "smallgoods"
    if "chicken" in t: return "chicken"
    if "lamb" in t: return "lamb"
    if "pork" in t: return "pork"
    if any(w in t for w in ("beef","angus","wagyu","porterhouse","scotch","rump","brisket","topside","silverside","sirloin","t-bone","tomahawk","chuck","eye fillet","skirt","flank","osso","gravy beef","oyster blade","minute steak","denver","bavette")): return "beef"
    return ""

def bone_suffix(t):
    if "boneless" in t or "bone out" in t or "deboned" in t: return " (boneless)"
    if "bone in" in t or "bone-in" in t: return " (bone in)"
    return ""

def detect_cut(t, typ):
    whole = "whole" in t
    def W(base): return base + " whole" if whole else base
    if typ == "beef":
        if "mince" in t: return "mince"
        if "corned" in t: return "corned silverside"
        if "silverside" in t: return "silverside"
        if "topside" in t: return "topside"
        if "brisket" in t: return "brisket"
        if "gravy" in t: return "gravy beef"
        if "osso" in t: return "osso bucco"
        if "oyster blade" in t: return "oyster blade"
        if "eye fillet" in t or "tenderloin" in t: return W("eye fillet")
        if "scotch" in t: return "scotch fillet"
        if "porterhouse" in t or "sirloin" in t: return "porterhouse steak"
        if "rump" in t: return "rump steak" if "steak" in t else W("rump")
        if "short rib" in t: return "short ribs"
        if "rib" in t: return "ribs"
        if "skirt" in t: return "skirt"
        if "flank" in t: return "flank"
        if "chuck" in t: return "chuck"
        if "minute" in t: return "minute steak"
        if "strip" in t or "stir" in t: return "stir-fry strips"
        if "steak" in t: return "steak"
        return ""
    if typ == "chicken":
        if "mince" in t: return "mince"
        if "breast" in t: return "breast"
        if "thigh" in t: return "thigh cutlet" if "cutlet" in t or "bone" in t else "thigh fillet"
        if "drumstick" in t: return "drumstick"
        if "wing" in t: return "wings"
        if "maryland" in t: return "maryland"
        if "tender" in t: return "tenderloins"
        if "whole" in t: return "whole"
        return ""
    if typ == "lamb":
        if "mince" in t: return "mince"
        if "shoulder" in t: return "shoulder" + bone_suffix(t)
        if "shank" in t: return "shank"
        if "cutlet" in t: return "cutlet"
        if "backstrap" in t: return "backstrap"
        if "forequarter" in t: return "forequarter chop"
        if "loin chop" in t or ("chop" in t and "loin" in t): return "loin chop"
        if "chop" in t: return "loin chop"
        if "rack" in t: return "rack"
        if "leg" in t: return "leg steak" if "steak" in t else "leg" + bone_suffix(t)
        return ""
    if typ == "pork":
        if "mince" in t: return "mince"
        if "belly" in t: return "belly"
        if "shoulder" in t: return "shoulder" + bone_suffix(t)
        if "scotch" in t: return "scotch fillet"
        if "schnitzel" in t: return "schnitzel steak"
        if "cutlet" in t: return "cutlet"
        if "rib" in t: return "ribs"
        if "loin" in t: return "loin steak" if "steak" in t else ("loin chop" if "chop" in t else "loin")
        if "leg" in t: return "leg" + bone_suffix(t)
        return ""
    if typ == "sausage":
        if "fennel" in t: return "pork & fennel"
        if "italian" in t: return "italian"
        if "chorizo" in t: return "chorizo"
        if "bratwurst" in t: return "bratwurst"
        if "pork" in t: return "pork sausage"
        if "beef" in t: return "beef sausage"
        if "chicken" in t: return "chicken"
        if "lamb" in t: return "lamb & rosemary"
        return "flavoured"
    if typ == "smallgoods":
        for w in ("bacon","prosciutto","salami","chorizo","kransky","pancetta","pastrami"):
            if w in t: return w
        if "hock" in t: return "ham hock"
        if "ham" in t: return "sliced ham"
        return ""
    if typ == "fish":
        if "prawn" in t: return "prawn"
        if "barramundi" in t: return "barramundi fillet"
        if "snapper" in t: return "whole snapper" if whole else "snapper fillet"
        if "cod" in t: return "cod fillet"
        if "marinara" in t: return "marinara mix"
        if "smoked" in t: return "smoked fillet"
        return "white fillet"
    if typ == "salmon":
        if "smoked" in t: return "smoked"
        return "fillet"
    return ""

def main():
    try:
        products = fetch_all()
    except Exception as e:
        print("fetch failed:", e); return 0  # leave existing file untouched
    prices = {}
    for p in products:
        title = (p.get("title") or "").lower()
        if any(s in title for s in SKIP):
            continue
        variants = p.get("variants") or [{}]
        try:
            price = float(variants[0].get("price"))
        except (TypeError, ValueError):
            continue
        typ = detect_type(title)
        if not typ:
            continue
        lo, hi = BANDS.get(typ, (5, 200))
        if price < lo or price > hi:          # outside a sane $/kg band -> bad parse, skip
            continue
        cut = detect_cut(title, typ)
        if not cut:
            continue
        key = f"{typ}|{cut}"
        if key not in prices or price < prices[key]:
            prices[key] = round(price, 2)
    if len(prices) < 15:
        print(f"only {len(prices)} prices parsed — keeping existing file"); return 0
    out = {
        "updated": datetime.date.today().isoformat(),
        "source": "Australian Meat Emporium (meatemporium.com.au)",
        "note": "AUD $/kg, auto-scraped Mon/Wed/Fri. Cheapest listing per cut.",
        "kg_prices": dict(sorted(prices.items())),
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {len(prices)} prices to {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
