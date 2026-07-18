"use strict";
/* UI layer. Talks only to the on-device Store (no network). */

const $ = (id) => document.getElementById(id);
const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const DOW_FULL = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const DAIRY_LEVELS = [["free","Dairy-free"],["replaceable","Dairy replaceable"]];
const SAUSAGE_KG = 0.1;  // assumed weight per sausage, for $/kg pricing
const state = {
  cook: { recipe: null, step: 0, servings: 4 },
  filter: { max_prep_min: null, max_cook_min: null, max_kj: null, max_cost: null,
    weight_loss_focus: false, high_protein: false, low_carb: false, dairy_levels: [],
    leftover_levels: [], exclude_tags: [] },
  search: { text: "", favourited: false, uses_freezer: false, uses_fridge: false, high_protein: false,
    low_carb: false, dairy_levels: [], leftover_levels: [] },
};

function toast(msg) { const t = $("toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 1900); }
function fmtDate(iso) { const d = new Date(iso + "T00:00:00"); return { dow: DOW[d.getDay()], d: d.getDate(), m: MON[d.getMonth()] }; }
function fmtLong(iso) { const f = fmtDate(iso); return `${f.dow} ${f.d} ${f.m}`; }
function qtyLabel(q, unit) { const n = Math.round(q * 10) / 10; const v = Number.isInteger(n) ? n : n.toFixed(1); return unit ? `${v} ${unit}` : `${v}`; }
function trimNum(n) { return String(Math.round(n * 100) / 100); }
// convert to kg / L once past 1000 g / ml (e.g. 1500 g -> "1.5 kg", 2250 g -> "2.25 kg")
function qtyLabelSmart(q, unit) {
  if (unit === "g" && q >= 1000) return `${trimNum(q / 1000)} kg`;
  if (unit === "ml" && q >= 1000) return `${trimNum(q / 1000)} L`;
  return qtyLabel(q, unit);
}

// ---------------------------------------------------------------- tabs
document.querySelectorAll("nav.tabs button").forEach((b) => {
  b.addEventListener("click", () => {
    document.querySelectorAll("nav.tabs button").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
    ["plan", "shopping", "pantry", "recipes", "settings"].forEach((t) => $("tab-" + t).classList.toggle("hidden", t !== b.dataset.tab));
    render(b.dataset.tab);
  });
});
function render(tab) {
  if (tab === "plan") renderPlan();
  else if (tab === "shopping") renderShopping();
  else if (tab === "pantry") renderPantry();
  else if (tab === "recipes") renderRecipes();
  else if (tab === "settings") renderSettings();
}
function goTab(tab) { document.querySelector(`nav.tabs button[data-tab="${tab}"]`).click(); }

// ---------------------------------------------------------------- PLAN
function renderPlan() {
  const p = Store.getPlan();
  $("subtitle").textContent = `Rolling ${p.weeks_count}-week plan · serves ${p.settings.servings_per_meal} · dinners`;
  const f = state.filter;
  const lvBox = (key, label) => `<button type="button" class="chip ${f.leftover_levels.includes(key) ? "on" : ""}" data-lv="${key}">${label}</button>`;
  let html = `<div class="card"><h2>Plan controls</h2>
    <div class="row"><button class="btn primary" id="regenAll">Regenerate whole plan</button>
    <details class="grow"><summary>Filter criteria (applied when regenerating)</summary>
      <div class="filter-panel">
        <div class="row">
          <label class="f">Max prep (min)<input id="f_prep" type="number" min="0" value="${f.max_prep_min ?? ""}" style="width:90px"></label>
          <label class="f">Max cook (min)<input id="f_cook" type="number" min="0" value="${f.max_cook_min ?? ""}" style="width:90px"></label>
          <label class="f">Max kJ/serve<input id="f_kj" type="number" min="0" value="${f.max_kj ?? ""}" style="width:100px"></label>
          <label class="f">Max cost/week $<input id="f_cost" type="number" min="0" value="${f.max_cost ?? ""}" style="width:90px"></label>
        </div>
        <div class="fl"><span class="fl-label">Leftovers (pick any)</span>
          <div class="chips">${lvBox("fresh","Best fresh")}${lvBox("ok","OK")}${lvBox("excellent","Excellent")}</div></div>
        <div class="fl"><span class="fl-label">Dietary</span>
          <div class="chips">
            <button type="button" class="chip ${f.weight_loss_focus?"on":""}" data-tg="weight_loss_focus">Weight-loss</button>
            <button type="button" class="chip ${f.high_protein?"on":""}" data-tg="high_protein">High protein</button>
            <button type="button" class="chip ${f.low_carb?"on":""}" data-tg="low_carb">Low carb</button>
          </div></div>
        <div class="fl"><span class="fl-label">Dairy (pick any)</span><div class="chips">
          ${DAIRY_LEVELS.map(([k,l]) => `<button type="button" class="chip ${f.dairy_levels.includes(k)?"on":""}" data-dl="${k}">${l}</button>`).join("")}</div></div>
        <div class="row"><label class="f grow">Exclude tags (comma)<input id="f_exclude" type="text" value="${f.exclude_tags.join(", ")}" placeholder="fish, pork"></label></div>
      </div></details></div></div>`;

  html += locationCardHtml("fridge") + locationCardHtml("freezer");

  p.weeks.forEach((w, wi) => {
    html += `<div class="week-title">Week ${wi + 1} — from ${fmtLong(w.week_start)} ${wi === 0 ? "· this week" : ""}
      <button class="btn small" data-regenweek="${w.week_start}" style="float:right">↻ week</button></div>
      <div class="card weekcard" data-weekstart="${w.week_start}">`;
    w.meals.forEach((m) => { html += dayRow(m, p.today); });
    html += `</div>`;
  });
  $("tab-plan").innerHTML = html;

  // filter bindings (persist into state.filter)
  const numBind = (id, key) => { const el = $(id); if (el) el.oninput = () => { const v = el.value.trim(); state.filter[key] = v === "" ? null : Number(v); }; };
  numBind("f_prep","max_prep_min"); numBind("f_cook","max_cook_min"); numBind("f_kj","max_kj"); numBind("f_cost","max_cost");
  document.querySelectorAll("[data-dl]").forEach((b) => b.onclick = () => {
    const k = b.dataset.dl, arr = state.filter.dairy_levels, i = arr.indexOf(k);
    if (i >= 0) arr.splice(i, 1); else arr.push(k); b.classList.toggle("on");
  });
  const exc = $("f_exclude"); if (exc) exc.oninput = () => state.filter.exclude_tags = exc.value.split(",").map((s)=>s.trim()).filter(Boolean);
  document.querySelectorAll("[data-lv]").forEach((b) => b.onclick = () => {
    const k = b.dataset.lv, arr = state.filter.leftover_levels, i = arr.indexOf(k);
    if (i >= 0) arr.splice(i, 1); else arr.push(k); b.classList.toggle("on");
  });
  document.querySelectorAll("[data-tg]").forEach((b) => b.onclick = () => { const k = b.dataset.tg; state.filter[k] = !state.filter[k]; b.classList.toggle("on"); });

  $("regenAll").onclick = () => regenerate({ scope: "all" });
  document.querySelectorAll("[data-regenweek]").forEach((b) => b.onclick = () => regenerate({ scope: "week", start: b.dataset.regenweek }));
  wireDayActions();
  document.querySelectorAll(".weekcard").forEach((card) => makeSortable(card, () => commitReorder(card)));
}

function bestBeforeLabel(it) {
  if (!it.best_before) return "";
  const d = it.days_left;
  if (d == null) return "";
  if (d < 0) return `<span class="pill bad" style="margin-left:6px">expired</span>`;
  if (d <= 7) return `<span class="pill bad" style="margin-left:6px">use in ${d}d</span>`;
  if (d <= 30) return `<span class="pill" style="margin-left:6px">best before ${fmtLong(it.best_before)}</span>`;
  return `<span class="small muted" style="margin-left:6px">best before ${fmtLong(it.best_before)}</span>`;
}
function locationCardHtml(location) {
  const icon = location === "fridge" ? "🧊" : "❄️";
  const title = location === "fridge" ? "In the fridge" : "In the freezer";
  const sum = location === "fridge" ? Store.fridgeSummary() : Store.freezerSummary();
  let inner;
  if (!sum.any) inner = `<div class="small muted">Nothing in the ${location}. Add stock under <b>Pantry</b> (set location to ${location === "fridge" ? "Fridge" : "Freezer"}).</div>`;
  else inner = sum.items.map((it) => `<div class="list-item"><span class="name">${icon} ${it.display}
      ${it.special_occasion ? '<span class="small muted">· ⭐ reserved</span>' : (it.used_by_plan ? '<span class="pill good" style="margin-left:6px">in this plan</span>' : "")}${bestBeforeLabel(it)}</span>
      <span class="qty">${qtyLabelSmart(it.quantity, it.unit)}</span></div>`).join("");
  return `<details class="card" open><summary style="font-weight:600;font-size:15px;color:var(--text)">${icon} ${title}</summary>
    <div style="margin-top:8px">${inner}</div></details>`;
}

function dayRow(m, today) {
  const f = fmtDate(m.date); const cls = ["day"];
  if (m.date === today) cls.push("today");
  if (m.status === "away") cls.push("away");
  if (m.status === "leftover") cls.push("leftover");
  const draggable = !m.locked && (m.status === "planned" || m.status === "empty");
  let title, meta = "", tags = "", viewId = null;
  const r = m.recipe;
  if (m.status === "away") { title = m.note === "nocook-pref" ? "🚫 No cook night" : "✈ Away / no cook needed"; if (m.note === "nocook-pref") meta = "Day preference: no cooking"; }
  else if (m.status === "leftover") { title = "♻ Leftovers" + (r ? " — " + r.title : ""); viewId = r ? r.id : null;
    meta = "No cooking or shopping needed" + (r ? ` · ${r.kj} kJ/serve · ${r.protein_g} g protein/serve` : ""); }
  else if (r) { title = r.title; viewId = r.id;
    meta = `${r.total_min} min (prep ${r.prep_min} + cook ${r.cook_min}) · ${r.kj} kJ/serve · ${r.protein_g} g protein/serve`
      + (m.extra_for_leftovers > 0 ? ` · cook ${m.servings} serves (double for leftovers)` : "")
      + (r.leftover !== "fresh" ? " · " + (r.leftover === "excellent" ? "excellent leftovers" : "ok leftovers") : "");
    tags = (r.tags || []).slice(0, 3).map((t) => `<span class="tag">${t}</span>`).join(""); }
  else { title = "— empty —"; meta = "Regenerate or drag a meal here"; }
  const titleHtml = viewId != null
    ? `<div class="title tappable" data-view="${viewId}" data-serves="${m.servings}" role="button" tabindex="0">${title}<span class="view-hint"> ›</span></div>`
    : `<div class="title">${title}</div>`;

  let a = `<div class="actions">`;
  if (m.recipe && m.status === "planned") {
    a += `<button class="btn small" data-cook="${m.recipe.id}" data-serves="${m.servings}">👨‍🍳 Cook</button>`;
    a += `<button class="btn small" data-swap="${m.id}">Swap</button>`;
    if (m.recipe.leftover !== "fresh") a += `<button class="btn small" data-leftover="${m.id}" title="Use leftovers on another night">♻</button>`;
  }
  a += `<button class="btn small icon ${m.locked ? "on" : ""}" data-lock="${m.id}" data-locked="${m.locked}">${m.locked ? "🔒" : "🔓"}</button>`;
  a += `<button class="btn small ${m.status === "away" ? "on" : ""}" data-away="${m.date}" data-isaway="${m.status === "away"}">✈</button>`;
  a += `<button class="btn small" data-regenday="${m.date}">↻</button></div>`;

  const grip = draggable ? `<div class="grip" title="Drag to reorder">⠿</div>` : `<div class="grip placeholder"></div>`;
  return `<div class="${cls.join(" ")}" ${draggable ? 'data-drag="1"' : ""} data-recipeid="${m.recipe ? m.recipe.id : ""}" data-date="${m.date}">
    ${grip}<div class="dow"><div class="d">${f.d}</div><div class="m">${f.dow}</div></div>
    <div class="body">${titleHtml}<div class="meta">${meta}</div><div class="tags">${tags}</div>${a}</div></div>`;
}

function wireDayActions() {
  document.querySelectorAll("[data-cook]").forEach((b) => b.onclick = () => openCook(Number(b.dataset.cook), Number(b.dataset.serves)));
  document.querySelectorAll("#tab-plan [data-view]").forEach((b) => {
    const open = () => openRecipeView(Number(b.dataset.view), Number(b.dataset.serves) || undefined);
    b.onclick = open;
    b.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } };
  });
  document.querySelectorAll("[data-lock]").forEach((b) => b.onclick = async () => { await Store.setLock(Number(b.dataset.lock), b.dataset.locked !== "true"); toast(b.dataset.locked !== "true" ? "Locked" : "Unlocked"); renderPlan(); });
  document.querySelectorAll("[data-away]").forEach((b) => b.onclick = async () => { const away = b.dataset.isaway === "true"; await Store.setDayStatus(b.dataset.away, away ? "open" : "away"); toast(away ? "Marked as cooking" : "Marked away"); renderPlan(); });
  document.querySelectorAll("[data-regenday]").forEach((b) => b.onclick = () => regenerate({ scope: "day", start: b.dataset.regenday }));
  document.querySelectorAll("[data-swap]").forEach((b) => b.onclick = () => openSwap(Number(b.dataset.swap)));
  document.querySelectorAll("[data-leftover]").forEach((b) => b.onclick = () => placeLeftover(Number(b.dataset.leftover)));
}

