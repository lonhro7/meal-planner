/* Auto-updating offline cache.
   NETWORK-FIRST for the app files: when online, always fetch the latest (so any
   change we deploy appears automatically — no reinstall, no version bump). When
   offline, fall back to the cached copy so the app still opens. Your data lives
   in IndexedDB on the device, separate from these files, so updates never touch it. */
const CACHE = "meals-ondevice";
const FILES = [
  "./", "./index.html", "./styles.css",
  "./seed.js", "./store.js", "./app.js",
  "./manifest.webmanifest", "./icon.svg",
  "./icon-180.png", "./icon-192.png", "./icon-512.png",
  "./data/ame-prices.json",
];

self.addEventListener("install", (e) => {
  // pre-cache once so the very first offline open works, then take over immediately
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) =>
    Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    fetch(e.request)
      .then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); return res; })
      .catch(() => caches.match(e.request))
  );
});
