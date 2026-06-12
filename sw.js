const CACHE_NAME = 'servis-hr-v3';
const STATIC_CACHE = 'servis-hr-static-v3';

const STATIC_FILES = [
  './',
  './index.html',
  './dashboard.html',
  './leave.html',
  './attendance.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
];

// These files should NEVER be cached - always fresh from network
const NO_CACHE = [
  'attendance_data.json',
  'leave_data.json',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => cache.addAll(STATIC_FILES))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== STATIC_CACHE).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  const filename = url.pathname.split('/').pop();

  // JSON data files: always fetch fresh from network, never cache
  if (NO_CACHE.includes(filename)) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' })
        .catch(() => new Response('{}', { headers: { 'Content-Type': 'application/json' } }))
    );
    return;
  }

  // Static files: serve from cache, fallback to network
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