async function regenerate(opts) { await Store.regenerate({ ...opts, filter: state.filter }); toast("Plan updated"); renderPlan(); }

async function openSwap(mealId) {
  const recipes = Store.listRecipes();
  const names = recipes.map((r, i) => `${i + 1}. ${r.title}`).join("\n");
  const pick = prompt("Swap to which recipe? Enter the number:\n\n" + names);
  const idx = Number(pick) - 1;
  if (recipes[idx]) { await Store.swap(mealId, recipes[idx].id); toast("Swapped — lists updated"); renderPlan(); }
}
async function placeLeftover(mealId) {
  const days = Store.eligibleLeftoverDays(mealId);
  if (!days.length) { toast("No free day within 3 days"); return; }
  const list = days.map((d, i) => `${i + 1}. ${DOW_FULL[d.weekday]} ${fmtLong(d.date)}`).join("\n");
  const pick = prompt("Use these leftovers on which night? (within 3 days)\n\n" + list);
  const idx = Number(pick) - 1;
  if (days[idx]) { await Store.setLeftoverPlacement(mealId, days[idx].date); toast("Leftover night set"); renderPlan(); }
}

// ---- drag reorder (pointer-based; works for touch + mouse) ----
function makeSortable(container, onEnd) {
  container.querySelectorAll('[data-drag="1"] .grip').forEach((grip) => {
    grip.style.touchAction = "none";
    grip.addEventListener("pointerdown", (e) => startDrag(e, grip.closest('[data-drag="1"]'), container, onEnd));
  });
}
function startDrag(e, el, container, onEnd) {
  e.preventDefault();
  let lastY = e.clientY;
  el.classList.add("dragging");
  const move = (ev) => {
    ev.preventDefault();
    el.style.transform = `translateY(${ev.clientY - lastY}px)`;
    const sibs = [...container.querySelectorAll('[data-drag="1"]')].filter((s) => s !== el);
    for (const s of sibs) {
      const r = s.getBoundingClientRect();
      if (ev.clientY > r.top && ev.clientY < r.bottom) {
        const mid = r.top + r.height / 2;
        if (ev.clientY < mid) container.insertBefore(el, s); else container.insertBefore(el, s.nextSibling);
        lastY = ev.clientY; el.style.transform = "translateY(0px)"; break;
      }
    }
  };
  const up = () => {
    document.removeEventListener("pointermove", move); document.removeEventListener("pointerup", up);
    el.classList.remove("dragging"); el.style.transform = "";
    onEnd();
  };
  document.addEventListener("pointermove", move); document.addEventListener("pointerup", up);
}
async function commitReorder(card) {
  const ids = [...card.querySelectorAll('[data-drag="1"]')].map((t) => Number(t.dataset.recipeid) || null);
  await Store.reorderPlanned(card.dataset.weekstart, ids);
  toast("Reordered — lists updated"); renderPlan();
}

