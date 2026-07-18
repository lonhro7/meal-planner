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
function mostRecentWeekStart(iso, startDay) { const d = parseISO(iso); const diff = (d.getDay() - startDay + 7) % 7; d.setDate(d.getDate() - diff); return isoLocal(d); }
function addDays(iso, n) { const d = parseISO(iso); d.setDate(d.getDate() + n); return isoLocal(d); }
function daysBetween(a, b) { return Math.round((parseISO(b) - parseISO(a)) / 86400000); }
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
    this.getPlan();
    await this.persist();
    if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(() => {});
    return this;
  },

  migrate() {
    const s = this.state.settings;
    if (s.week_start_day == null) s.week_start_day = 0;
    if (!s.day_prefs) s.day_prefs = { 0:"any",1:"any",2:"any",3:"any",4:"any",5:"any",6:"any" };
    if (!s.leftover_mode || s.leftover_mode === "dinners") s.leftover_mode = "auto";
    if (s.high_protein_g == null) s.high_protein_g = 30;
    if (s.low_carb_g == null) s.low_carb_g = 30;
    if (!s.meat_prices) s.meat_prices = {};
    (this.state.pantry || []).forEach((p) => {
      if (p.location == null) p.location = p.is_meat ? "freezer" : "pantry";
      if (p.special_occasion == null) p.special_occasion = false;
    });
  },

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
        day_prefs: { 0:"any",1:"any",2:"any",3:"any",4:"any",5:"any",6:"any" },
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
  // full recipe search: text (title + ingredients), favourited, uses-freezer-meat, dietary, tags
  searchRecipes(opts = {}) {
    const servings = this.state.settings.servings_per_meal;
    const terms = (opts.text || "").toLowerCase().split(/[,\n]/).map((s) => s.trim()).filter(Boolean);
    const f = { high_protein: opts.high_protein, low_carb: opts.low_carb, dairy: opts.dairy,
      leftover_levels: opts.leftover_levels || [], include_tags: opts.tags || [], exclude_tags: opts.exclude_tags || [],
      max_prep_min: opts.max_prep_min, max_cook_min: opts.max_cook_min };
    let out = this.state.recipes.filter((r) => {
      if (opts.favourited && (r.liked || 0) !== 1) return false;
      if (opts.uses_freezer && !this.usesFreezerMeat(r)) return false;
      if (!this.matchesFilter(r, f, servings)) return false;
      if (terms.length) {
        const hay = (r.title + " " + (r.ingredients || []).map((i) => i.name).join(" ") + " " + (r.tags || []).join(" ")).toLowerCase();
        if (!terms.every((t) => hay.includes(t))) return false;
      }
      return true;
    });
    return out.map((r) => ({ ...this.recipeBrief(r), uses_freezer: this.usesFreezerMeat(r) }))
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
    const p = { id, name: item.name || "", category: item.category || "meat", is_meat: item.is_meat !== false,
      meat_type: item.meat_type || "", meat_cut: item.meat_cut || "", quantity: item.quantity || 0,
      unit: item.unit || "g", location: item.location || (item.is_meat === false ? "pantry" : "freezer"),
      special_occasion: !!item.special_occasion };
    this.state.pantry.push(p); await this.persist(); return id;
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
          default_ppu: i.price_per_unit, price: this.state.settings.meat_prices[key] }; }
    }));
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
  freezerMeatTypes() {
    const set = new Set();
    this.state.pantry.forEach((p) => { if (p.is_meat && !p.special_occasion && p.quantity > 0 && p.location === "freezer") set.add(norm(p.meat_type)); });
    return set;
  },
  usesFreezerMeat(recipe) {
    const fz = this.freezerMeatTypes(); if (!fz.size) return false;
    return (recipe.ingredients || []).some((i) => i.is_meat && fz.has(norm(i.meat_type)));
  },
  // meat types the whole current plan needs (for the freezer summary "in use" flag)
  planMeatTypes() {
    const set = new Set();
    const end = addDays(this.state.plan.start_date, this.state.plan.weeks * 7 - 1);
    this.cookingMeals(this.state.plan.start_date, end).forEach(({ recipe }) =>
      (recipe.ingredients || []).forEach((i) => { if (i.is_meat) set.add(norm(i.meat_type)); }));
    return set;
  },
  freezerSummary() {
    const used = this.planMeatTypes();
    const items = this.state.pantry.filter((p) => p.location === "freezer")
      .map((p) => ({ display: this.displayName(p), meat_type: p.meat_type, quantity: p.quantity, unit: p.unit,
        special_occasion: !!p.special_occasion, used_by_plan: p.is_meat && used.has(norm(p.meat_type)) }))
      .sort((a, b) => a.display.localeCompare(b.display));
    return { items, any: items.length > 0 };
  },

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
  mealOut(m) {
    const r = m.recipe_id ? this.recipeById(m.recipe_id) : null;
    return { id: m.id, date: m.date, weekday: weekdayOf(m.date), status: m.status, locked: m.locked,
      servings: m.servings, note: m.note, is_leftover: m.status === "leftover",
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
    if (f.dairy === "free" && r.dairy !== "free") return false;
    if (f.dairy === "free_or_replaceable" && !(r.dairy === "free" || r.dairy === "replaceable")) return false;
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
    out.weight_loss_focus = base.weight_loss_focus || add.weight_loss_focus;
    out.high_protein = base.high_protein || add.high_protein;
    out.low_carb = base.low_carb || add.low_carb;
    if (add.dairy && add.dairy !== "any") out.dairy = add.dairy;
    return out;
  },
  presetFilter(pref) {
    if (pref === "quick") return { max_prep_min: 15, max_cook_min: 25 };
    if (pref === "long") return { min_cook_min: 45 };
    if (pref === "light") return { weight_loss_focus: true };
    return {};
  },
  candidates(f, servings) {
    const ok = this.state.recipes.filter((r) => this.matchesFilter(r, f, servings));
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
    const byDate = {}; this.state.meals.forEach((m) => (byDate[m.date] = m));
    const targetDates = new Set();
    dates.forEach((d) => { const m = byDate[d]; if (m && !m.locked && m.status !== "away") targetDates.add(d); });
    this.state.meals.forEach((m) => { if (targetDates.has(m.date)) { m.recipe_id = null; m.source_meal_id = null; m.status = "empty"; } });

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

      // target slot to fill
      const pref = (s.day_prefs && s.day_prefs[weekdayOf(m.date)]) || "any";

      if (pendingAuto && daysBetween(pendingAuto.date, m.date) >= 1 && daysBetween(pendingAuto.date, m.date) <= 3) {
        const src = this.mealById(pendingAuto.mealId);
        if (src && src.recipe_id) { placeLeftover(m, src); pendingAuto = null; filled++; continue; }
        pendingAuto = null;
      }
      if (pref === "leftover") {
        const src = recentSource(m.date);
        if (src) { placeLeftover(m, src); filled++; continue; }
      }
      const eff = this.mergeFilters(filt || {}, this.presetFilter(pref));
      let choice = this.pick(this.candidates(eff, servings), recent.slice(-4), lastProtein, availMeats);
      if (!choice) choice = this.pick(this.candidates(filt || {}, servings), recent.slice(-4), lastProtein, availMeats);
      if (!choice) continue;
      m.recipe_id = choice.id; m.status = "planned"; recent.push(choice.id); lastProtein = this.primaryProtein(choice);
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
  async swap(id, recipeId) { const m = this.mealById(id); if (m) { m.recipe_id = recipeId; m.status = "planned"; m.source_meal_id = null; await this.persist(); } },
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
    const servings = this.state.settings.servings_per_meal, agg = {};
    for (const { recipe } of pairs) {
      const scale = servings / Math.max(recipe.servings, 1);
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
      const price = row.is_meat ? this.meatPrice(row.meat_type, row.meat_cut, row.price_per_unit) : row.price_per_unit;
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
