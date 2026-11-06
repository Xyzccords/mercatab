// Guarda los archivos de la app para que abra sin internet.
const CACHE = 'mercatab-v2';
const ARCHIVOS = [
  './', 'index.html', 'manifest.webmanifest', 'css/estilos.css',
  'js/iconos.js', 'js/ui.js', 'js/datos.js', 'js/sunat.js', 'js/vistas.js', 'js/app.js',
  'fonts/atkinson-400.woff2', 'fonts/atkinson-700.woff2', 'img/icono.svg',
  'img/aceite.jpg', 'img/azucar.jpg', 'img/arroz.jpg', 'img/leche.jpg'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ARCHIVOS)));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(claves =>
    Promise.all(claves.filter(k => k !== CACHE).map(k => caches.delete(k)))));
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