// ---------------------------------------------------------------- SHOPPING
function renderShopping() {
  const g = Store.groceries(), meat = Store.meat("plan"), nut = Store.nutrition();
  let html = `<div class="card"><h2>Groceries — this week</h2>
    <div class="small muted" style="margin-bottom:8px">🛒 ${g.store} · ${fmtLong(g.week_start)} to ${fmtLong(g.week_end)} · AUD</div>`;
  const cats = Object.keys(g.by_category).sort();
  if (!cats.length) html += `<div class="empty-note">Nothing to buy — pantry covers this week, or no meals planned.</div>`;
  cats.forEach((c) => { html += `<div class="cat-head">${c}</div>`;
    g.by_category[c].forEach((it) => { html += `<label class="list-item"><input type="checkbox" class="tick">
      <span class="name">${it.name}</span><span class="qty">${qtyLabel(it.buy_qty, it.unit)}${it.est_cost ? " · $" + it.est_cost.toFixed(2) : ""}</span></label>`; });
  });
  html += `<div class="total-bar"><span>Estimated spend</span><span class="amt">$${g.estimated_cost.toFixed(2)}</span></div>`;
  if (g.weekly_budget > 0) html += `<div class="row"><span class="pill ${g.over_budget ? "bad" : "good"}">Budget $${g.weekly_budget.toFixed(2)} — ${g.over_budget ? "over" : "within"}</span></div>`;
  html += `</div>`;

  html += `<div class="card"><h2>Meat to buy</h2>
    <div class="small muted" style="margin-bottom:8px">🥩 ${meat.store} · whole plan vs your stock · AUD</div>`;
  if (!meat.to_buy.length) html += `<div class="empty-note">You have all the meat the plan needs. 🎉</div>`;
  meat.to_buy.forEach((it) => { html += `<div class="list-item"><span class="name">${it.name}</span>
    <span class="qty">buy ${qtyLabelSmart(it.buy_qty, it.unit)} (have ${qtyLabelSmart(it.have_qty, it.unit)})</span></div>`; });
  if (meat.items.length) { html += `<details style="margin-top:8px"><summary>Full meat requirement</summary>`;
    meat.items.forEach((it) => { html += `<div class="list-item small"><span class="name">${it.name}</span>
      <span class="qty">need ${qtyLabelSmart(it.needed_qty, it.unit)} · have ${qtyLabelSmart(it.have_qty, it.unit)}</span></div>`; });
    html += `</details>`; }
  html += `<div class="total-bar small"><span class="muted">Estimated meat spend</span><span>$${meat.estimated_cost.toFixed(2)}</span></div></div>`;

  html += `<div class="card"><h2>Nutrition this week (per serve)</h2><div class="macro-grid">
    <div class="macro"><div class="v">${nut.daily_average.kj}</div><div class="k">kJ/day</div></div>
    <div class="macro"><div class="v">${nut.daily_average.protein_g}g</div><div class="k">protein</div></div>
    <div class="macro"><div class="v">${nut.daily_average.carbs_g}g</div><div class="k">carbs</div></div>
    <div class="macro"><div class="v">${nut.daily_average.fat_g}g</div><div class="k">fat</div></div></div>
    <div class="small muted" style="margin-top:8px">Daily averages across cooking nights. Estimates only.</div></div>`;
  $("tab-shopping").innerHTML = html;
  document.querySelectorAll(".tick").forEach((c) => c.onchange = () => c.closest(".list-item").classList.toggle("checked", c.checked));
}

