"use strict";
/* On-device data + logic layer. All data lives on THIS phone (IndexedDB, with a
   localStorage fallback). Mirrors a server model so a future hosted switch is a
   swap of this layer, not a rewrite. No network required.
   Energy is in kJ. Prices are AUD (meat ~ Australian Meat Emporium, groceries ~
   Woolworths). */

const DB_NAME = "mealplanner";
const STORE = "kv";
const KEY = "state";
const HIGH_PROTEIN_G = 30;   // per serve threshold for the "high protein" filter
const LOW_CARB_G = 30;       // per serve threshold for the "low carb" filter
// Leftovers are three named levels. Score drives auto-leftover eligibility.
const LEFTOVER_LEVELS = ["fresh", "ok", "excellent"];   // "best fresh" / "ok" / "excellent"
const LEFTOVER_SCORE = { fresh: 0, ok: 2, excellent: 3 };
function leftoverScore(r) { return LEFTOVER_SCORE[(r && r.leftover) || "fresh"] || 0; }
const MEAT_TYPES = ["Beef","Chicken","Lamb","Pork","Sausage","Smallgoods","Fish","Other"];
const LEFTOVER_LABELS = { fresh: "Best fresh", ok: "OK leftovers", excellent: "Excellent leftovers" };
// day-preference rows. Each is a Yes(green)/No(red) toggle per weekday. Green = allowed,
// red = excluded. All default green EXCEPT "nocook" which defaults red (i.e. cook, not free).
// Order is the on-screen order.
const DAY_PREF_OPTIONS = [["quick","Quick and easy"],["slowcook","Early prep / slow cook"],["long","Long cook"],["light","Light"],["leftover","Leftover night"],["nocook","No cook"]];
// True when a row is green (allowed) for a day. Absent = default: green for all rows, red for "nocook".
function dayGreen(dp, key) { const v = (dp || {})[key]; if (v === undefined) return key !== "nocook"; return !!v; }
const AVG_SAUSAGE_KG = 0.1;  // assumed weight per sausage, for $/kg pricing of sausages
// approx weight per piece (kg) for cuts counted "whole" in recipes, so they can be priced $/kg
const PIECE_KG = {
  "chicken|thigh cutlet": 0.15, "chicken|drumstick": 0.1, "chicken|maryland": 0.35,
  "lamb|cutlet": 0.05, "lamb|loin chop": 0.12, "lamb|shank": 0.35, "lamb|forequarter chop": 0.15,
  "pork|loin chop": 0.15, "pork|cutlet": 0.2,
  "salmon|fillet": 0.16, "fish|white fillet": 0.15,
};
// curated cut lists per meat type (merged with recipe cuts + AME cuts at runtime)
const CURATED_CUTS = {
  beef: ["mince","chuck","rump","rump whole","rump steak","porterhouse steak","scotch fillet","eye fillet","eye fillet whole","blade","oyster blade","brisket","topside","silverside","corned silverside","gravy beef","osso bucco","stir-fry strips","minute steak","skirt","flank","short ribs","ribs"],
  chicken: ["mince","breast","thigh fillet","thigh cutlet","drumstick","wings","whole","tenderloins","maryland"],
  lamb: ["mince","leg (bone in)","leg (boneless)","leg steak","shoulder (bone in)","shoulder (boneless)","shank","cutlet","loin chop","forequarter chop","backstrap","rack"],
  pork: ["mince","loin","loin chop","loin steak","belly","shoulder (bone in)","shoulder (boneless)","scotch fillet","leg (bone in)","leg (boneless)","ribs","cutlet","schnitzel steak"],
  sausage: ["plain","flavoured","pork sausage","beef sausage","pork & fennel","italian","chorizo","chicken","bratwurst","lamb & rosemary","honey & garlic","sausage mince"],
  smallgoods: ["bacon","sliced ham","ham hock","chorizo","prosciutto","salami","kransky","pancetta"],
  fish: ["white fillet","barramundi fillet","cod fillet","snapper fillet","whole snapper","prawn","smoked fillet","marinara mix"],
  salmon: ["fillet","smoked"],
  other: [],
};
// recommended max freezer storage (months) by meat type / cut — used to auto-set best-before
function freezerMonths(type, cut) {
  type = (type || "").toLowerCase(); cut = (cut || "").toLowerCase();
  if (cut.includes("mince")) return 3;
  if (type === "sausage") return 2;
  if (type === "smallgoods") return 1;
  if (type === "salmon") return 3;
  if (type === "fish") return 4;
  if (type === "chicken") return cut.includes("whole") ? 12 : 9;
  if (type === "pork") return 6;
  if (type === "lamb") return 8;
  if (type === "beef") return 8;
  return 6;
}

