# Family Meal Planner — on-device iPhone app

A private meal planner that runs **entirely on your iPhone** — no server, no
account, no monthly cost, and it works fully offline. It's a PWA you install to
your home screen; it looks and behaves like a normal app.

Features: a **rolling 4-week dinner plan**, filter-driven meal selection, a full
**recipe search** (by ingredient, favourites, uses-freezer-meat, diet),
**drag-to-reorder** nights, an **In the freezer** summary on the plan, a
pantry/freezer-aware **grocery list** (Woolworths) and **meat-to-buy list**
(Australian Meat Emporium), offline **step-by-step cook mode**, **auto-leftovers**
(three levels, placed within 3 days), **cost** and **nutrition** estimates,
add-your-own recipes, and **backup export/restore**. Everything is **metric**
(g, ml, tsp, tbsp, cup, °C), energy in **kJ**, prices in **AUD**. Comes with
**200+** family dinners across beef, chicken, lamb, pork, sausages, smallgoods,
fish/seafood and vegetarian; serves 4.

Your data lives on the phone (in the browser's on-device database). Nothing leaves
the device unless you export a backup.

---

## Put it on your iPhone

Because it's a website-based app, it needs to be served over **HTTPS** for iOS to
install it properly and enable offline mode. Two easy ways:

### Option 1 — Free static hosting (simplest, recommended)
Upload the contents of this folder to any free static host and open the link in
Safari. Good options: **Netlify Drop** (drag the folder onto
[app.netlify.com/drop](https://app.netlify.com/drop)), **Cloudflare Pages**, or
**GitHub Pages**. These are free and give you an `https://…` link. Because the app
is fully on-device, this "hosting" only serves the files once — your data still
lives on your phone, and there's no running server or cost.

Then in Safari: open the link → **Share → Add to Home Screen**. Done. Open it from
the home-screen icon and it runs full-screen and offline.

### Option 2 — From your computer (for a quick try)
```bash
cd meal-planner-iphone
python3 -m http.server 8000
```
Open `http://localhost:8000` on the computer to try it. To reach it from the
iPhone with offline support you'd still want HTTPS (e.g. a free tunnel like
`cloudflared tunnel --url http://localhost:8000`), then Add to Home Screen from
that `https://…` link.

> Once installed, you don't need the host again for day-to-day use — the app and
> your data are on the phone. You'd only revisit the link to reinstall or move to a
> new phone (restore your backup there).

---

## Using it

- **Plan** — the rolling 4-week grid. Filter by prep/cook time, max kJ, max weekly
  cost, **leftover level** (Best fresh / OK / Excellent — pick any), **dietary**
  (weight-loss, high-protein, low-carb), **dairy** (free / free-or-replaceable) and
  excluded tags, then regenerate the whole plan, a week or a day. Per day: **Cook**,
  **Swap**, **♻ use leftovers on another night**, **Lock** (survives regeneration),
  **Away**, or **drag the ⠿ grip** to reorder nights. An **In the freezer** card at
  the top shows your freezer stock and flags what the current plan uses.
- **Shopping** — the **Woolworths** grocery list for the coming week (merged,
  stock-subtracted, by aisle, with estimated AUD spend + optional budget), the
  **Australian Meat Emporium** meat-to-buy list for the whole plan, and weekly
  nutrition (kJ + macros). All update instantly when you swap or reorder.
- **Pantry / stock** — record meat by **type** (dropdown) and **cut**, its
  **location** (freezer/fridge/pantry) and quantity. The planner leans toward using
  what's in your freezer. Tick **⭐ Special occasion** to reserve stock — the
  auto-planner won't touch it.
- **Recipes** — **search** the 200+ library by name or ingredient (e.g. "mince",
  "prawn"), or filter by ⭐ favourites, ❄️ uses-freezer-meat, high-protein,
  low-carb, dairy and leftover level. Each result has **View**, **＋ Plan** (drops
  it on the next free night), and 👍/👎. **Add your own** recipes at the bottom.
- **Settings** — household, **week-start day**, budget, **leftovers mode**,
  editable **high-protein / low-carb thresholds**, **day preferences** (e.g. a quick
  Monday, a long-cook Sunday, a leftover Wednesday), and **Backup & restore**.

## Back up your data (important)

Because the data is on this one phone, use **Settings → Export backup** now and
then. It saves a small `.json` file you can drop into iCloud/Files. On a new phone,
install the app and use **Restore from file** to bring everything back.

---

## Moving to a hosted version later

This on-device app was built to make that switch easy. The separate Python
(FastAPI) backend from the earlier build is the hosting-ready version, and this
app's **Export** produces data in the same shape it understands. So switching is:
deploy the backend, import your exported `.json` to seed it, and point a hosted
copy of this UI at the server — not a rewrite. Automatic recipe import from a web
link is the one feature that only works in the hosted version (a phone browser
can't fetch other sites' pages directly); on-device you add recipes via the form.

## Files
```
meal-planner-iphone/
├─ index.html            # app shell
├─ app.js                # UI
├─ store.js              # data + logic (plan, shopping, nutrition, backup)
├─ seed.js               # the 200+ curated recipes
├─ styles.css            # styling (iOS safe-areas, no-zoom inputs)
├─ manifest.webmanifest  # PWA manifest
├─ service-worker.js     # offline caching
└─ icon-*.png / icon.svg # app icons
```
No build step, no dependencies — it's plain HTML/CSS/JS.
