// Piezas de interfaz que usan todas las pantallas: formato, diálogos, avisos y campos de formulario.
const UI = (() => {
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const formatoMoneda = new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' });
  const dinero = n => formatoMoneda.format(n).replace(/ /g, ' ');

  const dosDigitos = n => String(n).padStart(2, '0');
  const isoLocal = f => `${f.getFullYear()}-${dosDigitos(f.getMonth() + 1)}-${dosDigitos(f.getDate())}`;
  const fechaCorta = iso => { const f = new Date(iso); return `${dosDigitos(f.getDate())}/${dosDigitos(f.getMonth() + 1)}/${f.getFullYear()}`; };
  const hora = iso => { const f = new Date(iso); return `${dosDigitos(f.getHours())}:${dosDigitos(f.getMinutes())}`; };
  const fechaLarga = f => f.toLocaleDateString('es-PE', { weekday: 'long', day: 'numeric', month: 'long' });

  // Diálogo modal con <dialog>: el navegador atrapa el foco, bloquea el fondo y cierra con Esc.
  function modal({ titulo, icono: ic = '', tono = '', texto = '', botones, foco = 0, escape = botones.length - 1 }) {
    return new Promise(resolve => {
      const d = document.getElementById('modal');
      d.innerHTML = `
        <div class="modal__cuerpo">
          ${ic ? `<span class="modal__ico modal__ico--${tono}">${icono(ic)}</span>` : ''}
          <h2 id="modal-titulo">${esc(titulo)}</h2>
          ${texto ? `<p>${texto}</p>` : ''}
          <div class="modal__botones">
            ${botones.map((b, i) => `<button type="button" class="boton ${b.clase || ''}" data-i="${i}">${esc(b.texto)}</button>`).join('')}
          </div>
        </div>`;
      const cerrar = valor => { d.onclick = null; d.oncancel = null; d.close(); d.removeAttribute('aria-labelledby'); resolve(valor); };
      d.onclick = e => { const b = e.target.closest('[data-i]'); if (b) cerrar(botones[+b.dataset.i].valor); };
      d.oncancel = e => { e.preventDefault(); cerrar(botones[escape].valor); };
      d.setAttribute('aria-labelledby', 'modal-titulo'); // solo mientras hay un título al que apuntar
      d.showModal();
      d.querySelector(`[data-i="${foco}"]`).focus();
    });
  }

  const confirmar = ({ titulo, texto, ic = 'alerta', tono = 'peligro', si, no = 'Cancelar' }) =>
    modal({ titulo, texto, icono: ic, tono, foco: 1, botones: [{ texto: si, clase: 'boton--peligro', valor: true }, { texto: no, clase: 'boton--sec', valor: false }] });

  const errorGuardar = () => modal({
    titulo: '¡Hubo un problema!', icono: 'alerta', tono: 'aviso',
    texto: 'No se pudo guardar. Revisa los datos e inténtalo de nuevo.',
    botones: [{ texto: 'Intentar de nuevo', valor: 'reintentar' }, { texto: 'Volver', clase: 'boton--sec', valor: 'volver' }]
  });

  function aviso(mensaje) {
    const caja = document.getElementById('avisos');
    const p = document.createElement('p');
    p.className = 'aviso';
    p.textContent = mensaje;
    caja.append(p);
    setTimeout(() => p.remove(), 5000);
  }

  // Campo de formulario con etiqueta visible, ayuda y error con texto (no solo color).
  function campo({ id, etiqueta, tipo = 'text', valor = '', ayuda = '', error = '', requerido = false, atributos = '' }) {
    const desc = [ayuda && `${id}-ayuda`, error && `${id}-error`].filter(Boolean).join(' ');
    return `
      <div class="campo ${error ? 'campo--error' : ''}">
        <label for="${id}">${esc(etiqueta)}${requerido ? ' <span class="req">(obligatorio)</span>' : ''}</label>
        ${ayuda ? `<p class="ayuda" id="${id}-ayuda">${esc(ayuda)}</p>` : ''}
        <input id="${id}" name="${id}" type="${tipo}" value="${esc(valor)}"${requerido ? ' required' : ''}${error ? ' aria-invalid="true"' : ''}${desc ? ` aria-describedby="${desc}"` : ''} ${atributos}>
        ${error ? `<p class="error" id="${id}-error">${icono('alerta')}<span>${esc(error)}</span></p>` : ''}
      </div>`;
  }

  const resumenErrores = errores => errores.length ? `
    <div class="resumen-error" id="resumen-errores" role="alert" tabindex="-1">
      <h2>${errores.length === 1 ? 'Hay 1 dato por corregir' : `Hay ${errores.length} datos por corregir`}</h2>
      <ul>${errores.map(e => `<li><button type="button" class="enlace" data-ir="${esc(e.id)}">${esc(e.mensaje)}</button></li>`).join('')}</ul>
    </div>` : '';

  const encabezado = (titulo, { ic = '', atras = '', accion = null } = {}) => `
    <div class="encab">
      ${atras ? `<a class="boton boton--icono boton--sec" href="${atras}" aria-label="Volver">${icono('volver')}</a>` : ic ? icono(ic, 'encab__ico') : ''}
      <h1 tabindex="-1">${esc(titulo)}</h1>
      ${accion ? `<a class="boton boton--chico" href="${accion.href}">${icono(accion.ic || 'mas')}<span>${esc(accion.texto)}</span></a>` : ''}
    </div>`;

  return { esc, dinero, isoLocal, fechaCorta, hora, fechaLarga, modal, confirmar, errorGuardar, aviso, campo, resumenErrores, encabezado };
})();