// ---------------------------------------------------------------- PANTRY / STOCK
function renderPantry() {
  const items = Store.getPantry();
  let html = `<div class="card"><h2>What's at home</h2>
    <div class="small muted" style="margin-bottom:8px">Meat here is checked against the plan to build the meat-to-buy list. The planner also leans toward using what's in your freezer.</div>`;
  if (!items.length) html += `<div class="empty-note">Nothing recorded yet. Add stock below.</div>`;
  items.forEach((p) => { html += `<div class="list-item"><span class="name">${p.display}
    <div class="small muted">${p.location}${p.special_occasion ? " · ⭐ special occasion" : ""}${p.best_before ? " · best before " + fmtLong(p.best_before) : ""}</div></span>
    <span class="qty">${qtyLabelSmart(p.quantity, p.unit)}</span>
    <button class="btn small" data-delpantry="${p.id}">✕</button></div>`; });
  html += `</div>`;

  const typeOpts = Store.MEAT_TYPES.map((t) => `<option value="${t}">${t}</option>`).join("");
  html += `<div class="card"><h2>Add / update stock</h2>
    <div class="row"><label class="f">Category<select id="p_cat">
      <option value="meat">meat</option><option value="veg">veg</option><option value="dairy">dairy</option>
      <option value="pantry">pantry</option><option value="spice">spice</option><option value="sauce">sauce</option></select></label>
      <label class="f grow" id="nameField" style="display:none">Name<input id="p_name" placeholder="e.g. Passata"></label></div>
    <div class="row" id="meatFields">
      <label class="f">Meat type<select id="p_mtype">${typeOpts}</select></label>
      <label class="f grow" id="cutLabel">Cut
        <div class="combo"><input id="p_mcut" autocomplete="off" placeholder="Tap to choose or search…">
        <div id="cutMenu" class="combo-menu hidden"></div></div></label></div>
    <div class="row">
      <label class="f">Quantity<input id="p_qty" type="number" step="any" inputmode="decimal" placeholder="0" style="width:100px"></label>
      <label class="f">Unit<select id="p_unit"><option>g</option><option>kg</option><option>ml</option><option>l</option>
        <option>whole</option><option>can</option><option>tbsp</option><option>tsp</option><option>cup</option></select></label>
      <label class="f">Location<select id="p_loc"><option value="freezer">Freezer</option><option value="fridge">Fridge</option><option value="pantry">Pantry</option></select></label></div>
    <div class="row">
      <label class="f">Purchase date (optional)<input id="p_pdate" type="date"></label>
      <label class="f">Best before (optional)<input id="p_bbdate" type="date"></label></div>
    <div class="small muted" id="bbHint" style="margin:2px 0 6px"></div>
    <label class="f" style="flex-direction:row;align-items:center;gap:8px;margin:6px 0">
      <input id="p_special" type="checkbox"> ⭐ Special occasion (kept aside — the auto-planner won't use this stock)</label>
    <button class="btn primary" id="addPantry">Add to stock</button></div>`;
  $("tab-pantry").innerHTML = html;

  const catSel = $("p_cat"), cutInput = $("p_mcut"), cutMenu = $("cutMenu");
  const updateBB = () => {
    const auto = Store.autoBestBefore($("p_mtype").value, cutInput.value, $("p_pdate").value, $("p_loc").value);
    if (auto && !$("p_bbdate").value) { $("p_bbdate").value = auto;
      $("bbHint").innerHTML = `Auto best-before <b>${fmtLong(auto)}</b> (max recommended freezer time). Edit above to override.`; }
    else if (!auto) $("bbHint").textContent = "";
  };
  // searchable cut dropdown, filtered by the selected meat type
  const renderCutMenu = (filter) => {
    const opts = Store.cutsForType($("p_mtype").value).filter((c) => c.toLowerCase().includes((filter || "").toLowerCase()));
    cutMenu.innerHTML = opts.length
      ? opts.map((c) => `<div data-cut="${c.replace(/"/g, "&quot;")}">${c}</div>`).join("")
      : `<div class="none">No match — type your own</div>`;
    cutMenu.querySelectorAll("[data-cut]").forEach((d) => d.onmousedown = (e) => { e.preventDefault(); cutInput.value = d.dataset.cut; cutMenu.classList.add("hidden"); updateBB(); });
  };
  cutInput.onfocus = () => { cutMenu.classList.remove("hidden"); renderCutMenu(""); };
  cutInput.oninput = () => { cutMenu.classList.remove("hidden"); renderCutMenu(cutInput.value); };
  cutInput.onblur = () => setTimeout(() => cutMenu.classList.add("hidden"), 150);
  const updateCutLabel = () => { const sausage = $("p_mtype").value === "Sausage";
    $("cutLabel").firstChild.textContent = sausage ? "Flavour" : "Cut";
    cutInput.placeholder = sausage ? "Tap to choose or type a flavour…" : "Tap to choose or search…"; };
  const toggle = () => { const meat = catSel.value === "meat"; $("meatFields").style.display = meat ? "flex" : "none"; $("nameField").style.display = meat ? "none" : "flex"; $("p_loc").value = meat ? "freezer" : "pantry"; if (meat) updateCutLabel(); };
  catSel.onchange = toggle; toggle();
  $("p_mtype").onchange = () => { cutInput.value = ""; updateCutLabel(); $("p_bbdate").value = ""; updateBB(); };
  $("p_pdate").onchange = updateBB; $("p_loc").onchange = () => { $("p_bbdate").value = ""; updateBB(); };
  $("addPantry").onclick = async () => {
    const isMeat = catSel.value === "meat";
    const base = { quantity: Number($("p_qty").value) || 0, unit: $("p_unit").value, location: $("p_loc").value,
      special_occasion: $("p_special").checked, purchase_date: $("p_pdate").value, best_before: $("p_bbdate").value };
    const body = isMeat
      ? { ...base, category: "meat", is_meat: true, meat_type: $("p_mtype").value, meat_cut: $("p_mcut").value.trim() }
      : { ...base, category: catSel.value, is_meat: false, name: $("p_name").value.trim() };
    if (!isMeat && !body.name) { toast("Enter a name"); return; }
    if (isMeat && !body.meat_cut) { toast("Enter a cut/flavour"); return; }
    await Store.addPantry(body); toast("Added to stock"); renderPantry();
  };
  document.querySelectorAll("[data-delpantry]").forEach((b) => b.onclick = async () => { await Store.deletePantry(Number(b.dataset.delpantry)); renderPantry(); });
}

