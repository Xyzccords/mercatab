// Iconos de trazo simple. Siempre van con aria-hidden: el texto o el aria-label del botón los explica.
const ICONOS = {
  inicio: '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
  productos: '<rect x="3" y="4" width="18" height="5" rx="1"/><path d="M5 9v11h14V9"/><path d="M10 13h4"/>',
  ventas: '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6M9 16h3"/>',
  ganancias: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/><path d="M6 12h.01M18 12h.01"/>',
  perfil: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
  caja: '<rect x="4" y="3" width="16" height="6" rx="1"/><path d="M6 9l-2 6h16l-2-6"/><rect x="3" y="15" width="18" height="6" rx="1"/><path d="M8 18h2M14 18h2"/>',
  mas: '<path d="M12 5v14M5 12h14"/>',
  lapiz: '<path d="M4 20l1-5L16 4l4 4L9 19z"/><path d="M14 6l4 4"/>',
  papelera: '<path d="M4 7h16M10 11v6M14 11v6"/><path d="M6 7l1 13h10l1-13"/><path d="M9 7V4h6v3"/>',
  buscar: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
  volver: '<path d="M19 12H5M11 6l-6 6 6 6"/>',
  calendario: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
  check: '<path d="M5 12l5 5 9-10"/>',
  alerta: '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
  sinred: '<path d="M2 8.5a15 15 0 0 1 4-2.5M22 8.5a15 15 0 0 0-11-3.5M5 12.5a10 10 0 0 1 3-2M19 12.5a10 10 0 0 0-5-2.5M8.5 16a5 5 0 0 1 7 0"/><path d="M12 20h.01"/><path d="M3 3l18 18"/>',
  guardar: '<path d="M5 3h12l3 3v15H5z"/><path d="M8 3v6h8V3M8 21v-7h8v7"/>',
  cerrar: '<path d="M6 6l12 12M18 6L6 18"/>',
  ojo: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  camara: '<path d="M4 8h3l2-3h6l2 3h3v12H4z"/><circle cx="12" cy="13" r="3.5"/>',
  nube: '<path d="M7 18a4 4 0 0 1 0-8 5.5 5.5 0 0 1 10.5 1.5A3.5 3.5 0 0 1 17 18z"/>',
  estrella: '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
  documento: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
  siguiente: '<path d="M9 6l6 6-6 6"/>',
  registro: '<circle cx="10" cy="8" r="4"/><path d="M2 21c0-4 3.6-6 8-6M18 14v6M15 17h6"/>',
  entrar: '<path d="M10 4H5v16h5M14 8l4 4-4 4M18 12H9"/>',
  negocio: '<path d="M4 21V8l8-5 8 5v13"/><path d="M9 21v-6h6v6"/>'
};

function icono(nombre, clase = '') {
  return `<svg class="icono ${clase}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${ICONOS[nombre] || ''}</svg>`;
}
