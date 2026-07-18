# Auto-updating setup (free) — Windows PC

Goal: whenever the app changes, your iPhone updates itself. No reinstalling, no
re-adding to the home screen, and your saved data is never touched (it lives in
the phone's own storage, separate from the app files).

## How it works (the mechanism)

1. The app files live in a **GitHub** repository (free).
2. A free host — **GitHub Pages** — automatically re-publishes the site every time
   the files in that repo change. You get one permanent `https://…` link.
3. You install the app to your home screen **once** from that link.
4. The app is now set to **auto-update**: each time you open it with internet, it
   quietly fetches the latest files and applies them. Offline, it still opens from
   its cached copy.

So the only recurring action is "the files in the repo change" — after that,
publishing and the phone update are automatic.

---

## One-time setup (~10 minutes, all free)

You only need a **GitHub account** (free). No Mac, no credit card, no Apple fee.

### 1. Create the repository
- Sign in at github.com → click **New repository**.
- Name it e.g. `meal-planner` → set **Public** → **Create repository**.

### 2. Upload the app files
- On the new repo page click **uploading an existing file**.
- Drag in **all the files from this `meal-planner-iphone` folder** (index.html,
  app.js, store.js, seed.js, styles.css, manifest.webmanifest, service-worker.js,
  and the icon files). Click **Commit changes**.

### 3. Turn on GitHub Pages
- In the repo: **Settings → Pages**.
- Under **Build and deployment → Source**, choose **Deploy from a branch**.
- Branch: **main**, folder: **/ (root)** → **Save**.
- Wait ~1 minute. The page shows your live link, like
  `https://YOURNAME.github.io/meal-planner/`.

### 4. Install on your iPhone
- Open that link in **Safari** on the iPhone.
- **Share → Add to Home Screen**. Done — open it from the icon.

That's it. It now runs full-screen, offline, and auto-updates.

---

## Making changes from now on

Whenever the app is updated, the new files just need to land in that GitHub repo.
Two ways:

- **Easy manual (20 seconds):** on the repo page, **Add file → Upload files**, drag
  the changed files in, **Commit**. GitHub Pages republishes automatically and your
  phone updates next time you open it. (This is the only manual touch, and it's
  tiny.)

- **Fully hands-off:** so that changes made in a Claude session publish themselves
  with zero action from you, connect GitHub to Claude once:
  - In Claude settings, enable **connector suggestions**, then connect the
    **GitHub** connector (or create a repo-scoped access token and share it with
    me). After that, in a session I can commit the changes straight to your repo →
    GitHub Pages redeploys → your phone updates. You do nothing.

---

## Good to know

- **Your data is safe across updates.** Recipes, plan, pantry, prices, favourites —
  all stored in the phone's on-device database, untouched by app updates. Keep using
  **Settings → Export backup** now and then as a belt-and-braces safety net.
- **Public repo, private data.** The repo only holds the app *code* (the same for
  everyone). None of your personal plan/pantry data is in it.
- **Alternative host:** Cloudflare Pages works the same way (connect the repo, auto
  deploys) if you'd prefer it over GitHub Pages — it just needs a second free
  account.