// ---------------------------------------------------------------- RECIPES
const KNOWN_UNITS = ["g","kg","ml","l","tsp","tbsp","cup","cups","can","tin","whole","clove","cloves","pinch","handful","bunch","sprig","slice","slices","rasher","rashers"];
const MEAT_MAP = { beef:"beef", steak:"beef", mince:"beef", chuck:"beef", chicken:"chicken", drumstick:"chicken", thigh:"chicken", pork:"pork", bacon:"smallgoods", ham:"smallgoods", chorizo:"smallgoods", sausage:"sausage", lamb:"lamb", salmon:"salmon", fish:"fish", barramundi:"fish", prawn:"fish", duck:"duck", veal:"veal", kangaroo:"kangaroo" };
const VEG = ["onion","garlic","carrot","potato","capsicum","broccoli","spinach","tomato","zucchini","mushroom","pea","corn","lettuce","cucumber","pumpkin","bean","celery","cabbage","asparagus","sweet potato"];
const DAIRY = ["milk","cheese","butter","cream","yoghurt","egg"];
function parseIngredientLine(line) {
  line = line.trim(); if (!line) return null;
  let qty = 0, unit = "", name = line;
  const m = line.match(/^([\d.\/]+)\s*(\S+)?\s+(.*)$/);
  if (m) {
    const q = m[1];
    if (q.includes("/")) { const [a, b] = q.split("/"); qty = Number(a) / Number(b); } else qty = Number(q);
    if (!isFinite(qty)) qty = 0;
    const tok = (m[2] || "").toLowerCase();
    if (KNOWN_UNITS.includes(tok)) { unit = tok === "cups" ? "cup" : tok; name = m[3]; }
    else name = ((m[2] || "") + " " + m[3]).trim();
  }
  const low = name.toLowerCase();
  let category = "pantry", is_meat = false, meat_type = "";
  for (const [w, t] of Object.entries(MEAT_MAP)) { if (low.includes(w)) { category = "meat"; is_meat = true; meat_type = t; break; } }
  if (!is_meat) { if (VEG.some((w) => low.includes(w))) category = "veg"; else if (DAIRY.some((w) => low.includes(w))) category = "dairy"; }
  return { name: name.charAt(0).toUpperCase() + name.slice(1), quantity: Math.round(qty * 10) / 10, unit, category, is_meat, meat_type, meat_cut: "", optional: false, price_per_unit: 0, step_index: 0 };
}
function renderRecipes() {
  const s = state.search;
  const chip = (key, label, extra = "") => `<button type="button" class="chip ${s[key] ? "on" : ""}" data-sf="${key}">${extra}${label}</button>`;
  const lv = (key, label) => `<button type="button" class="chip ${s.leftover_levels.includes(key) ? "on" : ""}" data-slv="${key}">${label}</button>`;
  const total = Store.state.recipes.length;
  let html = `<div class="card"><h2>Find a recipe</h2>
    <input id="q_text" type="text" placeholder="Search by name or ingredient (e.g. mince, prawn)…" value="${s.text.replace(/"/g,"&quot;")}" style="width:100%">
    <div class="chips" style="margin-top:10px">
      ${chip("favourited","Favourites","⭐ ")}${chip("uses_fridge","Uses fridge meat","🧊 ")}${chip("uses_freezer","Uses freezer meat","❄️ ")}
      ${chip("high_protein","High protein")}${chip("low_carb","Low carb")}</div>
    <div class="fl" style="margin-top:8px"><span class="fl-label">Leftovers</span><div class="chips">${lv("fresh","Best fresh")}${lv("ok","OK")}${lv("excellent","Excellent")}</div></div>
    <div class="fl"><span class="fl-label">Dairy (pick any)</span><div class="chips">
      ${DAIRY_LEVELS.map(([k,l]) => `<button type="button" class="chip ${s.dairy_levels.includes(k)?"on":""}" data-sdl="${k}">${l}</button>`).join("")}</div></div>
  </div>
  <div id="searchResults"></div>
  <details class="card"><summary style="font-weight:600;font-size:15px;color:var(--text)">➕ Add your own recipe</summary>
    <div class="small muted" style="margin:8px 0">On-device, recipes are added here (automatic import from a web link needs the hosted version).</div>
    <div class="row"><label class="f grow">Title<input id="r_title" placeholder="Mum's fried rice"></label></div>
    <div class="row"><label class="f">Prep min<input id="r_prep" type="number" value="10" style="width:80px"></label>
      <label class="f">Cook min<input id="r_cook" type="number" value="20" style="width:80px"></label>
      <label class="f">Serves<input id="r_serves" type="number" value="4" style="width:70px"></label></div>
    <div class="row"><label class="f">kJ/serve<input id="r_kj" type="number" placeholder="0" style="width:90px"></label>
      <label class="f">Protein g<input id="r_prot" type="number" placeholder="0" style="width:80px"></label>
      <label class="f">Carbs g<input id="r_carb" type="number" placeholder="0" style="width:80px"></label>
      <label class="f">Fat g<input id="r_fat" type="number" placeholder="0" style="width:80px"></label></div>
    <div class="row"><label class="f">Leftovers<select id="r_left">
        <option value="fresh">Best fresh</option><option value="ok">OK</option><option value="excellent">Excellent</option></select></label>
      <label class="f">Weight-loss 1–5<input id="r_wl" type="number" min="1" max="5" value="3" style="width:90px"></label>
      <label class="f">Dairy<select id="r_dairy"><option value="free">Dairy-free</option><option value="replaceable">Replaceable</option><option value="required" selected>Contains dairy</option></select></label></div>
    <div class="row"><label class="f grow">Tags (comma)<input id="r_tags" placeholder="chicken, quick"></label></div>
    <div class="row"><label class="f grow">Ingredients (one per line, e.g. "500 g beef mince")<textarea id="r_ings" rows="5" class="ta"></textarea></label></div>
    <div class="row"><label class="f grow">Method (one step per line)<textarea id="r_steps" rows="5" class="ta"></textarea></label></div>
    <button class="btn primary" id="addRecipe">Save recipe</button></details>`;
  $("tab-recipes").innerHTML = html;

  const results = () => renderSearchResults(total);
  $("q_text").oninput = (e) => { s.text = e.target.value; results(); };
  document.querySelectorAll("[data-sf]").forEach((b) => b.onclick = () => { s[b.dataset.sf] = !s[b.dataset.sf]; b.classList.toggle("on"); results(); });
  document.querySelectorAll("[data-slv]").forEach((b) => b.onclick = () => { const k = b.dataset.slv, i = s.leftover_levels.indexOf(k); if (i>=0) s.leftover_levels.splice(i,1); else s.leftover_levels.push(k); b.classList.toggle("on"); results(); });
  document.querySelectorAll("[data-sdl]").forEach((b) => b.onclick = () => { const k = b.dataset.sdl, i = s.dairy_levels.indexOf(k); if (i>=0) s.dairy_levels.splice(i,1); else s.dairy_levels.push(k); b.classList.toggle("on"); results(); });
  $("addRecipe").onclick = async () => {
    const title = $("r_title").value.trim(); if (!title) { toast("Enter a title"); return; }
    const ings = $("r_ings").value.split("\n").map(parseIngredientLine).filter(Boolean);
    const steps = $("r_steps").value.split("\n").map((x) => x.trim()).filter(Boolean);
    const tags = $("r_tags").value.split(",").map((x) => x.trim()).filter(Boolean);
    await Store.addRecipe({ title, prep_min: +$("r_prep").value || 0, cook_min: +$("r_cook").value || 0, servings: +$("r_serves").value || 4,
      kj: +$("r_kj").value || 0, protein_g: +$("r_prot").value || 0, carbs_g: +$("r_carb").value || 0, fat_g: +$("r_fat").value || 0,
      leftover: $("r_left").value, weight_loss_rating: +$("r_wl").value || 3, dairy: $("r_dairy").value, tags, method_steps: steps, ingredients: ings });
    toast("Recipe saved"); renderRecipes();
  };
  results();
}
function renderSearchResults(total) {
  const list = Store.searchRecipes(state.search);
  let html = `<div class="card"><h2>Matches (${list.length} of ${total})</h2>`;
  if (!list.length) html += `<div class="empty-note">No recipes match. Try fewer filters.</div>`;
  list.slice(0, 200).forEach((r) => { html += `<div class="list-item"><span class="name">${r.liked===1?"⭐ ":""}${r.uses_fridge?"🧊 ":""}${r.uses_freezer?"❄️ ":""}${r.title}
    <div class="small muted">${r.total_min} min · ${r.kj} kJ · ${r.leftover_label}</div></span>
    <button class="btn small" data-view="${r.id}">View</button>
    <button class="btn small" data-add="${r.id}">＋ Plan</button>
    <button class="btn small ${r.liked === 1 ? "on" : ""}" data-like="${r.id}" data-val="${r.liked === 1 ? 0 : 1}">👍</button></div>`; });
  html += `</div>`;
  $("searchResults").innerHTML = html;
  document.querySelectorAll("#searchResults [data-view]").forEach((b) => b.onclick = () => openCook(Number(b.dataset.view), Store.getSettings().servings_per_meal));
  document.querySelectorAll("#searchResults [data-add]").forEach((b) => b.onclick = async () => { const d = await Store.addToPlan(Number(b.dataset.add)); toast(d ? "Added to " + fmtLong(d) : "No empty day — free one or regenerate"); });
  document.querySelectorAll("#searchResults [data-like]").forEach((b) => b.onclick = async () => { await Store.likeRecipe(Number(b.dataset.like), Number(b.dataset.val)); renderSearchResults(total); });
}

