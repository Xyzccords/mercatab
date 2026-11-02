// Datos de la app. Todo vive en localStorage del navegador: sin servidor, funciona sin internet.
// Los productos y ventas iniciales son datos de ejemplo para poder probar las pantallas.

const Red = {
  simulada: false, // interruptor del Perfil para demostrar el modo sin conexión
  enLinea: () => navigator.onLine && !Red.simulada
};

const Datos = (() => {
  const CLAVE = 'mercatab.v1';
  const CLAVE_RESPALDO = 'mercatab.respaldo';
  const redondear = n => Math.round(n * 100) / 100;
  let estado = cargar();

  function generador(semilla) { // mulberry32: números repetibles para los datos de ejemplo
    return () => {
      semilla |= 0; semilla = (semilla + 0x6D2B79F5) | 0;
      let t = Math.imul(semilla ^ (semilla >>> 15), 1 | semilla);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function semilla() {
    const productos = [
      { id: 'p1', nombre: 'Aceite Primor Vegetal (1L)', stock: 24, unidad: 'Unid.', precio: 9.8, costoUnit: 7.6, foto: 'img/aceite.jpg', altFoto: 'Botella de aceite vegetal de un litro' },
      { id: 'p2', nombre: 'Azúcar Rubia (1kg)', stock: 40, unidad: 'Unid.', precio: 4.5, costoUnit: 3.6, foto: 'img/azucar.jpg', altFoto: 'Vaso de vidrio lleno de azúcar rubia' },
      { id: 'p3', nombre: 'Arroz Costeño (5kg)', stock: 12, unidad: 'Unid.', precio: 20, costoUnit: 16.5, foto: 'img/arroz.jpg', altFoto: 'Bolsa de arroz de cinco kilos' },
      { id: 'p4', nombre: 'Leche Evaporada (400g)', stock: 60, unidad: 'Unid.', precio: 3.9, costoUnit: 3.1, foto: 'img/leche.jpg', altFoto: 'Caja de leche evaporada' }
    ];
    productos.forEach(p => { p.inversion = Math.round(p.costoUnit * p.stock * 100) / 100; });

    const azar = generador(7);
    const ahora = new Date();
    const ventas = [];
    for (let dia = 40; dia >= 0; dia--) {
      const cuantas = dia === 0 ? 3 : 2 + Math.floor(azar() * 3);
      for (let k = 0; k < cuantas; k++) {
        const fecha = new Date(ahora);
        if (dia === 0) fecha.setMinutes(fecha.getMinutes() - (k + 1) * 37);
        else { fecha.setDate(fecha.getDate() - dia); fecha.setHours(8 + Math.floor(azar() * 11), Math.floor(azar() * 60), 0, 0); }
        const lineas = 1 + Math.floor(azar() * 3);
        const elegidos = [...productos].sort(() => azar() - 0.5).slice(0, lineas);
        const items = elegidos.map(p => ({ productoId: p.id, nombre: p.nombre, cant: 1 + Math.floor(azar() * 4), precio: p.precio, costoUnit: p.costoUnit }));
        ventas.push({ id: 0, fecha: fecha.toISOString(), items, comprobante: null });
      }
    }
    ventas.sort((a, b) => a.fecha.localeCompare(b.fecha));
    ventas.forEach((v, i) => { v.id = i + 1; completar(v); });

    return { productos, ventas, ultimoProducto: 4, ultimaVenta: ventas.length, correlativos: { B001: 0, F001: 0 },
      sesion: null, negocio: { ruc: '', razon: '' }, premium: false, ultimoRespaldo: null };
  }

  function completar(venta) {
    venta.total = redondear(venta.items.reduce((s, i) => s + i.cant * i.precio, 0));
    venta.costo = redondear(venta.items.reduce((s, i) => s + i.cant * i.costoUnit, 0));
  }

  function cargar() {
    try {
      const guardado = localStorage.getItem(CLAVE);
      if (guardado) return JSON.parse(guardado);
    } catch (e) { /* almacenamiento bloqueado o dañado: se parte de los datos de ejemplo */ }
    return semilla();
  }

  function persistir() {
    try { localStorage.setItem(CLAVE, JSON.stringify(estado)); return true; }
    catch (e) { return false; }
  }

  function moverStock(items, signo) {
    items.forEach(i => { const p = estado.productos.find(x => x.id === i.productoId); if (p) p.stock = redondear(p.stock + signo * i.cant); });
  }

  return {
    persistir,
    redondear,
    productos: () => estado.productos,
    producto: id => estado.productos.find(p => p.id === id),

    guardarProducto(p) {
      p.costoUnit = p.stock > 0 ? redondear(p.inversion / p.stock) : 0;
      const i = estado.productos.findIndex(x => x.id === p.id);
      if (i < 0) { p.id = 'p' + (++estado.ultimoProducto); estado.productos.push(p); } else estado.productos[i] = p;
      return persistir();
    },
    eliminarProducto(id) { estado.productos = estado.productos.filter(p => p.id !== id); return persistir(); },

    ventas: () => estado.ventas,
    venta: id => estado.ventas.find(v => v.id === id),

    registrarVenta(items, comprobante) {
      const v = { id: ++estado.ultimaVenta, fecha: new Date().toISOString(), items, comprobante };
      completar(v);
      moverStock(items, -1);
      estado.ventas.push(v);
      return persistir() ? v : null;
    },
    reemplazarVenta(id, items) {
      const v = Datos.venta(id);
      moverStock(v.items, +1);
      v.items = items;
      completar(v);
      moverStock(items, -1);
      return persistir();
    },
    eliminarVenta(id) {
      const v = Datos.venta(id);
      moverStock(v.items, +1);
      estado.ventas = estado.ventas.filter(x => x.id !== id);
      return persistir();
    },

    siguienteCorrelativo(serie) { return ++estado.correlativos[serie]; },
    comprobantes: () => estado.ventas.filter(v => v.comprobante).sort((a, b) => b.fecha.localeCompare(a.fecha)),

    // Suma ventas, inversión (costo de lo vendido) y ganancia entre dos fechas (el fin es inclusivo por día).
    resumen(desde, hasta) {
      const ini = new Date(desde); ini.setHours(0, 0, 0, 0);
      const fin = new Date(hasta); fin.setHours(23, 59, 59, 999);
      const r = { ventas: 0, inversion: 0, cantidad: 0 };
      estado.ventas.forEach(v => {
        const f = new Date(v.fecha);
        if (f >= ini && f <= fin) { r.ventas += v.total; r.inversion += v.costo; r.cantidad++; }
      });
      r.ventas = redondear(r.ventas); r.inversion = redondear(r.inversion);
      r.ganancia = redondear(r.ventas - r.inversion);
      return r;
    },

    get sesion() { return estado.sesion; },
    set sesion(s) { estado.sesion = s; persistir(); },
    get negocio() { return estado.negocio; },
    set negocio(n) { estado.negocio = n; persistir(); },
    get premium() { return estado.premium; },
    set premium(p) { estado.premium = p; persistir(); },
    get ultimoRespaldo() { return estado.ultimoRespaldo; },

    respaldar() {
      try {
        estado.ultimoRespaldo = new Date().toISOString();
        localStorage.setItem(CLAVE_RESPALDO, JSON.stringify(estado));
        return persistir();
      } catch (e) { return false; }
    },
    hayRespaldo: () => !!localStorage.getItem(CLAVE_RESPALDO),
    restaurar() {
      try { estado = JSON.parse(localStorage.getItem(CLAVE_RESPALDO)); return persistir(); }
      catch (e) { return false; }
    },
    reiniciar() { estado = semilla(); return persistir(); }
  };
})();
