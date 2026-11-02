// Service worker : permet d'installer l'appli et de l'utiliser hors connexion.
// L'appli et les images sont mises en cache à l'installation ; les sons (banque General MIDI,
// MP3 de secours) au fur et à mesure qu'on les écoute.
const CACHE = 'atelier-harmonie-@@VERSION@@';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png'];
const IMAGES = @@IMAGES@@;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(async c => {
    await c.addAll(FILES);
    await Promise.all(IMAGES.map(u => c.add(u).catch(() => {})));
  }));
  self.skipWaiting();
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('atelier-harmonie-') && k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = e.request.url;
  const banque = url.includes('midi-js-soundfonts');
  if (banque) {   // les sons ne changent jamais : cache d'abord
    e.respondWith(caches.match(e.request).then(m => m || fetch(e.request).then(r => {
      if (r.ok) { const copie = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copie)); }
      return r;
    })));
    return;
  }
  // réseau d'abord (pour recevoir les mises à jour), cache en secours hors connexion
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok && url.startsWith(self.location.origin)) { const copie = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copie)); }
    return r;
  }).catch(() => caches.match(e.request).then(m => m || caches.match('./index.html'))));
});