// ---------------------------------------------------------------- SETTINGS + BACKUP
function renderSettings() {
  const s = Store.getSettings();
  // weekdays listed in the household's week order, each a multi-select of preferences
  let dayRows = "";
  for (let i = 0; i < 7; i++) { const wd = (s.week_start_day + i) % 7; const cur = s.day_prefs[wd] || [];
    const chips = Store.DAY_PREF_OPTIONS.map(([v, l]) => `<button type="button" class="chip ${cur.includes(v) ? "on" : ""}" data-dpref="${wd}" data-dval="${v}">${l}</button>`).join("");
    dayRows += `<div class="fl"><span class="fl-label">${DOW_FULL[wd]}</span><div class="chips">${chips}</div></div>`; }
  const weekOpts = [0,1,2,3,4,5,6].map((d) => `<option value="${d}" ${s.week_start_day === d ? "selected" : ""}>${DOW_FULL[d]}</option>`).join("");
  const cap = (x) => x.charAt(0).toUpperCase() + x.slice(1);
  const priceRows = Store.getMeatCuts().map((c) => {
    const isSausage = c.type.toLowerCase() === "sausage";
    const pieceW = Store.pieceKg(c.type, c.cut);
    let mode, factor;   // convert stored $/unit <-> displayed value
    if (c.unit === "g") { mode = "gkg"; factor = 1000; }                 // g  -> $/kg
    else if (isSausage) { mode = "sausage"; factor = 1 / SAUSAGE_KG; }   // sausage -> $/kg
    else if (pieceW > 0) { mode = "piece"; factor = 1 / pieceW; }        // per-piece cut priced $/kg
    else { mode = "each"; factor = 1; }                                  // else $/each
    const unitLabel = mode === "each" ? "$/each" : "$/kg";
    const shown = c.price != null ? Math.round(c.price * factor * 100) / 100 : "";
    const ph = Math.round(c.default_ppu * factor * 100) / 100;
    return `<div class="row" style="align-items:center;margin-bottom:6px"><span class="grow small">${cap(c.type)} · ${c.cut} <span class="muted">(${unitLabel})</span>${c.ame ? ' <span class="pill good" style="padding:1px 6px">AME</span>' : ''}</span>
      <input type="number" step="any" data-mp="${c.key}" data-mode="${mode}" data-weight="${pieceW}" value="${shown}" placeholder="~${ph}" style="width:110px"></div>`;
  }).join("");
  const ameNote = Store.amePrices && Store.amePrices.updated
    ? `AME prices auto-updated ${fmtLong(Store.amePrices.updated)} (Mon/Wed/Fri). The <span class="pill good" style="padding:1px 6px">AME</span> tag = live-scraped default; your own entry always overrides.`
    : `Live AME auto-pricing runs Mon/Wed/Fri once the schedule is active.`;

  $("tab-settings").innerHTML = `<div class="card"><h2>Household</h2>
    <div class="row"><label class="f">Adults<input id="s_adults" type="number" min="0" value="${s.household_adults}" style="width:80px"></label>
      <label class="f">Children<input id="s_children" type="number" min="0" value="${s.household_children}" style="width:80px"></label>
      <label class="f">Servings/meal<input id="s_serves" type="number" min="1" value="${s.servings_per_meal}" style="width:90px"></label></div>
    <div class="row"><label class="f">Week starts on<select id="s_weekstart" style="width:150px">${weekOpts}</select></label>
      <label class="f">Weekly budget $ AUD<input id="s_budget" type="number" min="0" value="${s.weekly_budget}" style="width:120px"></label></div>
    <div class="small muted" style="margin-top:8px">Changes save automatically.</div></div>

    <div class="card"><h2>Leftovers</h2>
    <label class="f">How auto-leftovers work<select id="s_leftover">
      <option value="off" ${s.leftover_mode==="off"?"selected":""}>Off — no auto leftovers</option>
      <option value="auto" ${s.leftover_mode==="auto"?"selected":""}>Auto — place excellent leftovers within 3 days</option>
      <option value="manual" ${s.leftover_mode==="manual"?"selected":""}>Manual — I place them with the ♻ button</option></select></label>
    <div class="small muted" style="margin-top:8px">Recipes are rated Best fresh / OK / Excellent. Auto mode carries an “excellent” cook into a free night within 3 days; the ♻ button on any OK/Excellent meal lets you choose the night yourself.</div></div>

    <div class="card"><h2>Diet thresholds</h2>
    <div class="row"><label class="f">“High protein” means ≥ (g/serve)<input id="s_hp" type="number" min="0" value="${s.high_protein_g}" style="width:110px"></label>
      <label class="f">“Low carb” means ≤ (g/serve)<input id="s_lc" type="number" min="0" value="${s.low_carb_g}" style="width:110px"></label></div>
    <div class="small muted" style="margin-top:8px">These set what the High-protein and Low-carb filters mean.</div></div>

    <div class="card"><h2>Day preferences</h2>
    <div class="small muted" style="margin-bottom:8px">Tick any that apply to each night (you can pick more than one). “Light” = lower-kilojoule meals. “Early prep / slow cook” = set-and-forget or a 10–15 min finish when you get home. “No cook” leaves that night free.</div>
    ${dayRows}</div>

    <details class="card"><summary style="font-weight:600;font-size:15px;color:var(--text)">🥩 Meat pricing (optional)</summary>
    <div class="small muted" style="margin:8px 0">Australian Meat Emporium prices per cut. Sausages priced $/kg. Blank = estimate. Prices in AUD. ${ameNote}</div>
    ${priceRows || '<div class="small muted">No meat cuts in the library yet.</div>'}</details>

    <div class="card"><h2>Backup & restore</h2>
    <div class="small muted" style="margin-bottom:10px">Your data lives on this phone. Export a backup to iCloud/Files so it's safe, and restore it on a new phone.</div>
    <div class="row"><button class="btn primary" id="exportBtn">⬇ Export backup</button>
      <button class="btn" id="restoreBtn">⬆ Restore from file</button>
      <input type="file" id="restoreFile" accept="application/json,.json" style="display:none"></div>
    <div class="row" style="margin-top:14px"><button class="btn" id="resetBtn" style="border-color:var(--danger);color:var(--danger)">Reset to starter recipes</button></div></div>

    <div class="card"><h2>About</h2><div class="small muted"><b>Version 1.0</b> · On-device family meal planner. Metric, energy in kJ, prices in AUD. Auto-updates from Netlify. Cost and nutrition figures are estimates.</div></div>`;

  const saveHousehold = async () => { await Store.saveSettings({ household_adults: +$("s_adults").value || 0, household_children: +$("s_children").value || 0,
    servings_per_meal: +$("s_serves").value || 4, weekly_budget: +$("s_budget").value || 0 }); toast("Saved"); };
  ["s_adults","s_children","s_serves","s_budget"].forEach((id) => $(id).onchange = saveHousehold);
  $("s_weekstart").onchange = async () => { await Store.saveSettings({ week_start_day: +$("s_weekstart").value || 0 }); toast("Saved"); renderSettings(); };
  $("s_leftover").onchange = async () => { await Store.saveSettings({ leftover_mode: $("s_leftover").value }); toast("Saved"); };
  $("s_hp").onchange = async () => { await Store.saveSettings({ high_protein_g: +$("s_hp").value || 0 }); toast("Saved"); };
  $("s_lc").onchange = async () => { await Store.saveSettings({ low_carb_g: +$("s_lc").value || 0 }); toast("Saved"); };
  document.querySelectorAll("[data-dpref]").forEach((b) => b.onclick = async () => {
    const wd = b.dataset.dpref, v = b.dataset.dval; const dp = Store.getSettings().day_prefs; const arr = dp[wd] || [];
    const i = arr.indexOf(v); if (i >= 0) arr.splice(i, 1); else arr.push(v); dp[wd] = arr;
    b.classList.toggle("on"); await Store.saveSettings({ day_prefs: dp });
  });
  $("exportBtn").onclick = () => {
    const data = JSON.stringify(Store.exportData(), null, 2);
    const blob = new Blob([data], { type: "application/json" }); const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = `meal-planner-backup-${Store.getPlan().today}.json`;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000); toast("Backup exported");
  };
  $("restoreBtn").onclick = () => $("restoreFile").click();
  $("restoreFile").onchange = (e) => { const file = e.target.files[0]; if (!file) return; const reader = new FileReader();
    reader.onload = async () => { try { await Store.importData(JSON.parse(reader.result)); toast("Backup restored"); goTab("plan"); } catch (err) { toast(err.message || "Could not restore"); } };
    reader.readAsText(file); };
  $("resetBtn").onclick = async () => { if (confirm("Reset everything to the starter recipes and a fresh plan? Your changes will be lost.")) { await Store.resetAll(); toast("Reset done"); goTab("plan"); } };
  document.querySelectorAll("[data-mp]").forEach((inp) => inp.onchange = async () => {
    const mode = inp.dataset.mode; const v = inp.value.trim();
    if (v === "") { await Store.setMeatPrice(inp.dataset.mp, ""); toast("Price cleared"); return; }
    let ppu = Number(v);
    if (mode === "gkg") ppu = ppu / 1000;                                   // $/kg -> $/g
    else if (mode === "sausage") ppu = ppu * SAUSAGE_KG;                    // $/kg -> $/sausage
    else if (mode === "piece") ppu = ppu * (Number(inp.dataset.weight) || 0.15); // $/kg -> $/piece
    await Store.setMeatPrice(inp.dataset.mp, ppu);
    toast("Price saved");
  });
}

