// Pantallas. Cada una devuelve { titulo, nav, montar(root) }; montar() dibuja la pantalla y conecta sus eventos.
// ctx lo pone app.js: ir() navega, repintar() vuelve a dibujar la pantalla actual, setSucio() avisa que hay cambios sin guardar.

const Vistas = (() => {
  const { esc, dinero, fechaCorta, hora, fechaLarga, isoLocal, modal, confirmar, errorGuardar, aviso, campo, resumenErrores, encabezado } = UI;
  const $ = (raiz, sel) => raiz.querySelector(sel);
  const num = v => (String(v).trim() === '' ? NaN : Number(v));
  const plural = (n, uno, varios) => `${n} ${n === 1 ? uno : varios}`;

  const enfocarResumen = root => { const r = $(root, '#resumen-errores'); if (r) r.focus(); };
  const irACampo = (e, root) => { const b = e.target.closest('[data-ir]'); if (b) { const c = root.querySelector('#' + b.dataset.ir); if (c) c.focus(); } };

  const fotoDe = p => p.foto
    ? `<img class="fila__foto" src="${esc(p.foto)}" alt="${esc(p.altFoto || 'Foto de ' + p.nombre)}" width="64" height="64">`
    : `<span class="fila__foto fila__foto--vacia" aria-hidden="true">${icono('productos')}</span>`;

  /* ---------- Inicio ---------- */
  function inicio() {
    return { titulo: 'Inicio', nav: 'inicio', montar(root) {
      const hoy = new Date();
      const r = Datos.resumen(hoy, hoy);
      const ultimas = Datos.ventas().slice(-3).reverse();
      const pendientes = Datos.comprobantes().filter(v => v.comprobante.estado === 'pendiente').length;
      root.innerHTML = `
        <div class="encab"><h1 tabindex="-1">Resumen de hoy</h1></div>
        <p class="ayuda">${esc(fechaLarga(hoy))}</p>
        <dl class="stats">
          <div><dt>Ventas hoy</dt><dd>${r.cantidad}</dd></div>
          <div><dt>Ingreso hoy</dt><dd>${dinero(r.ventas)}</dd></div>
          <div class="ancha"><dt>Ganancia neta hoy</dt><dd>${dinero(r.ganancia)}</dd></div>
        </dl>
        <div class="acciones-rapidas">
          <a class="boton" href="#/ventas/nueva">${icono('caja')}<span>Registrar venta</span></a>
          <a class="boton boton--sec" href="#/productos/nuevo">${icono('productos')}<span>Agregar productos</span></a>
        </div>
        ${pendientes ? `<p class="nota">${plural(pendientes, 'comprobante espera', 'comprobantes esperan')} conexión para enviarse a SUNAT. <a href="#/comprobantes">Ver comprobantes</a></p>` : ''}
        <h2>Actividad reciente</h2>
        ${ultimas.length ? `<ul class="lista">${ultimas.map(v => `
          <li class="fila">
            <span class="fila__foto fila__foto--vacia" aria-hidden="true">${icono('ventas')}</span>
            <div class="fila__texto"><p class="fila__titulo">Venta n.º ${v.id}</p><p class="fila__detalle">${fechaCorta(v.fecha)} · ${hora(v.fecha)}</p></div>
            <p class="fila__precio">+${dinero(v.total)}</p>
          </li>`).join('')}</ul>` : '<div class="vacio"><p>Todavía no hay ventas. Registra la primera.</p></div>'}`;
    } };
  }

  /* ---------- Productos ---------- */
  function productos(ctx) {
    return { titulo: 'Productos', nav: 'productos', montar(root) {
      let filtro = '';
      const filas = () => {
        const ps = Datos.productos().filter(p => p.nombre.toLowerCase().includes(filtro.trim().toLowerCase()));
        if (!ps.length) return `<div class="vacio"><p>${filtro ? 'Ningún producto coincide con la búsqueda.' : 'Aún no tienes productos.'}</p>${filtro ? '' : '<a class="boton" href="#/productos/nuevo">Agregar el primero</a>'}</div>`;
        return `<ul class="lista">${ps.map(p => `
          <li class="fila">
            ${fotoDe(p)}
            <div class="fila__texto">
              <p class="fila__titulo">${esc(p.nombre)}</p>
              <p class="fila__precio">${dinero(p.precio)}</p>
              <p class="fila__detalle">Stock: ${p.stock} ${esc(p.unidad)}${p.stock <= 5 ? ' · <strong>Stock bajo</strong>' : ''}</p>
            </div>
            <div class="acciones">
              <a class="boton boton--icono boton--sec" href="#/productos/editar/${p.id}" aria-label="Editar ${esc(p.nombre)}">${icono('lapiz')}</a>
              <button type="button" class="boton boton--icono boton--peligro" data-accion="eliminar" data-id="${p.id}" aria-label="Eliminar ${esc(p.nombre)}">${icono('papelera')}</button>
            </div>
          </li>`).join('')}</ul>`;
      };
      root.innerHTML = `
        ${encabezado('Productos', { ic: 'productos', accion: { href: '#/productos/nuevo', texto: 'Nuevo producto' } })}
        <div class="campo"><label for="buscar">Buscar productos</label><input id="buscar" type="search" autocomplete="off" placeholder="Ej. arroz"></div>
        <div id="resultado" aria-live="polite">${filas()}</div>`;
      root.oninput = e => { if (e.target.id === 'buscar') { filtro = e.target.value; $(root, '#resultado').innerHTML = filas(); } };
      root.onclick = async e => {
        const b = e.target.closest('[data-accion="eliminar"]');
        if (!b) return;
        const p = Datos.producto(b.dataset.id);
        const ok = await confirmar({ titulo: '¿Eliminar producto?', texto: `Se eliminará «${esc(p.nombre)}» con su stock (${p.stock} ${esc(p.unidad)}). Las ventas ya registradas se mantienen. Esta acción no se puede deshacer.`, si: 'Eliminar' });
        if (ok && Datos.eliminarProducto(p.id)) { aviso('Producto eliminado.'); ctx.repintar(); }
      };
    } };
  }

  function reducirImagen(archivo) {
    return new Promise(ok => {
      const lector = new FileReader();
      lector.onload = () => {
        const img = new Image();
        img.onload = () => {
          const escala = Math.min(1, 256 / Math.max(img.width, img.height));
          const lienzo = document.createElement('canvas');
          lienzo.width = Math.round(img.width * escala); lienzo.height = Math.round(img.height * escala);
          lienzo.getContext('2d').drawImage(img, 0, 0, lienzo.width, lienzo.height);
          ok(lienzo.toDataURL('image/jpeg', 0.8));
        };
        img.onerror = () => ok('');
        img.src = lector.result;
      };
      lector.readAsDataURL(archivo);
    });
  }

  function productoForm(ctx, params) {
    const original = params.id ? Datos.producto(params.id) : null;
    return { titulo: original ? 'Editar producto' : 'Agregar producto', nav: 'productos', montar(root) {
      if (params.id && !original) { ctx.ir('#/productos'); return; }
      let v = original
        ? { nombre: original.nombre, stock: original.stock, unidad: original.unidad, precio: original.precio, inversion: original.inversion, foto: original.foto || '', altFoto: original.altFoto || '' }
        : { nombre: '', stock: '', unidad: 'Unid.', precio: '', inversion: '', foto: '', altFoto: '' };
      let errores = [];
      const err = id => (errores.find(e => e.id === id) || {}).mensaje || '';

      const pintar = () => {
        root.innerHTML = `
          ${encabezado(original ? 'Editar producto' : 'Agregar producto', { atras: '#/productos' })}
          ${resumenErrores(errores)}
          <form id="f" novalidate>
            ${campo({ id: 'nombre', etiqueta: 'Nombre del producto', valor: v.nombre, requerido: true, error: err('nombre'), atributos: 'autocomplete="off" maxlength="60" placeholder="Ej. Arroz Costeño (5kg)"' })}
            <div class="dos-col">
              ${campo({ id: 'stock', etiqueta: 'Stock', tipo: 'number', valor: v.stock, requerido: true, error: err('stock'), atributos: 'inputmode="decimal" min="0" step="any" autocomplete="off" placeholder="0"' })}
              <div class="campo"><label for="unidad">Unidad</label>
                <select id="unidad" autocomplete="off">${['Unid.', 'kg', 'L'].map(u => `<option${u === v.unidad ? ' selected' : ''}>${u}</option>`).join('')}</select></div>
            </div>
            ${campo({ id: 'precio', etiqueta: 'Precio por unidad (S/)', tipo: 'number', valor: v.precio, ayuda: 'A cuánto vendes cada unidad.', requerido: true, error: err('precio'), atributos: 'inputmode="decimal" min="0" step="0.01" autocomplete="off" placeholder="0.00"' })}
            ${campo({ id: 'inversion', etiqueta: 'Inversión total (S/)', tipo: 'number', valor: v.inversion, ayuda: 'Lo que pagaste por todo el stock que registras.', requerido: true, error: err('inversion'), atributos: 'inputmode="decimal" min="0" step="0.01" autocomplete="off" placeholder="0.00"' })}
            <div class="campo">
              <label for="foto">Foto del producto (opcional)</label>
              ${v.foto ? `<img class="foto-previa" src="${esc(v.foto)}" alt="Vista previa de la foto del producto">` : ''}
              <input id="foto" type="file" accept="image/*" autocomplete="off">
            </div>
            <div class="fila-botones">
              <button type="submit" class="boton">${icono('guardar')}<span>Guardar</span></button>
              <a class="boton boton--peligro" href="#/productos">${icono('cerrar')}<span>Cancelar</span></a>
            </div>
          </form>`;
      };
      const leer = () => {
        v = { ...v, nombre: $(root, '#nombre').value, stock: $(root, '#stock').value, unidad: $(root, '#unidad').value,
          precio: $(root, '#precio').value, inversion: $(root, '#inversion').value };
      };
      const validar = () => {
        const e = [];
        if (!v.nombre.trim()) e.push({ id: 'nombre', mensaje: 'Escribe el nombre del producto. Ejemplo: Arroz Costeño (5kg).' });
        if (!(num(v.stock) >= 0)) e.push({ id: 'stock', mensaje: 'El stock debe ser un número, 0 o mayor.' });
        if (!(num(v.precio) > 0)) e.push({ id: 'precio', mensaje: 'El precio por unidad debe ser mayor que 0.' });
        if (!(num(v.inversion) >= 0)) e.push({ id: 'inversion', mensaje: 'Escribe cuánto pagaste por el stock. Si fue gratis, pon 0.' });
        return e;
      };

      pintar();
      root.oninput = () => ctx.setSucio(true);
      root.onclick = e => irACampo(e, root);
      root.onchange = async e => {
        if (e.target.id !== 'foto' || !e.target.files[0]) return;
        leer();
        v.foto = await reducirImagen(e.target.files[0]);
        v.altFoto = 'Foto de ' + (v.nombre.trim() || 'el producto');
        pintar();
        $(root, '#foto').focus();
      };
      root.onsubmit = async e => {
        e.preventDefault();
        leer();
        errores = validar();
        if (errores.length) { pintar(); enfocarResumen(root); return; }
        const p = { id: original ? original.id : '', nombre: v.nombre.trim(), stock: num(v.stock), unidad: v.unidad, precio: num(v.precio),
          inversion: num(v.inversion), foto: v.foto, altFoto: v.foto ? (v.altFoto || 'Foto de ' + v.nombre.trim()) : '' };
        while (!Datos.guardarProducto(p)) { if (await errorGuardar() === 'volver') return; }
        ctx.setSucio(false);
        const botones = original
          ? [{ texto: 'Aceptar', valor: 'ok' }]
          : [{ texto: 'Aceptar', valor: 'ok' }, { texto: 'Agregar nuevo producto', clase: 'boton--sec', valor: 'otro' }];
        const r = await modal({ titulo: original ? '¡Cambios guardados!' : '¡Producto registrado!', icono: 'check', tono: 'ok', escape: 0,
          texto: original ? 'Los datos del producto ya están al día.' : 'Tu artículo ya está disponible en el inventario.', botones });
        ctx.ir(r === 'otro' ? '#/productos/nuevo' : '#/productos');
      };
    } };
  }

  /* ---------- Ventas ---------- */
  function ventas(ctx) {
    return { titulo: 'Ventas', nav: 'ventas', montar(root) {
      const hoy = new Date();
      const hace30 = new Date(); hace30.setDate(hoy.getDate() - 30);
      let desde = isoLocal(hace30), hasta = isoLocal(hoy);
      const PASO = 15; // la lista es corta para que quien usa solo teclado llegue pronto a la barra de navegación
      let mostrar = PASO;
      const filas = () => {
        const ini = new Date(desde + 'T00:00:00'), fin = new Date(hasta + 'T23:59:59');
        const lista = Datos.ventas().filter(v => { const f = new Date(v.fecha); return f >= ini && f <= fin; }).reverse();
        if (!lista.length) return '<div class="vacio"><p>No hay ventas en estas fechas.</p></div>';
        return `<ul class="lista">${lista.slice(0, mostrar).map(v => `
          <li class="fila">
            <div class="fila__texto">
              <p class="fila__titulo">Venta n.º ${v.id}</p>
              <p class="fila__detalle">${fechaCorta(v.fecha)} · ${hora(v.fecha)}</p>
              <p class="fila__precio">${dinero(v.total)}</p>
              ${v.comprobante ? `<p class="fila__detalle"><span class="etiqueta ${v.comprobante.estado === 'aceptado' ? 'etiqueta--ok' : 'etiqueta--pend'}">${icono(v.comprobante.estado === 'aceptado' ? 'check' : 'sinred')}${esc(v.comprobante.codigo)} · ${v.comprobante.estado === 'aceptado' ? 'Aceptado' : 'Pendiente'}</span></p>` : ''}
            </div>
            <div class="acciones">
              ${v.comprobante
                ? `<a class="boton boton--icono boton--sec" href="#/comprobantes/${v.id}" aria-label="Ver comprobante ${esc(v.comprobante.codigo)}">${icono('documento')}</a>`
                : `<a class="boton boton--icono boton--sec" href="#/ventas/editar/${v.id}" aria-label="Editar venta ${v.id}">${icono('lapiz')}</a>
                   <button type="button" class="boton boton--icono boton--peligro" data-accion="eliminar" data-id="${v.id}" aria-label="Eliminar venta ${v.id}">${icono('papelera')}</button>`}
            </div>
          </li>`).join('')}</ul><p class="ayuda">Mostrando ${Math.min(mostrar, lista.length)} de ${plural(lista.length, 'venta', 'ventas')}.</p>${lista.length > mostrar ? `<button type="button" class="boton boton--sec boton--bloque" data-accion="mas">Mostrar ${Math.min(PASO, lista.length - mostrar)} más</button>` : ''}`;
      };
      root.innerHTML = `
        ${encabezado('Ventas', { ic: 'ventas', accion: { href: '#/ventas/nueva', texto: 'Nueva venta' } })}
        <div class="filtros">
          ${campo({ id: 'desde', etiqueta: 'Desde', tipo: 'date', valor: desde, atributos: 'autocomplete="off"' })}
          ${campo({ id: 'hasta', etiqueta: 'Hasta', tipo: 'date', valor: hasta, atributos: 'autocomplete="off"' })}
        </div>
        <p><a class="boton boton--sec boton--chico" href="#/comprobantes">${icono('documento')}<span>Comprobantes SUNAT</span></a></p>
        <div id="resultado" aria-live="polite">${filas()}</div>`;
      root.onchange = e => {
        if (e.target.id === 'desde') desde = e.target.value || desde;
        else if (e.target.id === 'hasta') hasta = e.target.value || hasta;
        else return;
        mostrar = PASO;
        $(root, '#resultado').innerHTML = filas();
      };
      root.onclick = async e => {
        if (e.target.closest('[data-accion="mas"]')) {
          mostrar += PASO;
          $(root, '#resultado').innerHTML = filas();
          const nuevos = root.querySelectorAll('#resultado .fila');
          const primero = nuevos[mostrar - PASO] && nuevos[mostrar - PASO].querySelector('a, button');
          if (primero) primero.focus();
          return;
        }
        const b = e.target.closest('[data-accion="eliminar"]');
        if (!b) return;
        const v = Datos.venta(Number(b.dataset.id));
        const ok = await confirmar({ titulo: '¿Eliminar venta?', texto: `Se quitará la venta n.º ${v.id} por ${dinero(v.total)} y el stock vuelve al inventario. Esta acción no se puede deshacer.`, si: 'Eliminar' });
        if (ok && Datos.eliminarVenta(v.id)) { aviso('Venta eliminada.'); ctx.repintar(); }
      };
    } };
  }

  function ventaForm(ctx, params) {
    const original = params.id ? Datos.venta(Number(params.id)) : null;
    return { titulo: original ? 'Editar venta' : 'Agregar venta', nav: 'ventas', montar(root) {
      if (params.id && (!original || original.comprobante)) { ctx.ir(original ? '#/comprobantes/' + original.id : '#/ventas'); return; }
      let lineas = original ? original.items.map(i => ({ productoId: i.productoId, cant: String(i.cant) })) : [{ productoId: '', cant: '' }];
      let tipo = 'ninguno', doc = { numero: '', nombre: '' };
      let errores = [];
      const err = id => (errores.find(e => e.id === id) || {}).mensaje || '';
      const disponible = id => { const p = Datos.producto(id); if (!p) return 0; const antes = original ? original.items.filter(i => i.productoId === id).reduce((s, i) => s + i.cant, 0) : 0; return p.stock + antes; };
      const total = () => Datos.redondear(lineas.reduce((s, l) => { const p = Datos.producto(l.productoId); const c = num(l.cant); return s + (p && c > 0 ? p.precio * c : 0); }, 0));

      const lineaHTML = (l, i) => {
        const eP = err('prod-' + i), eC = err('cant-' + i);
        const opciones = Datos.productos().map(p => `<option value="${p.id}"${p.id === l.productoId ? ' selected' : ''}>${esc(p.nombre)} · stock ${p.stock}</option>`).join('');
        return `
          <div class="linea-venta">
            <div class="campo ${eP ? 'campo--error' : ''}"><label for="prod-${i}">Producto</label>
              <select id="prod-${i}" autocomplete="off"${eP ? ` aria-invalid="true" aria-describedby="prod-${i}-error"` : ''}><option value="">Seleccionar producto</option>${opciones}</select></div>
            <div class="campo ${eC ? 'campo--error' : ''}"><label for="cant-${i}">Cantidad</label>
              <input id="cant-${i}" type="number" inputmode="decimal" min="0" step="any" autocomplete="off" value="${esc(l.cant)}"${eC ? ` aria-invalid="true" aria-describedby="cant-${i}-error"` : ''}></div>
            <button type="button" class="boton boton--icono boton--peligro" data-accion="quitar" data-i="${i}" aria-label="Quitar el producto ${i + 1} de la venta"${lineas.length === 1 ? ' disabled' : ''}>${icono('papelera')}</button>
            ${eP ? `<p class="error" id="prod-${i}-error">${icono('alerta')}<span>${esc(eP)}</span></p>` : ''}
            ${eC ? `<p class="error" id="cant-${i}-error">${icono('alerta')}<span>${esc(eC)}</span></p>` : ''}
          </div>`;
      };
      const clienteHTML = () => `
        <div class="consulta">
          ${campo({ id: 'doc-numero', etiqueta: tipo === 'factura' ? 'RUC del cliente' : 'DNI del cliente (opcional)', valor: doc.numero, requerido: tipo === 'factura', error: err('doc-numero'),
            ayuda: `Datos de ejemplo: RUC ${Sunat.ejemplos.rucs[0]} o DNI ${Sunat.ejemplos.dni[0]}.`, atributos: `inputmode="numeric" maxlength="${tipo === 'factura' ? 11 : 8}" autocomplete="off"` })}
          <button type="button" class="boton boton--sec" data-accion="consultar">Consultar SUNAT</button>
        </div>
        <p class="consulta__estado" id="consulta-estado" role="status"></p>
        ${campo({ id: 'doc-nombre', etiqueta: tipo === 'factura' ? 'Razón social' : 'Nombre del cliente (opcional)', valor: doc.nombre, requerido: tipo === 'factura', error: err('doc-nombre'),
          atributos: `autocomplete="${tipo === 'factura' ? 'organization' : 'name'}"` })}`;

      const pintar = () => {
        root.innerHTML = `
          ${encabezado(original ? 'Editar venta' : 'Agregar venta', { atras: '#/ventas' })}
          ${resumenErrores(errores)}
          <form id="f" novalidate>
            ${lineas.map(lineaHTML).join('')}
            <button type="button" class="boton boton--sec boton--bloque" data-accion="mas">${icono('mas')}<span>Agregar producto</span></button>
            <div class="total"><span>Total</span><strong id="total" aria-live="polite">${dinero(total())}</strong></div>
            ${original ? '' : `
            <fieldset class="opciones">
              <legend>Comprobante electrónico</legend>
              <label><input type="radio" name="tipo" value="ninguno"${tipo === 'ninguno' ? ' checked' : ''}> Sin comprobante</label>
              <label><input type="radio" name="tipo" value="boleta"${tipo === 'boleta' ? ' checked' : ''}> Boleta de venta</label>
              <label><input type="radio" name="tipo" value="factura"${tipo === 'factura' ? ' checked' : ''}> Factura</label>
            </fieldset>
            ${tipo === 'ninguno' ? '' : clienteHTML()}`}
            <div class="fila-botones">
              <button type="submit" class="boton">${icono('guardar')}<span>Guardar</span></button>
              <a class="boton boton--peligro" href="#/ventas">${icono('cerrar')}<span>Cancelar</span></a>
            </div>
          </form>`;
      };
      const leer = () => {
        lineas = lineas.map((l, i) => ({ productoId: $(root, '#prod-' + i).value, cant: $(root, '#cant-' + i).value }));
        const t = $(root, 'input[name="tipo"]:checked'); if (t) tipo = t.value;
        const n = $(root, '#doc-numero'), m = $(root, '#doc-nombre');
        if (n) doc = { numero: n.value.trim(), nombre: m.value.trim() };
      };
      const validar = () => {
        const e = [];
        const llenas = lineas.map((l, i) => ({ ...l, i })).filter(l => l.productoId || l.cant !== '');
        if (!llenas.length) e.push({ id: 'prod-0', mensaje: 'Agrega al menos un producto a la venta.' });
        const vistos = new Set();
        llenas.forEach(l => {
          const p = Datos.producto(l.productoId), c = num(l.cant);
          if (!p) e.push({ id: 'prod-' + l.i, mensaje: 'Elige el producto que vendiste.' });
          else if (vistos.has(p.id)) e.push({ id: 'prod-' + l.i, mensaje: 'Este producto ya está en otra fila: suma las cantidades en una sola.' });
          else vistos.add(p.id);
          if (!(c > 0)) e.push({ id: 'cant-' + l.i, mensaje: 'Escribe una cantidad mayor que 0.' });
          else if (p && c > disponible(p.id)) e.push({ id: 'cant-' + l.i, mensaje: `Solo quedan ${disponible(p.id)} ${p.unidad} de ${p.nombre}.` });
        });
        if (tipo === 'factura') {
          if (!Sunat.rucValido(doc.numero)) e.push({ id: 'doc-numero', mensaje: 'El RUC debe tener 11 dígitos y ser válido (empieza con 10 o 20).' });
          if (!doc.nombre) e.push({ id: 'doc-nombre', mensaje: 'Escribe la razón social del cliente o usa Consultar SUNAT.' });
        } else if (tipo === 'boleta') {
          if (doc.numero && !Sunat.dniValido(doc.numero)) e.push({ id: 'doc-numero', mensaje: 'El DNI debe tener 8 dígitos.' });
          if (!doc.numero && total() >= Sunat.LIMITE_BOLETA_SIN_DNI) e.push({ id: 'doc-numero', mensaje: `Desde ${dinero(Sunat.LIMITE_BOLETA_SIN_DNI)} la boleta necesita el DNI del cliente.` });
        }
        return e;
      };

      pintar();
      root.oninput = e => { ctx.setSucio(true); if (/^(prod|cant)-/.test(e.target.id)) { leer(); $(root, '#total').textContent = dinero(total()); } };
      root.onchange = e => {
        if (e.target.name === 'tipo') { leer(); errores = []; pintar(); $(root, `input[name="tipo"][value="${tipo}"]`).focus(); }
        else if (/^prod-/.test(e.target.id)) { leer(); $(root, '#total').textContent = dinero(total()); }
      };
      root.onclick = async e => {
        irACampo(e, root);
        const b = e.target.closest('[data-accion]');
        if (!b) return;
        const accion = b.dataset.accion;
        if (accion === 'mas') { leer(); lineas.push({ productoId: '', cant: '' }); pintar(); $(root, '#prod-' + (lineas.length - 1)).focus(); }
        if (accion === 'quitar') { leer(); lineas.splice(Number(b.dataset.i), 1); pintar(); $(root, '#prod-' + Math.max(0, Number(b.dataset.i) - 1)).focus(); }
        if (accion === 'consultar') {
          leer();
          const estado = $(root, '#consulta-estado');
          const ok = tipo === 'factura' ? Sunat.rucValido(doc.numero) : Sunat.dniValido(doc.numero);
          if (!ok) { estado.innerHTML = `${icono('alerta')} ${tipo === 'factura' ? 'Escribe un RUC de 11 dígitos válido.' : 'Escribe un DNI de 8 dígitos.'}`; return; }
          estado.textContent = 'Consultando SUNAT (simulado)…';
          try {
            const r = await Sunat.consultar(doc.numero);
            $(root, '#doc-nombre').value = r.nombre;
            estado.innerHTML = `${icono('check')} Encontrado: ${esc(r.nombre)}${r.estado ? ` · ${esc(r.estado)} / ${esc(r.condicion)}` : ''}`;
          } catch (x) {
            estado.innerHTML = `${icono('alerta')} ${x.message === 'sin-red'
              ? 'Sin conexión: no se pudo consultar. Escribe el nombre a mano; el comprobante quedará pendiente de envío.'
              : 'No se encontró este número en los datos de ejemplo. Revisa los dígitos o escribe el nombre a mano.'}`;
          }
        }
      };
      root.onsubmit = async e => {
        e.preventDefault();
        leer();
        errores = validar();
        if (errores.length) { pintar(); enfocarResumen(root); return; }
        const items = lineas.filter(l => l.productoId).map(l => { const p = Datos.producto(l.productoId);
          return { productoId: p.id, nombre: p.nombre, cant: num(l.cant), precio: p.precio, costoUnit: p.costoUnit }; });
        let venta = original;
        if (original) { while (!Datos.reemplazarVenta(original.id, items)) { if (await errorGuardar() === 'volver') return; } }
        else {
          const importe = total();
          const comprobante = tipo === 'ninguno' ? null : Sunat.emitir({ tipo, total: importe, fecha: new Date().toISOString(), cliente: { numero: doc.numero, nombre: doc.nombre } });
          venta = Datos.registrarVenta(items, comprobante);
          while (!venta) { if (await errorGuardar() === 'volver') return; venta = Datos.registrarVenta(items, comprobante); }
        }
        ctx.setSucio(false);
        const c = venta.comprobante;
        const botones = [{ texto: 'Aceptar', valor: 'ok' }];
        if (c) botones.push({ texto: 'Ver comprobante', clase: 'boton--sec', valor: 'ver' });
        if (!original) botones.push({ texto: 'Agregar nueva venta', clase: 'boton--sec', valor: 'otra' });
        const r = await modal({ titulo: original ? '¡Cambios guardados!' : '¡Venta registrada!', icono: 'check', tono: 'ok', escape: 0,
          texto: `Total ${dinero(venta.total)}. ${c ? `Comprobante ${esc(c.codigo)}: ${esc(Sunat.etiquetaEstado(c.estado))}.` : 'Ya cuenta en tus ganancias.'}`, botones });
        ctx.ir(r === 'ver' ? '#/comprobantes/' + venta.id : r === 'otra' ? '#/ventas/nueva' : '#/ventas');
      };
    } };
  }

  /* ---------- Ganancias ---------- */
  const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  const DIAS = ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb'];

  function grafico(grupos, resumenTexto) {
    const W = 340, H = 220, izq = 44, der = 8, arriba = 24, abajo = 30;
    const maximo = Math.max(...grupos.flatMap(g => [g.ganancia, g.inversion]), 1);
    const paso = Math.pow(10, Math.floor(Math.log10(maximo)));
    const tope = Math.ceil(maximo / paso) * paso;
    const y = v => arriba + (H - arriba - abajo) * (1 - v / tope);
    const ancho = (W - izq - der) / grupos.length;
    const barra = Math.min(26, ancho / 2.5);
    const compacto = grupos.length > 3;
    const fmt = v => compacto ? String(Math.round(v)) : dinero(v);
    const guias = [0, tope / 2, tope].map(v => `<line x1="${izq}" x2="${W - der}" y1="${y(v)}" y2="${y(v)}" stroke="#E3D3CA"/><text x="${izq - 6}" y="${y(v) + 4}" text-anchor="end" font-size="12">${Math.round(v)}</text>`).join('');
    const barras = grupos.map((g, i) => {
      const cx = izq + ancho * i + ancho / 2;
      const una = (v, x, color) => `<rect x="${x}" y="${y(v)}" width="${barra}" height="${Math.max(0, y(0) - y(v))}" fill="${color}" rx="3"/>`;
      const val = (v, x) => `<text x="${x + barra / 2}" y="${y(v) - 4}" text-anchor="middle" font-size="12">${fmt(v)}</text>`;
      return `${una(g.ganancia, cx - barra - 1, 'var(--barra-ganancia)')}${una(g.inversion, cx + 1, 'var(--barra-inversion)')}
        ${val(g.ganancia, cx - barra - 1)}${compacto ? '' : val(g.inversion, cx + 1)}
        <text x="${cx}" y="${H - 8}" text-anchor="middle" font-size="12">${esc(g.etiqueta)}</text>`;
    }).join('');
    return `<svg class="grafico" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="g-t g-d"><title id="g-t">Ganancia e inversión</title><desc id="g-d">${esc(resumenTexto)}</desc>${guias}${barras}</svg>`;
  }

  function ganancias() {
    return { titulo: 'Ganancias', nav: 'ganancias', montar(root) {
      const hoy = new Date();
      let modo = 'semana', desde = isoLocal(new Date(hoy.getFullYear(), hoy.getMonth(), 1)), hasta = isoLocal(hoy);

      const periodo = () => {
        if (modo === 'semana') {
          const grupos = [];
          for (let i = 6; i >= 0; i--) { const d = new Date(); d.setDate(hoy.getDate() - i); grupos.push({ etiqueta: DIAS[d.getDay()], desde: d, hasta: d }); }
          return { grupos, nombre: 'los últimos 7 días' };
        }
        if (modo === 'mes') {
          const y = hoy.getFullYear(), m = hoy.getMonth(), ultimo = new Date(y, m + 1, 0).getDate();
          const tramos = [[1, 7], [8, 14], [15, 21], [22, 28]]; if (ultimo > 28) tramos.push([29, ultimo]);
          return { grupos: tramos.map(([a, b]) => ({ etiqueta: `${a}-${b}`, desde: new Date(y, m, a), hasta: new Date(y, m, b) })), nombre: `${MESES[m]} de ${y}` };
        }
        const a = new Date(desde + 'T00:00:00'), b = new Date(hasta + 'T00:00:00');
        return { grupos: [{ etiqueta: `${fechaCorta(a)} al ${fechaCorta(b)}`.replace(/\/\d{4}/g, ''), desde: a, hasta: b }], nombre: `del ${fechaCorta(a)} al ${fechaCorta(b)}` };
      };

      const pintar = foco => {
        const rangoMal = modo === 'fechas' && desde > hasta;
        const { grupos, nombre } = rangoMal ? { grupos: [], nombre: '' } : periodo();
        const datos = grupos.map(g => ({ etiqueta: g.etiqueta, ...Datos.resumen(g.desde, g.hasta) }));
        const t = datos.reduce((s, d) => ({ ventas: s.ventas + d.ventas, inversion: s.inversion + d.inversion, ganancia: s.ganancia + d.ganancia }), { ventas: 0, inversion: 0, ganancia: 0 });
        const texto = `Ganancia ${dinero(t.ganancia)} e inversión ${dinero(t.inversion)} en ${nombre}.`;
        root.innerHTML = `
          ${encabezado('Ganancias', { ic: 'ganancias' })}
          <fieldset class="segmentado" aria-label="Periodo">
            ${[['semana', 'Semana'], ['mes', 'Mes'], ['fechas', 'Fechas']].map(([v, n]) => `<div><input type="radio" name="modo" id="modo-${v}" value="${v}"${modo === v ? ' checked' : ''}><label for="modo-${v}">${n}</label></div>`).join('')}
          </fieldset>
          ${modo === 'fechas' ? `<div class="filtros">
            ${campo({ id: 'desde', etiqueta: 'Desde', tipo: 'date', valor: desde, atributos: 'autocomplete="off"' })}
            ${campo({ id: 'hasta', etiqueta: 'Hasta', tipo: 'date', valor: hasta, error: rangoMal ? 'La fecha final debe ser igual o posterior a la inicial.' : '', atributos: 'autocomplete="off"' })}
          </div>` : ''}
          ${rangoMal ? '' : `
          <section class="tarjeta" aria-label="Resultado de ${esc(nombre)}">
            <p class="ayuda">Ganancia de ${esc(nombre)}</p>
            <p class="balance">${dinero(t.ganancia)}</p>
            ${grafico(datos, texto)}
            <ul class="leyenda"><li><i style="background:var(--barra-ganancia)"></i>Ganancia</li><li><i style="background:var(--barra-inversion)"></i>Inversión</li></ul>
            <dl class="totales">
              <div><dt>Ventas</dt><dd>${dinero(t.ventas)}</dd></div>
              <div><dt>Inversión</dt><dd>${dinero(t.inversion)}</dd></div>
              <div><dt>Ganancia</dt><dd>${dinero(t.ganancia)}</dd></div>
            </dl>
            <details><summary>Ver los datos en tabla</summary>
              <table><caption>Datos del gráfico</caption>
                <thead><tr><th scope="col">Periodo</th><th scope="col">Ventas</th><th scope="col">Inversión</th><th scope="col">Ganancia</th></tr></thead>
                <tbody>${datos.map(d => `<tr><th scope="row">${esc(d.etiqueta)}</th><td>${dinero(d.ventas)}</td><td>${dinero(d.inversion)}</td><td>${dinero(d.ganancia)}</td></tr>`).join('')}</tbody>
              </table>
            </details>
          </section>`}`;
        if (foco) { const el = $(root, foco); if (el) el.focus(); }
      };

      pintar();
      root.onchange = e => {
        if (e.target.name === 'modo') { modo = e.target.value; pintar('#modo-' + modo); }
        else if (e.target.id === 'desde') { desde = e.target.value || desde; pintar('#desde'); }
        else if (e.target.id === 'hasta') { hasta = e.target.value || hasta; pintar('#hasta'); }
      };
    } };
  }

  /* ---------- Perfil, cuenta y membresía ---------- */
  function perfil(ctx) {
    return { titulo: 'Perfil', nav: 'perfil', montar(root) {
      const s = Datos.sesion;
      root.innerHTML = `
        ${encabezado('Perfil', { ic: 'perfil' })}
        ${s ? `<div class="tarjeta pila" style="margin-bottom:16px"><p style="margin:0"><strong>${esc(s.nombre)}</strong><br>${esc(s.email)}</p>
          <button type="button" class="boton boton--sec" data-accion="salir">${icono('entrar')}<span>Cerrar sesión</span></button></div>` : ''}
        <ul class="menu">
          ${s ? '' : `<li><a href="#/login">${icono('entrar')}<span class="crece">Iniciar sesión</span>${icono('siguiente')}</a></li>
          <li><a href="#/registro">${icono('registro')}<span class="crece">Registrarse</span>${icono('siguiente')}</a></li>`}
          <li><a href="#/premium">${icono('estrella')}<span class="crece">Premium: respaldo en la nube</span>${icono('siguiente')}</a></li>
          <li><a href="#/negocio">${icono('negocio')}<span class="crece">Datos del negocio</span>${icono('siguiente')}</a></li>
          <li><a href="#/comprobantes">${icono('documento')}<span class="crece">Comprobantes SUNAT</span>${icono('siguiente')}</a></li>
        </ul>
        <h2>Para la demostración</h2>
        <ul class="menu">
          <li><button type="button" role="switch" aria-checked="${Red.simulada}" data-accion="red">${icono('sinred')}<span class="crece">Simular sin conexión</span><span class="interruptor">${Red.simulada ? 'Activado' : 'Desactivado'}</span></button></li>
          <li><button type="button" data-accion="reiniciar">${icono('papelera')}<span class="crece">Restablecer datos de ejemplo</span></button></li>
        </ul>`;
      root.onclick = async e => {
        const b = e.target.closest('[data-accion]');
        if (!b) return;
        if (b.dataset.accion === 'salir') { Datos.sesion = null; aviso('Cerraste la sesión.'); ctx.repintar(); }
        if (b.dataset.accion === 'red') { Red.simulada = !Red.simulada; ctx.actualizarRed(); ctx.repintar(); $(root, '[data-accion="red"]').focus(); }
        if (b.dataset.accion === 'reiniciar') {
          const ok = await confirmar({ titulo: '¿Restablecer los datos?', texto: 'Se borrarán tus productos y ventas y volverán los datos de ejemplo.', si: 'Restablecer' });
          if (ok && Datos.reiniciar()) { aviso('Datos de ejemplo restablecidos.'); ctx.repintar(); }
        }
      };
    } };
  }

  function formularioCuenta(ctx, registro) {
    return { titulo: registro ? 'Crear cuenta' : 'Iniciar sesión', nav: 'perfil', montar(root) {
      let v = { nombre: '', email: '', clave: '', clave2: '' };
      let errores = [], verClave = false;
      const err = id => (errores.find(e => e.id === id) || {}).mensaje || '';
      const claveCampo = (id, etiqueta, auto, ayuda) => `
        <div class="campo ${err(id) ? 'campo--error' : ''}">
          <label for="${id}">${etiqueta} <span class="req">(obligatorio)</span></label>
          ${ayuda ? `<p class="ayuda" id="${id}-ayuda">${ayuda}</p>` : ''}
          <div class="consulta">
            <input id="${id}" name="${id}" type="${verClave ? 'text' : 'password'}" value="${esc(v[id])}" required autocomplete="${auto}"${err(id) ? ` aria-invalid="true" aria-describedby="${id}-error"` : ayuda ? ` aria-describedby="${id}-ayuda"` : ''}>
            ${id === 'clave' ? `<button type="button" class="boton boton--icono boton--sec" data-accion="ver" aria-pressed="${verClave}" aria-label="${verClave ? 'Ocultar' : 'Mostrar'} contraseña">${icono('ojo')}</button>` : ''}
          </div>
          ${err(id) ? `<p class="error" id="${id}-error">${icono('alerta')}<span>${esc(err(id))}</span></p>` : ''}
        </div>`;
      const pintar = () => {
        root.innerHTML = `
          ${encabezado(registro ? 'Crear cuenta' : 'Iniciar sesión', { atras: '#/perfil' })}
          ${resumenErrores(errores)}
          <p class="nota">Cuenta de demostración: los datos no salen de este dispositivo.</p>
          <form id="f" novalidate>
            ${registro ? campo({ id: 'nombre', etiqueta: 'Nombre completo', valor: v.nombre, requerido: true, error: err('nombre'), atributos: 'autocomplete="name" placeholder="Ej. Juan Pérez"' }) : ''}
            ${campo({ id: 'email', etiqueta: 'Correo electrónico', tipo: 'email', valor: v.email, requerido: true, error: err('email'), atributos: 'autocomplete="email" placeholder="usuario@correo.com"' })}
            ${claveCampo('clave', 'Contraseña', registro ? 'new-password' : 'current-password', registro ? 'Mínimo 8 caracteres.' : '')}
            ${registro ? claveCampo('clave2', 'Confirmar contraseña', 'new-password', '') : ''}
            <div class="pila">
              <button type="submit" class="boton boton--bloque">${icono(registro ? 'registro' : 'entrar')}<span>${registro ? 'Registrarse' : 'Iniciar sesión'}</span></button>
              <a class="boton boton--sec boton--bloque" href="#/inicio">Continuar sin sesión</a>
              <p class="enlace-pie">${registro ? '¿Ya tienes una cuenta? <a href="#/login">Inicia sesión</a>' : '¿No tienes una cuenta? <a href="#/registro">Regístrate</a>'}</p>
            </div>
          </form>`;
      };
      const leer = () => {
        const g = id => { const el = $(root, '#' + id); return el ? el.value : ''; };
        v = { nombre: g('nombre').trim(), email: g('email').trim(), clave: g('clave'), clave2: g('clave2') };
      };
      pintar();
      root.oninput = () => ctx.setSucio(true);
      root.onclick = e => {
        irACampo(e, root);
        if (e.target.closest('[data-accion="ver"]')) { leer(); verClave = !verClave; pintar(); $(root, '[data-accion="ver"]').focus(); }
      };
      root.onsubmit = e => {
        e.preventDefault();
        leer();
        errores = [];
        if (registro && !v.nombre) errores.push({ id: 'nombre', mensaje: 'Escribe tu nombre completo.' });
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.email)) errores.push({ id: 'email', mensaje: 'Escribe un correo válido. Ejemplo: usuario@correo.com.' });
        if (v.clave.length < 8) errores.push({ id: 'clave', mensaje: 'La contraseña debe tener al menos 8 caracteres.' });
        if (registro && v.clave !== v.clave2) errores.push({ id: 'clave2', mensaje: 'Las contraseñas no coinciden. Escríbelas de nuevo.' });
        if (errores.length) { pintar(); enfocarResumen(root); return; }
        Datos.sesion = { nombre: registro ? v.nombre : v.email.split('@')[0], email: v.email };
        ctx.setSucio(false);
        aviso(registro ? 'Cuenta creada.' : 'Sesión iniciada.');
        ctx.ir('#/perfil');
      };
    } };
  }

  function premium(ctx) {
    return { titulo: 'Premium', nav: 'perfil', montar(root) {
      const s = Datos.sesion;
      const ultimo = Datos.ultimoRespaldo;
      root.innerHTML = `
        ${encabezado('Premium', { atras: '#/perfil' })}
        <div class="tarjeta pila">
          <h2 style="margin:0">Respaldo de tus datos en la nube</h2>
          <p style="margin:0">Sin internet, MercaTab funciona completo y guarda todo en tu celular. Con la membresía mensual, además, puedes respaldar tus productos y ventas en la nube y recuperarlos si cambias o pierdes el celular.</p>
          <p class="ayuda" style="margin:0">Membresía mensual simulada: no hay cobro y el precio está por definir.</p>
          ${!s ? `<p class="nota" style="margin:0">Para activar el respaldo primero <a href="#/login">inicia sesión</a> o <a href="#/registro">crea una cuenta</a>.</p>`
            : !Datos.premium ? `<button type="button" class="boton" data-accion="activar">${icono('estrella')}<span>Activar membresía</span></button>`
            : `<p style="margin:0"><span class="etiqueta etiqueta--ok">${icono('check')}Membresía activa</span></p>
               <p style="margin:0">Último respaldo: ${ultimo ? `${fechaCorta(ultimo)} a las ${hora(ultimo)}` : 'todavía no hiciste ninguno'}.</p>
               ${Red.enLinea() ? '' : `<p class="nota" style="margin:0">Sin conexión: el respaldo se hace cuando vuelva internet.</p>`}
               <button type="button" class="boton"${Red.enLinea() ? '' : ' disabled'} data-accion="respaldar">${icono('nube')}<span>Respaldar ahora</span></button>
               <button type="button" class="boton boton--sec"${Red.enLinea() && Datos.hayRespaldo() ? '' : ' disabled'} data-accion="restaurar">Restaurar el último respaldo</button>`}
        </div>`;
      root.onclick = async e => {
        const b = e.target.closest('[data-accion]');
        if (!b) return;
        const a = b.dataset.accion;
        if (a === 'activar') { Datos.premium = true; aviso('Membresía activada (simulada).'); ctx.repintar(); }
        if (a === 'respaldar') { aviso(Datos.respaldar() ? 'Respaldo guardado.' : 'No se pudo respaldar. Inténtalo de nuevo.'); ctx.repintar(); }
        if (a === 'restaurar') {
          const ok = await confirmar({ titulo: '¿Restaurar el respaldo?', texto: 'Tus datos actuales se reemplazarán por los del último respaldo.', si: 'Restaurar' });
          if (ok) { aviso(Datos.restaurar() ? 'Respaldo restaurado.' : 'No se pudo restaurar el respaldo.'); ctx.repintar(); }
        }
      };
    } };
  }

  function negocio(ctx) {
    return { titulo: 'Datos del negocio', nav: 'perfil', montar(root) {
      let v = { ruc: Datos.negocio.ruc, razon: Datos.negocio.razon };
      let errores = [];
      const err = id => (errores.find(e => e.id === id) || {}).mensaje || '';
      const pintar = () => {
        root.innerHTML = `
          ${encabezado('Datos del negocio', { atras: '#/perfil' })}
          ${resumenErrores(errores)}
          <p class="nota">Estos datos salen como emisor en tus boletas y facturas.</p>
          <form id="f" novalidate>
            <div class="consulta">
              ${campo({ id: 'ruc', etiqueta: 'RUC del negocio', valor: v.ruc, requerido: true, error: err('ruc'), ayuda: `Datos de ejemplo: ${Sunat.ejemplos.rucs[1]}.`, atributos: 'inputmode="numeric" maxlength="11" autocomplete="off"' })}
              <button type="button" class="boton boton--sec" data-accion="consultar">Consultar SUNAT</button>
            </div>
            <p class="consulta__estado" id="consulta-estado" role="status"></p>
            ${campo({ id: 'razon', etiqueta: 'Razón social o nombre', valor: v.razon, requerido: true, error: err('razon'), atributos: 'autocomplete="organization"' })}
            <div class="fila-botones">
              <button type="submit" class="boton">${icono('guardar')}<span>Guardar</span></button>
              <a class="boton boton--peligro" href="#/perfil">${icono('cerrar')}<span>Cancelar</span></a>
            </div>
          </form>`;
      };
      const leer = () => { v = { ruc: $(root, '#ruc').value.trim(), razon: $(root, '#razon').value.trim() }; };
      pintar();
      root.oninput = () => ctx.setSucio(true);
      root.onclick = async e => {
        irACampo(e, root);
        if (!e.target.closest('[data-accion="consultar"]')) return;
        leer();
        const estado = $(root, '#consulta-estado');
        if (!Sunat.rucValido(v.ruc)) { estado.innerHTML = `${icono('alerta')} Escribe un RUC de 11 dígitos válido.`; return; }
        estado.textContent = 'Consultando SUNAT (simulado)…';
        try { const r = await Sunat.consultar(v.ruc); $(root, '#razon').value = r.nombre; estado.innerHTML = `${icono('check')} Encontrado: ${esc(r.nombre)} · ${esc(r.estado)} / ${esc(r.condicion)}`; ctx.setSucio(true); }
        catch (x) { estado.innerHTML = `${icono('alerta')} ${x.message === 'sin-red' ? 'Sin conexión: no se pudo consultar. Escribe la razón social a mano.' : 'No se encontró este RUC en los datos de ejemplo.'}`; }
      };
      root.onsubmit = e => {
        e.preventDefault();
        leer();
        errores = [];
        if (!Sunat.rucValido(v.ruc)) errores.push({ id: 'ruc', mensaje: 'El RUC debe tener 11 dígitos y ser válido (empieza con 10 o 20).' });
        if (!v.razon) errores.push({ id: 'razon', mensaje: 'Escribe la razón social o el nombre del negocio.' });
        if (errores.length) { pintar(); enfocarResumen(root); return; }
        Datos.negocio = v;
        ctx.setSucio(false);
        aviso('Datos del negocio guardados.');
        ctx.ir('#/perfil');
      };
    } };
  }

  /* ---------- Comprobantes ---------- */
  function comprobantes(ctx) {
    return { titulo: 'Comprobantes', nav: 'ventas', montar(root) {
      const lista = Datos.comprobantes();
      const pend = lista.filter(v => v.comprobante.estado === 'pendiente').length;
      root.innerHTML = `
        ${encabezado('Comprobantes', { atras: '#/ventas' })}
        <p class="nota">Conexión con SUNAT simulada: sirve para probar el flujo, no tiene validez tributaria.</p>
        ${pend ? `<p><button type="button" class="boton boton--chico"${Red.enLinea() ? '' : ' disabled'} data-accion="enviar">${icono('nube')}<span>Enviar ${plural(pend, 'pendiente', 'pendientes')} a SUNAT</span></button></p>
          ${Red.enLinea() ? '' : '<p class="ayuda">Sin conexión: se enviarán solos cuando vuelva internet.</p>'}` : ''}
        ${lista.length ? `<ul class="lista">${lista.map(v => `
          <li><a class="fila" style="text-decoration:none;color:inherit" href="#/comprobantes/${v.id}">
            <div class="fila__texto">
              <p class="fila__titulo">${esc(v.comprobante.codigo)}</p>
              <p class="fila__detalle">${v.comprobante.tipo === 'factura' ? 'Factura' : 'Boleta'} · ${esc(v.comprobante.cliente.nombre || 'Cliente sin identificar')}</p>
              <p class="fila__precio">${dinero(v.total)}</p>
              <span class="etiqueta ${v.comprobante.estado === 'aceptado' ? 'etiqueta--ok' : 'etiqueta--pend'}">${icono(v.comprobante.estado === 'aceptado' ? 'check' : 'sinred')}${esc(Sunat.etiquetaEstado(v.comprobante.estado))}</span>
            </div>${icono('siguiente')}</a></li>`).join('')}</ul>`
          : '<div class="vacio"><p>Aún no emitiste comprobantes. Al registrar una venta puedes elegir boleta o factura.</p><a class="boton" href="#/ventas/nueva">Registrar una venta</a></div>'}`;
      root.onclick = e => {
        if (!e.target.closest('[data-accion="enviar"]')) return;
        const n = Sunat.enviarPendientes();
        aviso(n ? `Se enviaron ${plural(n, 'comprobante', 'comprobantes')} a SUNAT (simulado).` : 'No hay comprobantes pendientes.');
        ctx.repintar();
      };
    } };
  }

  function comprobante(ctx, params) {
    const venta = Datos.venta(Number(params.id));
    return { titulo: venta && venta.comprobante ? venta.comprobante.codigo : 'Comprobante', nav: 'ventas', montar(root) {
      if (!venta || !venta.comprobante) { ctx.ir('#/comprobantes'); return; }
      const c = venta.comprobante, neg = Datos.negocio;
      root.innerHTML = `
        ${encabezado(c.tipo === 'factura' ? 'Factura electrónica' : 'Boleta electrónica', { atras: '#/comprobantes' })}
        <article class="ticket" aria-label="Comprobante ${esc(c.codigo)}">
          <h2>${esc(neg.razon || 'Negocio sin datos')}</h2>
          <p>RUC ${esc(neg.ruc || 'sin registrar')}${neg.ruc ? '' : ' · completa los datos en Perfil'}</p>
          <p><strong>${esc(c.codigo)}</strong></p>
          <p>Emitido el ${fechaCorta(c.fecha)} a las ${hora(c.fecha)}</p>
          <p>Cliente: ${esc(c.cliente.nombre || 'Sin identificar')}${c.cliente.numero ? ` (${c.cliente.numero.length === 11 ? 'RUC' : 'DNI'} ${esc(c.cliente.numero)})` : ''}</p>
          <table>
            <caption class="solo-lector">Detalle del comprobante</caption>
            <thead><tr><th scope="col">Cant.</th><th scope="col">Descripción</th><th scope="col">P. unit.</th><th scope="col">Importe</th></tr></thead>
            <tbody>${venta.items.map(i => `<tr><td>${i.cant}</td><td style="text-align:left">${esc(i.nombre)}</td><td>${dinero(i.precio)}</td><td>${dinero(i.cant * i.precio)}</td></tr>`).join('')}</tbody>
            <tfoot>
              <tr><th scope="row" colspan="3">Operación gravada</th><td>${dinero(c.base)}</td></tr>
              <tr><th scope="row" colspan="3">IGV (18 %)</th><td>${dinero(c.igv)}</td></tr>
              <tr class="fin"><th scope="row" colspan="3">Total</th><td>${dinero(c.total)}</td></tr>
            </tfoot>
          </table>
          <p><span class="etiqueta ${c.estado === 'aceptado' ? 'etiqueta--ok' : 'etiqueta--pend'}">${icono(c.estado === 'aceptado' ? 'check' : 'sinred')}${esc(Sunat.etiquetaEstado(c.estado))}</span></p>
          <p class="marca-agua">Representación simulada para el curso. No tiene validez tributaria.</p>
        </article>
        <div class="fila-botones no-imprimir">
          <button type="button" class="boton" data-accion="imprimir">${icono('documento')}<span>Imprimir</span></button>
          ${c.estado === 'pendiente' ? `<button type="button" class="boton boton--sec"${Red.enLinea() ? '' : ' disabled'} data-accion="reenviar">Enviar a SUNAT</button>` : ''}
        </div>`;
      root.onclick = e => {
        const b = e.target.closest('[data-accion]');
        if (!b) return;
        if (b.dataset.accion === 'imprimir') window.print();
        if (b.dataset.accion === 'reenviar') { Sunat.enviarPendientes(); aviso('Comprobante enviado a SUNAT (simulado).'); ctx.repintar(); }
      };
    } };
  }

  return { inicio, productos, productoForm, ventas, ventaForm, ganancias, perfil, login: ctx => formularioCuenta(ctx, false), registro: ctx => formularioCuenta(ctx, true), premium, negocio, comprobantes, comprobante };
})();
