// Arranque de la app: rutas con hash (#/productos), barra de navegación, estado de red y aviso de cambios sin guardar.
(() => {
  const principal = document.getElementById('contenido');
  const barra = document.getElementById('barra');
  let hashActual = location.hash;

  const ctx = {
    sucio: false,
    setSucio(v) { ctx.sucio = v; },
    ir(hash) { ctx.sucio = false; if (location.hash === hash) pintar(); else location.hash = hash; },
    repintar() { pintar(false); },
    actualizarRed
  };

  const RUTAS = [
    ['inicio', () => Vistas.inicio()],
    ['productos', c => Vistas.productos(c)],
    ['productos/nuevo', c => Vistas.productoForm(c, {})],
    ['productos/editar/:id', (c, p) => Vistas.productoForm(c, p)],
    ['ventas', c => Vistas.ventas(c)],
    ['ventas/nueva', c => Vistas.ventaForm(c, {})],
    ['ventas/editar/:id', (c, p) => Vistas.ventaForm(c, p)],
    ['ganancias', () => Vistas.ganancias()],
    ['perfil', c => Vistas.perfil(c)],
    ['login', c => Vistas.login(c)],
    ['registro', c => Vistas.registro(c)],
    ['premium', c => Vistas.premium(c)],
    ['negocio', c => Vistas.negocio(c)],
    ['comprobantes', c => Vistas.comprobantes(c)],
    ['comprobantes/:id', (c, p) => Vistas.comprobante(c, p)]
  ];

  const NAV = [['inicio', 'Inicio'], ['productos', 'Productos'], ['ventas', 'Ventas'], ['ganancias', 'Ganancias'], ['perfil', 'Perfil']];
  barra.innerHTML = NAV.map(([id, texto]) => `<a href="#/${id}" data-nav="${id}">${icono(id)}<span>${texto}</span></a>`).join('');

  function buscarRuta(ruta) {
    const partes = ruta.split('/');
    for (const [patron, fabrica] of RUTAS) {
      const pp = patron.split('/');
      if (pp.length !== partes.length) continue;
      const params = {};
      if (pp.every((x, i) => x.startsWith(':') ? (params[x.slice(1)] = partes[i], true) : x === partes[i])) return { fabrica, params };
    }
    return null;
  }

  // moverFoco: al cambiar de pantalla el foco pasa al título, para que teclado y lector de pantalla sepan dónde están.
  function pintar(moverFoco = true) {
    ctx.sucio = false;
    const ruta = location.hash.startsWith('#/') ? location.hash.slice(2) : 'inicio';
    const encontrada = buscarRuta(ruta) || buscarRuta('inicio');
    const vista = encontrada.fabrica(ctx, encontrada.params);
    document.title = `${vista.titulo} · MercaTab`;
    barra.querySelectorAll('a').forEach(a => {
      if (a.dataset.nav === vista.nav) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    principal.innerHTML = '';
    ['onclick', 'oninput', 'onchange', 'onsubmit'].forEach(e => { principal[e] = null; }); // cada pantalla conecta los suyos
    vista.montar(principal);
    if (moverFoco) { window.scrollTo(0, 0); (principal.querySelector('h1') || principal).focus({ preventScroll: true }); }
  }

  window.addEventListener('hashchange', async () => {
    if (ctx.sucio) {
      const destino = location.hash;
      history.replaceState(null, '', hashActual || '#/inicio');
      const salir = await UI.modal({
        titulo: '¿Estás seguro de querer salir sin guardar cambios?', icono: 'alerta', tono: 'aviso', escape: 0,
        botones: [{ texto: 'Continuar editando', valor: false }, { texto: 'Sí, salir', clase: 'boton--peligro', valor: true }]
      });
      if (salir) { ctx.sucio = false; location.hash = destino; }
      return;
    }
    hashActual = location.hash;
    pintar();
  });
  window.addEventListener('beforeunload', e => { if (ctx.sucio) e.preventDefault(); });

  function actualizarRed() {
    document.getElementById('red').innerHTML = Red.enLinea() ? '' : `<span class="red__chip">${icono('sinred')}Sin conexión · Guardado en tu celular</span>`;
    if (Red.enLinea()) {
      const n = Sunat.enviarPendientes();
      if (n) UI.aviso(`Volvió internet: se enviaron ${n} ${n === 1 ? 'comprobante' : 'comprobantes'} a SUNAT (simulado).`);
    }
  }
  window.addEventListener('online', () => { actualizarRed(); pintar(false); });
  window.addEventListener('offline', () => { actualizarRed(); pintar(false); });

  document.getElementById('saltar').addEventListener('click', e => { e.preventDefault(); principal.focus(); });

  if ('serviceWorker' in navigator && location.protocol.startsWith('http')) navigator.serviceWorker.register('sw.js');

  actualizarRed();
  pintar(false);
})();