// ------------------------------------------------------------- RECIPE VIEW
// Read-only full recipe: ingredients (scaled to servings) + numbered method.
function openRecipeView(recipeId, servings) {
  const r = Store.getRecipe(recipeId); if (!r) return;
  const serves = servings || r.servings;
  state.viewing = { id: recipeId, servings: serves };
  const scale = serves / Math.max(r.servings, 1);
  $("rvTitle").textContent = r.title;
  const macros = `${r.kj} kJ · ${r.protein_g} g protein · ${r.carbs_g} g carbs · ${r.fat_g} g fat`;
  const ings = (r.ingredients || []).slice().sort((a, b) => (a.step_index || 0) - (b.step_index || 0));
  const ingHtml = ings.length
    ? ings.map((x) => `<li>${qtyLabel(x.quantity * scale, x.unit)} ${x.name}${x.optional ? " (optional)" : ""}</li>`).join("")
    : `<li class="muted">No ingredients recorded.</li>`;
  const steps = r.method_steps && r.method_steps.length ? r.method_steps : ["No method steps recorded."];
  const stepHtml = steps.map((s, i) => `<li><span class="rv-stepn">${i + 1}</span><span>${s}</span></li>`).join("");
  $("rvBody").innerHTML =
    `<div class="rv-photo" id="rvPhoto"></div>
     <div class="rv-summary">${r.total_min} min (prep ${r.prep_min} + cook ${r.cook_min}) · serves ${serves}</div>
     <div class="rv-summary">${macros} · per serve</div>
     ${r.leftover_label ? `<div class="rv-summary">Leftovers: ${r.leftover_label}</div>` : ""}
     <h4 class="rv-h">Ingredients</h4><ul class="rv-ings">${ingHtml}</ul>
     <h4 class="rv-h">Method</h4><ol class="rv-steps">${stepHtml}</ol>`;
  $("recipeView").classList.add("open");
  $("rvBody").scrollTop = 0;
  loadRecipePhoto(recipeId);
}
function closeRecipeView() { $("recipeView").classList.remove("open"); }
$("rvClose").onclick = closeRecipeView;
$("rvCook").onclick = () => { const v = state.viewing; closeRecipeView(); if (v) openCook(v.id, v.servings); };