// ------------------------------------------------------------- persistence
function openDB() {
  return new Promise((resolve, reject) => {
    if (!("indexedDB" in window)) return reject(new Error("no-idb"));
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}
async function idbGet() {
  try {
    const db = await openDB();
    return await new Promise((res, rej) => {
      const r = db.transaction(STORE).objectStore(STORE).get(KEY);
      r.onsuccess = () => res(r.result || null); r.onerror = () => rej(r.error);
    });
  } catch (_) { const raw = localStorage.getItem(DB_NAME); return raw ? JSON.parse(raw) : null; }
}
async function idbSet(value) {
  try {
    const db = await openDB();
    await new Promise((res, rej) => {
      const r = db.transaction(STORE, "readwrite").objectStore(STORE).put(value, KEY);
      r.onsuccess = () => res(); r.onerror = () => rej(r.error);
    });
  } catch (_) { localStorage.setItem(DB_NAME, JSON.stringify(value)); }
}

// ------------------------------------------------------------- helpers
function isoLocal(d) { const y = d.getFullYear(), m = String(d.getMonth() + 1).padStart(2, "0"), day = String(d.getDate()).padStart(2, "0"); return `${y}-${m}-${day}`; }
function parseISO(iso) { return new Date(iso + "T00:00:00"); }
function todayISO() { return isoLocal(new Date()); }
function weekdayOf(iso) { return parseISO(iso).getDay(); }               // 0 Sun .. 6 Sat

// Build progressively looser search queries from a recipe title, for matching a
// dish photo on TheMealDB. Drops a trailing "with …" side, "&", and filler words.
const IMG_FILLER = /\b(slow[- ]?cooked|slow cooker|easy|quick|classic|creamy|homemade|home[- ]?made|simple|best|family|hearty|one[- ]?pan|one[- ]?pot|sheet[- ]?pan|oven[- ]?baked|oven|baked|grilled|pan[- ]?fried|roast(ed)?|our|the|and|style|with)\b/g;
function imageQueries(title) {
  const base = (title || "").toLowerCase();
  const noSide = base.split(/\bwith\b/)[0];
  const clean = noSide.replace(/&/g, " ").replace(IMG_FILLER, " ").replace(/[^a-z\s]/g, " ").replace(/\s+/g, " ").trim();
  const words = clean.split(" ").filter(Boolean);
  const cand = [clean, words.slice(0, 3).join(" "), words.slice(0, 2).join(" "), words.slice(-2).join(" ")];
  return [...new Set(cand.map((s) => s.trim()).filter((s) => s.length >= 3))];
}
function mostRecentWeekStart(iso, startDay) { const d = parseISO(iso); const diff = (d.getDay() - startDay + 7) % 7; d.setDate(d.getDate() - diff); return isoLocal(d); }
function addDays(iso, n) { const d = parseISO(iso); d.setDate(d.getDate() + n); return isoLocal(d); }
function daysBetween(a, b) { return Math.round((parseISO(b) - parseISO(a)) / 86400000); }
function addMonthsISO(iso, months) { const d = parseISO(iso); d.setMonth(d.getMonth() + months); return isoLocal(d); }
function clone(o) { return JSON.parse(JSON.stringify(o)); }
function norm(s) { return (s || "").trim().toLowerCase(); }
function cutMatch(a, b) { a = norm(a); b = norm(b); if (!a || !b) return true; return a === b || a.includes(b) || b.includes(a); }

// ------------------------------------------------------------- the store
const Store = {
  state: null,
  MEAT_TYPES,
  LEFTOVER_LEVELS,
  LEFTOVER_LABELS,

  async init() {
    let s = await idbGet();
    if (!s || !s.recipes) s = this.freshState();
    this.state = s;
    this.migrate();
    await this.loadAmePrices();
    this.getPlan();
    await this.persist();
    if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(() => {});
    return this;
  },
  // AME default prices (refreshed by a scheduled GitHub Action; overrides still win)
  async loadAmePrices() {
    try { const res = await fetch("./data/ame-prices.json", { cache: "no-store" }); if (res.ok) this.amePrices = await res.json(); }
    catch (_) { /* offline or missing — fall back to estimates */ }
  },
  ameKg(type, cut) { const m = this.amePrices && this.amePrices.kg_prices; return m ? m[norm(type) + "|" + norm(cut)] : undefined; },
  pieceKg(type, cut) { return PIECE_KG[norm(type) + "|" + norm(cut)] || 0; },
  // default price-per-unit for a cut: AME $/kg (if known) converted to the cut's unit, else fallback
  defaultPPU(type, cut, unit, fallback) {
    const kg = this.ameKg(type, cut);
    if (kg == null) return fallback;
    if (unit === "g") return kg / 1000;
    if (norm(type) === "sausage") return kg * AVG_SAUSAGE_KG;
    const w = this.pieceKg(type, cut);
    if (unit === "whole" && w) return kg * w;   // priced $/kg, costed per piece via avg weight
    return fallback;
  },
  meatPriceResolved(type, cut, unit, fallback) {
    const ov = this.state.settings.meat_prices[norm(type) + "|" + norm(cut)];
    return ov != null ? ov : this.defaultPPU(type, cut, unit, fallback);
  },
  // cut options for a meat type (curated ∪ recipe cuts ∪ AME cuts)
  cutsForType(type) {
    const t = norm(type);
    const set = new Set((CURATED_CUTS[t] || []).map((c) => c));
    this.state.recipes.forEach((r) => (r.ingredients || []).forEach((i) => { if (i.is_meat && norm(i.meat_type) === t && i.meat_cut) set.add(i.meat_cut); }));
    if (this.amePrices && this.amePrices.kg_prices) Object.keys(this.amePrices.kg_prices).forEach((k) => { const [kt, kc] = k.split("|"); if (kt === t && kc) set.add(kc); });
    let arr = [...set].map((c) => c.trim()).filter(Boolean);
    // if a cut has (bone in)/(boneless) variants, drop the plain generic (e.g. "shoulder")
    const bases = new Set();
    arr.forEach((c) => { const m = c.match(/^(.*) \((?:bone in|boneless)\)$/); if (m) bases.add(m[1]); });
    return arr.filter((c) => !bases.has(c)).sort((a, b) => a.localeCompare(b));
  },

  migrate() {
    const s = this.state.settings;
    if (s.week_start_day == null) s.week_start_day = 0;
    if (!s.day_prefs) s.day_prefs = { 0:{},1:{},2:{},3:{},4:{},5:{},6:{} };
    // day prefs are now per-row Yes/No objects; convert any older string/array form to {}
    for (let d = 0; d < 7; d++) {
      const v = s.day_prefs[d];
      if (v == null || Array.isArray(v) || typeof v !== "object") s.day_prefs[d] = {};
    }
    if (!s.leftover_mode || s.leftover_mode === "dinners") s.leftover_mode = "auto";
    if (s.high_protein_g == null) s.high_protein_g = 30;
    if (s.low_carb_g == null) s.low_carb_g = 30;
    if (!s.meat_prices) s.meat_prices = {};
    if (!s.meat_max_pct) s.meat_max_pct = {};        // e.g. { beef: 40 } = beef on at most 40% of dinners
    if (!s.meat_allowed_cuts) s.meat_allowed_cuts = {}; // e.g. { pork: ["belly","leg (bone in)"] } = only those cuts
    (this.state.pantry || []).forEach((p) => {
      if (p.location == null) p.location = p.is_meat ? "freezer" : "pantry";
      if (p.special_occasion == null) p.special_occasion = false;
      if (p.purchase_date === undefined) p.purchase_date = "";
      if (p.best_before === undefined) p.best_before = "";
    });
  },
  DAY_PREF_OPTIONS,
  freezerMonths,

  freshState() {
    const recipes = SEED_RECIPES.map((r, i) => ({ id: i + 1, liked: 0, times_cooked: 0, ...clone(r) }));
    const start = mostRecentWeekStart(todayISO(), 0);
    return {
      schema: 2, recipes, pantry: [],
      plan: { start_date: start, weeks: 4 }, meals: [],
      settings: {
        household_adults: 2, household_children: 2, servings_per_meal: 4,
        weekly_budget: 0, leftover_mode: "auto", week_start_day: 0,
        high_protein_g: 30, low_carb_g: 30, meat_prices: {},
        meat_max_pct: {}, meat_allowed_cuts: {},
        day_prefs: { 0:{},1:{},2:{},3:{},4:{},5:{},6:{} },
      },
      seq: { recipe: recipes.length + 1, pantry: 1, meal: 1 },
    };
  },
  async persist() { await idbSet(this.state); },

  // ---------------------------------------------------------- settings
  getSettings() { return clone(this.state.settings); },
  async saveSettings(s) { Object.assign(this.state.settings, s); this.getPlan(); await this.persist(); },

  // ---------------------------------------------------------- recipes
  recipeById(id) { return this.state.recipes.find((r) => r.id === id) || null; },
  primaryProtein(r) { const m = (r.ingredients || []).find((i) => i.is_meat && i.meat_type); return m ? norm(m.meat_type) : ""; },
  totalMin(r) { return (r.prep_min || 0) + (r.cook_min || 0); },
  recipeBrief(r) {
    return { id: r.id, title: r.title, total_min: this.totalMin(r), prep_min: r.prep_min, cook_min: r.cook_min,
      leftover: r.leftover || "fresh", leftover_label: LEFTOVER_LABELS[r.leftover || "fresh"],
      weight_loss_rating: r.weight_loss_rating, kj: r.kj || 0,
      protein_g: r.protein_g || 0, carbs_g: r.carbs_g || 0, fat_g: r.fat_g || 0, dairy: r.dairy || "required",
      tags: r.tags || [], liked: r.liked || 0, source_name: r.source_name || "", source_url: r.source_url || "" };
  },
  listRecipes() { return this.state.recipes.map((r) => this.recipeBrief(r)).sort((a, b) => a.title.localeCompare(b.title)); },
  getRecipe(id) {
    const r = this.recipeById(id); if (!r) return null;
    return { ...this.recipeBrief(r), servings: r.servings, method_steps: r.method_steps || [], ingredients: clone(r.ingredients || []) };
  },
  async likeRecipe(id, v) { const r = this.recipeById(id); if (r) { r.liked = Math.max(-1, Math.min(1, v)); await this.persist(); } },

  // ---- dish photos (auto-fetched per dish from TheMealDB, cached on device) ----
  // Returns {status, url}. status: "ready" (have a url), "none" (searched, nothing),
  // "offline" (couldn't reach the source — safe to retry later). Once fetched the
  // image URLs are stored on the recipe and the service worker caches the picture
  // itself, so it shows offline next time.
  recipeImageUrl(id) { const r = this.recipeById(id); return (r && r.image_url) || ""; },
  recipeImageCount(id) { const r = this.recipeById(id); return (r && r.image_candidates || []).length; },
  async resolveRecipeImage(id) {
    const r = this.recipeById(id); if (!r) return { status: "none", url: "", count: 0 };
    if (r.image_url) return { status: "ready", url: r.image_url, count: (r.image_candidates || []).length };
    if (r.image_none) return { status: "none", url: "", count: 0 };
    if (typeof fetch !== "function") return { status: "offline", url: "", count: 0 };
    let reached = false;
    for (const q of imageQueries(r.title)) {
      try {
        const res = await fetch("https://www.themealdb.com/api/json/v1/1/search.php?s=" + encodeURIComponent(q));
        if (!res.ok) continue;
        reached = true;
        const data = await res.json();
        const thumbs = ((data && data.meals) || []).map((m) => m.strMealThumb).filter(Boolean);
        if (thumbs.length) {
          r.image_candidates = [...new Set(thumbs)]; r.image_idx = 0; r.image_url = r.image_candidates[0];
          delete r.image_none; await this.persist();
          return { status: "ready", url: r.image_url, count: r.image_candidates.length };
        }
      } catch (e) { /* network / CORS — try next query, then report offline */ }
    }
    if (reached) { r.image_none = true; await this.persist(); return { status: "none", url: "", count: 0 }; }
    return { status: "offline", url: "", count: 0 };   // never reached the source; don't cache a negative
  },
  // Cycle to another candidate photo (when a search returned several dishes).
  async cycleRecipeImage(id) {
    const r = this.recipeById(id); const c = r && r.image_candidates;
    if (!c || c.length < 2) return { status: r && r.image_url ? "ready" : "none", url: (r && r.image_url) || "", count: (c || []).length };
    r.image_idx = ((r.image_idx || 0) + 1) % c.length; r.image_url = c[r.image_idx];
    await this.persist(); return { status: "ready", url: r.image_url, count: c.length };
  },
  // Hide the photo for this dish (marks it as "no photo" so it won't refetch).
  async clearRecipeImage(id) {
    const r = this.recipeById(id); if (!r) return;
    r.image_url = ""; r.image_candidates = []; r.image_idx = 0; r.image_none = true; await this.persist();
  },
  // Let the user ask for a fresh search after hiding/removing a photo.
  async retryRecipeImage(id) {
    const r = this.recipeById(id); if (!r) return { status: "none", url: "" };
    r.image_url = ""; r.image_candidates = []; r.image_idx = 0; delete r.image_none; await this.persist();
    return this.resolveRecipeImage(id);
  },
  // full recipe search: text (title + ingredients), favourited, uses-freezer-meat, dietary, tags
  searchRecipes(opts = {}) {
    const servings = this.state.settings.servings_per_meal;
    const terms = (opts.text || "").toLowerCase().split(/[,\n]/).map((s) => s.trim()).filter(Boolean);
    const f = { high_protein: opts.high_protein, low_carb: opts.low_carb, dairy_levels: opts.dairy_levels || [],
      leftover_levels: opts.leftover_levels || [], include_tags: opts.tags || [], exclude_tags: opts.exclude_tags || [],
      max_prep_min: opts.max_prep_min, max_cook_min: opts.max_cook_min };
    let out = this.state.recipes.filter((r) => {
      if (opts.favourited && (r.liked || 0) !== 1) return false;
      if (opts.uses_freezer && !this.usesFreezerMeat(r)) return false;
      if (opts.uses_fridge && !this.usesFridgeMeat(r)) return false;
      if (!this.matchesFilter(r, f, servings)) return false;
      if (terms.length) {
        const hay = (r.title + " " + (r.ingredients || []).map((i) => i.name).join(" ") + " " + (r.tags || []).join(" ")).toLowerCase();
        if (!terms.every((t) => hay.includes(t))) return false;
      }
      return true;
    });
    return out.map((r) => ({ ...this.recipeBrief(r), uses_freezer: this.usesFreezerMeat(r), uses_fridge: this.usesFridgeMeat(r) }))
      .sort((a, b) => (b.liked - a.liked) || a.title.localeCompare(b.title));
  },
  async addRecipe(data) {
    const id = this.state.seq.recipe++;
    this.state.recipes.push({ id, title: data.title, liked: 0, times_cooked: 0,
      source_name: data.source_name || "My recipes", source_url: "", servings: data.servings || 4,
      prep_min: data.prep_min || 0, cook_min: data.cook_min || 0,
      weight_loss_rating: data.weight_loss_rating || 3, kid_friendly: data.kid_friendly !== false,
      kj: data.kj || 0, protein_g: data.protein_g || 0, carbs_g: data.carbs_g || 0, fat_g: data.fat_g || 0,
      leftover: data.leftover || "fresh", dairy: data.dairy || "required",
      method_steps: data.method_steps || [], tags: data.tags || [], ingredients: data.ingredients || [] });
    await this.persist(); return id;
  },

  // ---------------------------------------------------------- pantry / stock
  displayName(p) { return p.is_meat ? [p.meat_type, p.meat_cut].filter(Boolean).join(" · ") : p.name; },
  getPantry() {
    return clone(this.state.pantry).map((p) => ({ ...p, display: this.displayName(p) }))
      .sort((a, b) => (a.category + a.display).localeCompare(b.category + b.display));
  },
  async addPantry(item) {
    const id = this.state.seq.pantry++;
    const isMeat = item.is_meat !== false;
    const location = item.location || (isMeat ? "freezer" : "pantry");
    let best_before = item.best_before || "";
    // auto best-before for freezer meat when a purchase date is given
    if (!best_before && item.purchase_date && isMeat && location === "freezer") {
      best_before = addMonthsISO(item.purchase_date, freezerMonths(item.meat_type, item.meat_cut));
    }
    const p = { id, name: item.name || "", category: item.category || "meat", is_meat: isMeat,
      meat_type: item.meat_type || "", meat_cut: item.meat_cut || "", quantity: item.quantity || 0,
      unit: item.unit || "g", location, special_occasion: !!item.special_occasion,
      purchase_date: item.purchase_date || "", best_before };
    this.state.pantry.push(p); await this.persist(); return id;
  },
  // preview the auto best-before a freezer meat item would get (for the UI)
  autoBestBefore(meat_type, meat_cut, purchase_date, location) {
    if (!purchase_date || location !== "freezer") return "";
    return addMonthsISO(purchase_date, freezerMonths(meat_type, meat_cut));
  },
  async deletePantry(id) { this.state.pantry = this.state.pantry.filter((p) => p.id !== id); await this.persist(); },
  // meat types available to the auto-planner (excludes special-occasion, reserved stock)
  availableMeatTypes() {
    const set = new Set();
    this.state.pantry.forEach((p) => { if (p.is_meat && !p.special_occasion && p.quantity > 0) set.add(norm(p.meat_type)); });
    return set;
  },
  // distinct meat type+cut used across recipes, with default price + any user override
  getMeatCuts() {
    const map = {};
    this.state.recipes.forEach((r) => (r.ingredients || []).forEach((i) => {
      if (i.is_meat) { const key = norm(i.meat_type) + "|" + norm(i.meat_cut);
        if (!map[key]) map[key] = { key, type: i.meat_type, cut: i.meat_cut, unit: i.unit,
          default_ppu: this.defaultPPU(i.meat_type, i.meat_cut, i.unit, i.price_per_unit),
          price: this.state.settings.meat_prices[key], ame: this.ameKg(i.meat_type, i.meat_cut) != null }; }
    }));
    // add AME cuts not used in any recipe (e.g. whole muscle vs steak) so both can be priced
    if (this.amePrices && this.amePrices.kg_prices) Object.entries(this.amePrices.kg_prices).forEach(([key, kg]) => {
      if (!map[key]) { const [type, cut] = key.split("|");
        map[key] = { key, type, cut, unit: "g", default_ppu: kg / 1000, price: this.state.settings.meat_prices[key], ame: true }; }
    });
    return Object.values(map).sort((a, b) => (a.type + a.cut).localeCompare(b.type + b.cut));
  },
  meatPrice(type, cut, fallback) {
    const ov = this.state.settings.meat_prices[norm(type) + "|" + norm(cut)];
    return ov != null ? ov : fallback;
  },
  async setMeatPrice(key, value) {
    if (value == null || value === "" || isNaN(value)) delete this.state.settings.meat_prices[key];
    else this.state.settings.meat_prices[key] = Number(value);
    await this.persist();
  },
  locationMeatTypes(location) {
    const set = new Set();
    this.state.pantry.forEach((p) => { if (p.is_meat && !p.special_occasion && p.quantity > 0 && p.location === location) set.add(norm(p.meat_type)); });
    return set;
  },
  freezerMeatTypes() { return this.locationMeatTypes("freezer"); },
  fridgeMeatTypes() { return this.locationMeatTypes("fridge"); },
  usesFreezerMeat(recipe) {
    const fz = this.freezerMeatTypes(); if (!fz.size) return false;
    return (recipe.ingredients || []).some((i) => i.is_meat && fz.has(norm(i.meat_type)));
  },
  usesFridgeMeat(recipe) {
    const fr = this.fridgeMeatTypes(); if (!fr.size) return false;
    return (recipe.ingredients || []).some((i) => i.is_meat && fr.has(norm(i.meat_type)));
  },
  // meat types the whole current plan needs (for the freezer summary "in use" flag)
  planMeatTypes() {
    const set = new Set();
    const end = addDays(this.state.plan.start_date, this.state.plan.weeks * 7 - 1);
    this.cookingMeals(this.state.plan.start_date, end).forEach(({ recipe }) =>
      (recipe.ingredients || []).forEach((i) => { if (i.is_meat) set.add(norm(i.meat_type)); }));
    return set;
  },
  locationSummary(location) {
    const used = this.planMeatTypes();
    const today = todayISO();
    const items = this.state.pantry.filter((p) => p.location === location)
      .map((p) => ({ id: p.id, display: this.displayName(p), meat_type: p.meat_type, quantity: p.quantity, unit: p.unit,
        special_occasion: !!p.special_occasion, best_before: p.best_before || "",
        days_left: p.best_before ? daysBetween(today, p.best_before) : null,
        used_by_plan: p.is_meat && used.has(norm(p.meat_type)) }))
      .sort((a, b) => a.display.localeCompare(b.display));
    return { items, any: items.length > 0 };
  },
  freezerSummary() { return this.locationSummary("freezer"); },
  fridgeSummary() { return this.locationSummary("fridge"); },

  // ---------------------------------------------------------- plan lifecycle
  mealByDate(date) { return this.state.meals.find((m) => m.date === date); },
  mealById(id) { return this.state.meals.find((m) => m.id === id); },
  ensureSlots() {
    const existing = new Set(this.state.meals.map((m) => m.date));
    for (let i = 0; i < this.state.plan.weeks * 7; i++) {
      const d = addDays(this.state.plan.start_date, i);
      if (!existing.has(d)) this.state.meals.push({ id: this.state.seq.meal++, date: d, recipe_id: null,
        status: "empty", locked: false, source_meal_id: null, servings: this.state.settings.servings_per_meal, note: "" });
    }
  },
  roll() {
    const wsd = this.state.settings.week_start_day || 0;
    const cur = mostRecentWeekStart(todayISO(), wsd);
    const aligned = weekdayOf(this.state.plan.start_date) === wsd;
    if (!aligned || daysBetween(this.state.plan.start_date, cur) > 0) {
      this.state.meals = this.state.meals.filter((m) => daysBetween(m.date, cur) <= 0);
      this.state.plan.start_date = cur;
    }
  },
  getPlan() {
    this.roll(); this.ensureSlots();
    const start = this.state.plan.start_date, weeksN = this.state.plan.weeks;
    const meals = [...this.state.meals].sort((a, b) => a.date.localeCompare(b.date));
    const weeks = [];
    for (let w = 0; w < weeksN; w++) {
      const ws = addDays(start, w * 7), we = addDays(start, w * 7 + 7);
      weeks.push({ week_start: ws, meals: meals.filter((m) => m.date >= ws && m.date < we).map((m) => this.mealOut(m)) });
    }
    return { start_date: start, weeks_count: weeksN, weeks, today: todayISO(), settings: this.getSettings() };
  },
  // Effective servings for a night. A cook night that feeds one or more leftover
  // nights is scaled up so the original batch covers them all (e.g. serves 4 that
  // feeds one leftover night -> cook 8). Derived, so it always reflects the current
  // plan with no stale state. Leftover/away nights just use their own servings.
  mealServings(m) {
    const dflt = this.state.settings.servings_per_meal;
    const base = m.servings || dflt;
    if (m.status !== "planned") return base;
    const extra = this.state.meals.reduce((n, x) =>
      (x.status === "leftover" && x.source_meal_id === m.id) ? n + (x.servings || dflt) : n, 0);
    return base + extra;
  },
  mealOut(m) {
    const r = m.recipe_id ? this.recipeById(m.recipe_id) : null;
    const base = m.servings || this.state.settings.servings_per_meal;
    const eff = this.mealServings(m);
    return { id: m.id, date: m.date, weekday: weekdayOf(m.date), status: m.status, locked: m.locked,
      servings: eff, base_servings: base, extra_for_leftovers: Math.max(0, eff - base),
      note: m.note, is_leftover: m.status === "leftover",
      recipe: r ? this.recipeBrief(r) : null };
  },

  // ---------------------------------------------------------- filtering
  recipeCost(r, servings) { const s = servings / Math.max(r.servings, 1); return Math.round((r.ingredients || []).reduce((a, i) => a + i.quantity * s * (i.price_per_unit || 0), 0) * 100) / 100; },
  matchesFilter(r, f, servings) {
    if (f.max_prep_min != null && r.prep_min > f.max_prep_min) return false;
    if (f.max_cook_min != null && r.cook_min > f.max_cook_min) return false;
    if (f.min_cook_min != null && r.cook_min < f.min_cook_min) return false;
    if ((f.leftover_levels || []).length && !f.leftover_levels.includes(r.leftover || "fresh")) return false;
    if (f.weight_loss_focus && r.weight_loss_rating < 4) return false;
    if (f.max_kj != null && (r.kj || 0) > f.max_kj) return false;
    const hp = this.state.settings.high_protein_g ?? HIGH_PROTEIN_G;
    const lc = this.state.settings.low_carb_g ?? LOW_CARB_G;
    if (f.high_protein && (r.protein_g || 0) < hp) return false;
    if (f.low_carb && (r.carbs_g || 0) > lc) return false;
    if (f.kid_friendly_only && !r.kid_friendly) return false;
    // dairy_levels: multi-select of "free" / "replaceable"; empty = any
    if ((f.dairy_levels || []).length && !f.dairy_levels.includes(r.dairy || "required")) return false;
    const tags = new Set(r.tags || []);
    if ((f.include_tags || []).length && !f.include_tags.every((t) => tags.has(t))) return false;
    if ((f.exclude_tags || []).some((t) => tags.has(t))) return false;
    if (f.max_cost != null && this.recipeCost(r, servings) > f.max_cost) return false;
    return true;
  },
  mergeFilters(base, add) {
    const out = { ...base };
    const tighterMax = (a, b) => (a == null ? b : b == null ? a : Math.min(a, b));
    const tighterMin = (a, b) => (a == null ? b : b == null ? a : Math.max(a, b));
    out.max_prep_min = tighterMax(base.max_prep_min, add.max_prep_min);
    out.max_cook_min = tighterMax(base.max_cook_min, add.max_cook_min);
    out.max_kj = tighterMax(base.max_kj, add.max_kj);
    out.max_cost = tighterMax(base.max_cost, add.max_cost);
    out.min_cook_min = tighterMin(base.min_cook_min, add.min_cook_min);
    out.leftover_levels = base.leftover_levels || [];
    out.dairy_levels = base.dairy_levels || [];
    out.weight_loss_focus = base.weight_loss_focus || add.weight_loss_focus;
    out.high_protein = base.high_protein || add.high_protein;
    out.low_carb = base.low_carb || add.low_carb;
    // include-tag requirements from presets (e.g. slow-cook) accumulate
    out.include_tags = [...new Set([...(base.include_tags || []), ...(add.include_tags || [])])];
    return out;
  },
  presetFilter(pref) {
    if (pref === "quick") return { max_prep_min: 15, max_cook_min: 25 };
    if (pref === "long") return { min_cook_min: 45 };
    if (pref === "slowcook") return { include_tags: ["slow-cook"] };
    if (pref === "light") return { weight_loss_focus: true };
    return {};
  },
  // merge a day's list of prefs into one effective filter on top of the base
  applyDayPrefs(base, prefs) {
    let eff = { ...base };
    (prefs || []).forEach((p) => { eff = this.mergeFilters(eff, this.presetFilter(p)); });
    return eff;
  },
  // Does the recipe only use meat cuts the user allows? A meat type with a
  // non-empty allowed-cuts list is restricted to those cuts; others are unrestricted.
  passesCutPrefs(r) {
    const cuts = this.state.settings.meat_allowed_cuts || {};
    for (const ing of r.ingredients || []) {
      if (!ing.is_meat || !ing.meat_type) continue;
      const allowed = cuts[norm(ing.meat_type)];
      if (allowed && allowed.length && !allowed.some((c) => cutMatch(c, ing.meat_cut))) return false;
    }
    return true;
  },
  candidates(f, servings) {
    const ok = this.state.recipes.filter((r) => this.matchesFilter(r, f, servings) && this.passesCutPrefs(r));
    const liked = ok.filter((r) => (r.liked || 0) >= 0);
    return liked.length ? liked : ok;
  },
  pick(cands, recentIds, lastProtein, availMeats) {
    if (!cands.length) return null;
    let pool = cands.filter((r) => !recentIds.includes(r.id)); if (!pool.length) pool = cands;
    const varied = pool.filter((r) => !lastProtein || this.primaryProtein(r) !== lastProtein); if (varied.length) pool = varied;
    const weights = pool.map((r) => {
      let w = 1 + Math.max(r.liked || 0, 0) * 2 + (r.leftover_rating || 0) * 0.2;
      if (availMeats && availMeats.has(this.primaryProtein(r))) w += 2.5;   // prefer using what's in the freezer/stock
      return w;
    });
    const total = weights.reduce((a, b) => a + b, 0); let x = Math.random() * total;
    for (let i = 0; i < pool.length; i++) { x -= weights[i]; if (x <= 0) return pool[i]; }
    return pool[pool.length - 1];
  },

  // ---------------------------------------------------------- generation
  async generate(dates, filt) {
    const s = this.state.settings, servings = s.servings_per_meal, availMeats = this.availableMeatTypes();
    this.getPlan();
    // never touch days before today — past meals stay as they are
    const today = todayISO();
    dates = (dates || []).filter((d) => d >= today);
    const byDate = {}; this.state.meals.forEach((m) => (byDate[m.date] = m));
    // release any previous "no cook" preference days so they can be re-evaluated
    dates.forEach((d) => { const m = byDate[d]; if (m && m.status === "away" && m.note === "nocook-pref") { m.status = "empty"; m.note = ""; } });
    const targetDates = new Set();
    dates.forEach((d) => { const m = byDate[d]; if (m && !m.locked && m.status !== "away") targetDates.add(d); });
    this.state.meals.forEach((m) => { if (targetDates.has(m.date)) { m.recipe_id = null; m.source_meal_id = null; m.status = "empty"; } });

    // --- meat frequency caps (percentage of cooking dinners across the plan) ---
    // Turn each "beef <= 40%" into a hard max count over all cook-able nights, and
    // pre-count meats already fixed on non-target (locked/past) nights.
    const planNights = this.state.meals.filter((m) => {
      if (m.status === "away") return false;
      const pr = (s.day_prefs && s.day_prefs[weekdayOf(m.date)]) || {};
      if (targetDates.has(m.date) && dayGreen(pr, "nocook")) return false;  // green nocook = free night
      return true;
    }).length;
    const maxCount = {};
    for (const [t, p] of Object.entries(s.meat_max_pct || {})) {
      if (p != null && p < 100) maxCount[norm(t)] = Math.floor((p / 100) * planNights);
    }
    const meatCount = {};
    for (const m of this.state.meals) {
      if (targetDates.has(m.date) || m.status !== "planned" || !m.recipe_id) continue;
      const rr = this.recipeById(m.recipe_id); const mt = rr ? (this.primaryProtein(rr) || "vegetarian") : "";
      if (mt) meatCount[mt] = (meatCount[mt] || 0) + 1;
    }
    // strip candidates whose protein has hit its cap (strict — no relaxing to fill).
    // A recipe with no meat counts as "vegetarian" so it can be capped too.
    const freqOk = (list) => list.filter((r) => {
      const mt = this.primaryProtein(r) || "vegetarian";
      if (!(mt in maxCount)) return true;
      return (meatCount[mt] || 0) < maxCount[mt];
    });

    const ordered = [...this.state.meals].sort((a, b) => a.date.localeCompare(b.date));
    let recent = [], lastProtein = "", filled = 0;
    const cooks = [];                 // prior cooks available as leftover sources: {meal, rating, date}
    const usedSources = new Set();
    let pendingAuto = null;           // {mealId, date} awaiting auto leftover placement

    const placeLeftover = (slot, source) => {
      slot.status = "leftover"; slot.recipe_id = source.recipe_id; slot.source_meal_id = source.id;
      usedSources.add(source.id); const r = this.recipeById(slot.recipe_id); lastProtein = r ? this.primaryProtein(r) : "";
    };
    const recentSource = (dateISO) => {
      for (let i = cooks.length - 1; i >= 0; i--) {
        const c = cooks[i]; const gap = daysBetween(c.date, dateISO);
        if (gap >= 1 && gap <= 3 && c.rating >= 2 && !usedSources.has(c.meal.id)) return c.meal;
      }
      return null;
    };

    for (const m of ordered) {
      if (m.status === "away") { lastProtein = ""; continue; }
      if (m.status === "leftover" && !targetDates.has(m.date)) { const r = this.recipeById(m.recipe_id); lastProtein = r ? this.primaryProtein(r) : ""; continue; }
      if (m.recipe_id && !targetDates.has(m.date)) {
        const r = this.recipeById(m.recipe_id); recent.push(m.recipe_id); lastProtein = r ? this.primaryProtein(r) : "";
        cooks.push({ meal: m, rating: r ? leftoverScore(r) : 0, date: m.date }); continue;
      }
      if (!targetDates.has(m.date)) continue;

      // target slot to fill — day preferences are per-row Yes(green)/No(red) toggles
      const dp = (s.day_prefs && s.day_prefs[weekdayOf(m.date)]) || {};
      const green = (k) => dayGreen(dp, k);

      // "No cook" green = free night (nothing cooked or shopped). Default is red (cook).
      if (green("nocook")) { m.status = "away"; m.recipe_id = null; m.source_meal_id = null; m.note = "nocook-pref"; lastProtein = ""; continue; }

      // Leftovers may auto-land here only if the "Leftover night" row is green (default).
      if (pendingAuto && green("leftover") && daysBetween(pendingAuto.date, m.date) >= 1 && daysBetween(pendingAuto.date, m.date) <= 3) {
        const src = this.mealById(pendingAuto.mealId);
        if (src && src.recipe_id) { placeLeftover(m, src); pendingAuto = null; filled++; continue; }
        pendingAuto = null;
      }
      // Style rows: a red row removes that style from this day's options.
      const styleOk = (r) => {
        if (!green("quick") && r.prep_min <= 15 && r.cook_min <= 25) return false;
        if (!green("slowcook") && (r.tags || []).includes("slow-cook")) return false;
        if (!green("long") && r.cook_min >= 45) return false;
        if (!green("light") && (r.weight_loss_rating || 0) >= 4) return false;
        return true;
      };
      const base = freqOk(this.candidates(filt || {}, servings));
      let choice = this.pick(base.filter(styleOk), recent.slice(-4), lastProtein, availMeats);
      if (!choice) choice = this.pick(base, recent.slice(-4), lastProtein, availMeats);   // relax styles rather than leave empty
      if (!choice) continue;   // nothing fits the meat caps/cut rules — leave the night empty
      m.recipe_id = choice.id; m.status = "planned"; recent.push(choice.id); lastProtein = this.primaryProtein(choice);
      const cmt = this.primaryProtein(choice) || "vegetarian"; meatCount[cmt] = (meatCount[cmt] || 0) + 1;
      cooks.push({ meal: m, rating: leftoverScore(choice), date: m.date }); filled++;
      if (s.leftover_mode === "auto" && leftoverScore(choice) >= 3) pendingAuto = { mealId: m.id, date: m.date };
    }
    await this.persist(); return filled;
  },
  async regenerate({ scope, start, end, filter }) {
    this.getPlan();
    const wsd = this.state.settings.week_start_day || 0;
    let dates = [];
    if (scope === "all") dates = this.state.meals.map((m) => m.date);
    else if (scope === "week") { const ws = mostRecentWeekStart(start || todayISO(), wsd); for (let i = 0; i < 7; i++) dates.push(addDays(ws, i)); }
    else if (scope === "day") dates = [start];
    else if (scope === "range") { const n = daysBetween(start, end) + 1; for (let i = 0; i < n; i++) dates.push(addDays(start, i)); }
    return this.generate(dates, filter || {});
  },
  async setLock(id, locked) { const m = this.mealById(id); if (m) { m.locked = locked; await this.persist(); } },
  async swap(id, recipeId) {
    const m = this.mealById(id); if (!m) return;
    m.recipe_id = recipeId; m.status = "planned"; m.source_meal_id = null;
    // any leftover nights fed by this meal now follow the new recipe (or are cleared if it can't do leftovers)
    const r = this.recipeById(recipeId); const canLeftover = r ? leftoverScore(r) >= 2 : false;
    this.state.meals.forEach((x) => {
      if (x.status === "leftover" && x.source_meal_id === m.id) {
        if (canLeftover) { x.recipe_id = recipeId; }
        else { x.status = "empty"; x.recipe_id = null; x.source_meal_id = null; }   // new dish isn't leftover-friendly
      }
    });
    await this.persist();
  },
  // add a recipe to the plan: to a given date, else the first empty (non-away, unlocked) slot
  async addToPlan(recipeId, date) {
    this.getPlan();
    let slot;
    if (date) slot = this.mealByDate(date);
    else slot = [...this.state.meals].sort((a, b) => a.date.localeCompare(b.date))
      .find((m) => m.status === "empty" && !m.locked);
    if (!slot) return null;
    slot.recipe_id = recipeId; slot.status = "planned"; slot.source_meal_id = null;
    await this.persist(); return slot.date;
  },
  async setDayStatus(date, status) {
    const m = this.mealByDate(date); if (!m) return;
    if (status === "away") { m.status = "away"; m.recipe_id = null; m.source_meal_id = null; m.note = ""; }
    else if (m.status === "away") m.status = "empty";
    await this.persist();
  },
  // manual "use these leftovers on…" — target must be 1–3 days after the cook
  eligibleLeftoverDays(sourceMealId) {
    const src = this.mealById(sourceMealId); if (!src || !src.recipe_id) return [];
    const out = [];
    for (let g = 1; g <= 3; g++) {
      const d = addDays(src.date, g); const m = this.mealByDate(d);
      if (m && m.status !== "away" && !m.locked) out.push({ date: d, weekday: weekdayOf(d) });
    }
    return out;
  },
  async setLeftoverPlacement(sourceMealId, targetDate) {
    const src = this.mealById(sourceMealId), tgt = this.mealByDate(targetDate);
    if (!src || !src.recipe_id || !tgt) return;
    const gap = daysBetween(src.date, targetDate); if (gap < 1 || gap > 3) return;
    tgt.status = "leftover"; tgt.recipe_id = src.recipe_id; tgt.source_meal_id = src.id;
    await this.persist();
  },
  // drag reorder within a week: newOrder = recipe_ids (or null) for the draggable slots in date order
  async reorderPlanned(weekStart, newOrder) {
    const we = addDays(weekStart, 7);
    const slots = this.state.meals.filter((m) => m.date >= weekStart && m.date < we && !m.locked && (m.status === "planned" || m.status === "empty"))
      .sort((a, b) => a.date.localeCompare(b.date));
    slots.forEach((m, i) => { const rid = newOrder[i]; if (rid) { m.recipe_id = rid; m.status = "planned"; } else { m.recipe_id = null; m.status = "empty"; } m.source_meal_id = null; });
    await this.persist();
  },

  // ---------------------------------------------------------- shopping/nutrition/cost
  cookingMeals(startISO, endISO) {
    return this.state.meals.filter((m) => m.date >= startISO && m.date <= endISO && m.status === "planned" && m.recipe_id)
      .map((m) => ({ meal: m, recipe: this.recipeById(m.recipe_id) })).filter((x) => x.recipe);
  },
  aggregate(pairs) {
    const dflt = this.state.settings.servings_per_meal, agg = {};
    for (const { meal, recipe } of pairs) {
      const scale = (meal ? this.mealServings(meal) : dflt) / Math.max(recipe.servings, 1);
      for (const ing of recipe.ingredients || []) {
        const key = norm(ing.name) + "|" + ing.unit;
        if (!agg[key]) agg[key] = { name: ing.name, unit: ing.unit, category: ing.category, is_meat: ing.is_meat,
          meat_type: ing.meat_type, meat_cut: ing.meat_cut, needed_qty: 0, price_per_unit: ing.price_per_unit || 0, used_in: [] };
        agg[key].needed_qty += ing.quantity * scale;
        if (!agg[key].used_in.includes(recipe.title)) agg[key].used_in.push(recipe.title);
      }
    }
    return agg;
  },
  pantryHave(row) {   // excludes special-occasion (reserved) stock
    let have = 0;
    for (const p of this.state.pantry) {
      if (p.special_occasion) continue;
      if (p.unit !== row.unit) continue;
      if (row.is_meat && p.is_meat) { if (norm(p.meat_type) === norm(row.meat_type) && cutMatch(p.meat_cut, row.meat_cut)) have += p.quantity; }
      else if (!row.is_meat && !p.is_meat && norm(p.name) === norm(row.name)) have += p.quantity;
    }
    return have;
  },
  buildRows(agg, meatOnly) {
    const rows = [];
    for (const row of Object.values(agg)) {
      if (meatOnly && !row.is_meat) continue;
      if (!meatOnly && row.is_meat) continue;   // groceries exclude meat (meat has its own list/store)
      const needed = Math.round(row.needed_qty * 10) / 10;
      const have = Math.round(this.pantryHave(row) * 10) / 10;
      const buy = Math.max(0, Math.round((needed - have) * 10) / 10);
      const price = row.is_meat ? this.meatPriceResolved(row.meat_type, row.meat_cut, row.unit, row.price_per_unit) : row.price_per_unit;
      rows.push({ name: row.is_meat ? [row.meat_type, row.meat_cut].filter(Boolean).join(" · ") || row.name : row.name,
        unit: row.unit, category: row.category, is_meat: row.is_meat, meat_type: row.meat_type, meat_cut: row.meat_cut,
        needed_qty: needed, have_qty: have, buy_qty: buy, est_cost: Math.round(buy * price * 100) / 100, used_in: row.used_in });
    }
    rows.sort((a, b) => (a.category + a.name).localeCompare(b.category + b.name));
    return rows;
  },
  groceries(weekStart) {   // Woolworths list (no meat)
    const ws = weekStart || mostRecentWeekStart(todayISO(), this.state.settings.week_start_day || 0), we = addDays(ws, 6);
    const rows = this.buildRows(this.aggregate(this.cookingMeals(ws, we)), false).filter((r) => r.buy_qty > 0);
    const total = Math.round(rows.reduce((s, r) => s + r.est_cost, 0) * 100) / 100;
    const byCat = {}; rows.forEach((r) => { (byCat[r.category] = byCat[r.category] || []).push(r); });
    const budget = this.state.settings.weekly_budget;
    return { store: "Woolworths", week_start: ws, week_end: we, items: rows, by_category: byCat,
      estimated_cost: total, weekly_budget: budget, over_budget: budget > 0 && total > budget };
  },
  meat(scope, weekStart) {   // Australian Meat Emporium list
    let start, end;
    if (scope === "week") { start = weekStart || mostRecentWeekStart(todayISO(), this.state.settings.week_start_day || 0); end = addDays(start, 6); }
    else { start = this.state.plan.start_date; end = addDays(start, this.state.plan.weeks * 7 - 1); }
    const rows = this.buildRows(this.aggregate(this.cookingMeals(start, end)), true);
    const toBuy = rows.filter((r) => r.buy_qty > 0);
    return { store: "Australian Meat Emporium", scope, start, end, items: rows, to_buy: toBuy,
      estimated_cost: Math.round(toBuy.reduce((s, r) => s + r.est_cost, 0) * 100) / 100 };
  },
  nutrition(weekStart) {
    const start = weekStart || mostRecentWeekStart(todayISO(), this.state.settings.week_start_day || 0);
    const days = []; const tot = { kj: 0, protein_g: 0, carbs_g: 0, fat_g: 0 }; let cooking = 0;
    for (let i = 0; i < 7; i++) {
      const d = addDays(start, i), m = this.mealByDate(d);
      const e = { date: d, title: null, kj: 0, protein_g: 0, carbs_g: 0, fat_g: 0, status: m ? m.status : "empty" };
      if (m && m.recipe_id && (m.status === "planned" || m.status === "leftover")) {
        const r = this.recipeById(m.recipe_id);
        if (r) { e.title = r.title; e.kj = r.kj; e.protein_g = r.protein_g; e.carbs_g = r.carbs_g; e.fat_g = r.fat_g;
          tot.kj += r.kj; tot.protein_g += r.protein_g; tot.carbs_g += r.carbs_g; tot.fat_g += r.fat_g; cooking++; }
      }
      days.push(e);
    }
    const rnd = (v) => Math.round(v * 10) / 10;
    const avg = cooking ? { kj: Math.round(tot.kj / cooking), protein_g: rnd(tot.protein_g / cooking), carbs_g: rnd(tot.carbs_g / cooking), fat_g: rnd(tot.fat_g / cooking) } : tot;
    return { week_start: start, days, weekly_total: { kj: tot.kj, protein_g: rnd(tot.protein_g), carbs_g: rnd(tot.carbs_g), fat_g: rnd(tot.fat_g) }, daily_average: avg };
  },

  // ---------------------------------------------------------- backup
  exportData() { return { app: "family-meal-planner", schema: 2, exported_at: new Date().toISOString(), state: clone(this.state) }; },
  async importData(obj) {
    const s = obj && obj.state ? obj.state : obj;
    if (!s || !Array.isArray(s.recipes) || !s.plan) throw new Error("This doesn't look like a meal-planner backup.");
    this.state = s;
    if (!this.state.seq) this.state.seq = { recipe: s.recipes.length + 1, pantry: (s.pantry || []).length + 1, meal: (s.meals || []).length + 1 };
    this.migrate(); this.getPlan(); await this.persist();
  },
  async resetAll() { this.state = this.freshState(); this.getPlan(); await this.persist(); },
};

window.Store = Store;
