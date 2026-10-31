// Tiene l'app disponibile anche senza connessione. Il catalogo e i prezzi restano sempre online.
const CACHE = "raccoglitore-v5";
const STATIC = "statici-ocr-5.1.1-cjk-font-1";   // lettore del numero e caratteri: non cambiano, si scaricano una volta sola
const IMG = "carte-img";
const IMG_MAX = 1500;                        // limite alle immagini salvate, per non riempire la memoria del telefono
const SHELL = ["./", "index.html", "guida.html", "manifest.webmanifest", "icon-180.png", "icon-192.png", "fonts/fonts.css"];

self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => ![CACHE, STATIC, IMG].includes(k)).map(k => caches.delete(k)))));
  self.clients.claim();
});

async function trim(cache, max) {
  const keys = await cache.keys();
  for (let i = 0; i < keys.length - max; i++) await cache.delete(keys[i]);
}

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  if (url.origin === location.origin) {
    // Lettore del numero e caratteri: prima la copia salvata.
    if (/\/(ocr|fonts)\//.test(url.pathname)) {
      e.respondWith(caches.open(STATIC).then(async c => {
        const hit = await c.match(e.request);
        if (hit) return hit;
        const r = await fetch(e.request);
        if (r.ok) c.put(e.request, r.clone());
        return r;
      }));
      return;
    }
    // Pagine dell'app: prima la rete (per ricevere gli aggiornamenti), poi la copia salvata.
    e.respondWith(fetch(e.request).then(r => {
      if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return r;
    }).catch(() => caches.match(e.request).then(r => r || caches.match("index.html"))));
    return;
  }
  // Immagini delle carte: copia salvata se c'è, così il raccoglitore si sfoglia anche offline.
  if (url.hostname === "assets.tcgdex.net") {
    e.respondWith(caches.open(IMG).then(async c => {
      const hit = await c.match(e.request);
      if (hit) return hit;
      const r = await fetch(e.request);
      if (r.ok || r.type === "opaque") { await c.put(e.request, r.clone()); trim(c, IMG_MAX); }
      return r;
    }));
  }
});