// Auto-fetched dish photo (TheMealDB). Best-effort: shows a spinner while it looks,
// then the picture, a small "try another", and a "hide" control — or a quiet note
// if nothing matched or we're offline.
async function loadRecipePhoto(id) {
  const box = $("rvPhoto"); if (!box) return;
  box.className = "rv-photo loading";
  box.innerHTML = `<div class="rv-photo-msg">Finding a photo…</div>`;
  let r;
  try { r = await Store.resolveRecipeImage(id); }
  catch (e) { r = { status: "offline", url: "", count: 0 }; }
  if (!state.viewing || state.viewing.id !== id) return;   // view moved on
  paintRecipePhoto(id, r);
}
function paintRecipePhoto(id, r) {
  const box = $("rvPhoto"); if (!box) return;
  if (r.status === "ready" && r.url) {
    const more = r.count > 1 ? `<button class="btn small" id="rvImgAnother">↻ Another</button>` : "";
    box.className = "rv-photo";
    box.innerHTML = `<img src="${r.url}" alt="" loading="lazy" onerror="this.parentNode.classList.add('broken')">
      <div class="rv-photo-tools">${more}<button class="btn small" id="rvImgHide">✕ Hide</button></div>
      <div class="rv-photo-credit">Photo: TheMealDB · may not match exactly</div>`;
    const another = $("rvImgAnother");
    if (another) another.onclick = async () => { const nx = await Store.cycleRecipeImage(id); paintRecipePhoto(id, nx); };
    $("rvImgHide").onclick = async () => { await Store.clearRecipeImage(id); paintRecipePhoto(id, { status: "none", url: "", count: 0 }); };
  } else {
    const label = r.status === "offline" ? "Photo will load when you're online" : "No matching photo found";
    box.className = "rv-photo empty";
    box.innerHTML = `<div class="rv-photo-msg">${label} · <a href="#" id="rvImgRetry">search again</a></div>`;
    $("rvImgRetry").onclick = async (e) => { e.preventDefault(); box.className = "rv-photo loading"; box.innerHTML = `<div class="rv-photo-msg">Searching…</div>`;
      const nx = await Store.retryRecipeImage(id); if (state.viewing && state.viewing.id === id) paintRecipePhoto(id, nx); };
  }
}

// ---------------------------------------------------------------- COOK MODE
let wakeLock = null;
function openCook(recipeId, servings) {
  const r = Store.getRecipe(recipeId); if (!r) return;
  state.cook = { recipe: r, step: 0, servings: servings || r.servings };
  $("cook").classList.add("open");
  if ("wakeLock" in navigator) navigator.wakeLock.request("screen").then((w) => (wakeLock = w)).catch(() => {});
  drawCook();
}
function closeCook() { $("cook").classList.remove("open"); if (wakeLock) { wakeLock.release(); wakeLock = null; } }
function drawCook() {
  const { recipe, step, servings } = state.cook;
  const scale = servings / Math.max(recipe.servings, 1);
  $("cookTitle").textContent = recipe.title; $("servesVal").textContent = servings;
  const steps = recipe.method_steps.length ? recipe.method_steps : ["No method steps recorded."];
  const i = Math.max(0, Math.min(step, steps.length - 1));
  $("stepNum").textContent = `Step ${i + 1} of ${steps.length}`; $("stepText").textContent = steps[i];
  const ings = recipe.ingredients.filter((x) => x.step_index === i);
  $("stepIngs").innerHTML = ings.length ? ings.map((x) => `<div>• ${qtyLabel(x.quantity * scale, x.unit)} ${x.name}${x.optional ? " (optional)" : ""}</div>`).join("") : `<div class="muted">— use ingredients as needed —</div>`;
  $("prevStep").disabled = i === 0; $("nextStep").textContent = i === steps.length - 1 ? "Done ✓" : "Next ▶";
}
$("nextStep").onclick = () => { const steps = state.cook.recipe.method_steps.length || 1; if (state.cook.step >= steps - 1) closeCook(); else { state.cook.step++; drawCook(); } };
$("prevStep").onclick = () => { if (state.cook.step > 0) { state.cook.step--; drawCook(); } };
$("cookClose").onclick = closeCook;
$("servesUp").onclick = () => { state.cook.servings++; drawCook(); };
$("servesDown").onclick = () => { if (state.cook.servings > 1) { state.cook.servings--; drawCook(); } };

// ---------------------------------------------------------------- boot
// Register the service worker and auto-apply updates. When a newer version is
// deployed, the SW takes over and we reload once so the change appears with no
// action from the user. Data lives in IndexedDB, so a reload never loses it.
if ("serviceWorker" in navigator) {
  let refreshing = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (refreshing) return; refreshing = true; location.reload();
  });
  navigator.serviceWorker.register("service-worker.js").then((reg) => {
    reg.update();                                  // check for a new version on launch
    setInterval(() => reg.update(), 60 * 60 * 1000); // and hourly while open
  }).catch(() => {});
}
Store.init().then(() => render("plan")).catch((e) => { console.error(e); $("tab-plan").innerHTML = "<div class='card'>Could not start: " + e.message + "</div>"; });
