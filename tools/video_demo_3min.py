"""Video demo de ~3 min: flujo completo solo con teclado, con subtítulos en pantalla (sin voz)."""
import os, shutil, subprocess
from playwright.sync_api import sync_playwright

URL = "file:///D:/PruebasTareas/ihm_pa3/app/index.html"
SAL = r"D:\PruebasTareas\ihm_pa3\evidencia\video"
TMP = os.path.join(SAL, "tmp"); os.makedirs(TMP, exist_ok=True)

# Subtítulo y tecla pulsada: son popovers para quedar por encima de los diálogos modales.
INYECTAR = """
(() => {
  const css = document.createElement('style');
  css.textContent = `
    #__sub, #__tecla { position: fixed; margin: 0; border: 0; inset: auto; color: #fff; font-family: Arial, sans-serif; }
    #__sub { left: 10px; right: 10px; bottom: 82px; background: rgba(43,33,24,.94); padding: 10px 14px; border-radius: 10px; font-size: 16px; font-weight: 700; line-height: 1.35; text-align: center; }
    #__tecla { right: 8px; top: 8px; background: #B3261E; padding: 6px 14px; border-radius: 8px; font-size: 20px; font-weight: 700; }`;
  document.head.append(css);
  for (const id of ['__sub', '__tecla']) { const d = document.createElement('div'); d.id = id; d.setAttribute('popover', 'manual'); d.setAttribute('aria-hidden', 'true'); document.body.append(d); }
  let t;
  addEventListener('keydown', e => {
    const n = { ' ': 'Espacio', ArrowDown: '↓', ArrowUp: '↑', ArrowLeft: '←', ArrowRight: '→' }[e.key] || (e.key.length === 1 ? '' : e.key);
    if (!n) return;
    const k = document.getElementById('__tecla'); k.textContent = (e.shiftKey ? 'Shift + ' : '') + n;
    try { k.hidePopover(); } catch (x) {} k.showPopover(); clearTimeout(t); t = setTimeout(() => { try { k.hidePopover(); } catch (x) {} }, 900);
  }, true);
})();
"""

with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 390, "height": 844}, record_video_dir=TMP, record_video_size={"width": 390, "height": 844}, locale="es-PE")
    pg = ctx.new_page()
    pg.goto(URL); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_selector("main h1")
    pg.evaluate("Datos.negocio = { ruc: Sunat.ejemplos.rucs[1], razon: 'ABARROTES LA ESQUINA E.I.R.L.' }")
    pg.reload(); pg.wait_for_selector("main h1"); pg.evaluate(INYECTAR)

    def leyenda(t, espera=3500):
        pg.evaluate("""(t) => { const s = document.getElementById('__sub'); s.textContent = t; try { s.hidePopover(); } catch (x) {} s.showPopover(); }""", t)
        pg.wait_for_timeout(espera)
    def pausa(ms=700): pg.wait_for_timeout(ms)
    def tecla(k, ms=700): pg.keyboard.press(k); pausa(ms)
    def tab_hasta(sel, maximo=40, ritmo=420):
        for _ in range(maximo):
            if pg.evaluate("(s) => document.activeElement.matches(s)", sel): return
            pg.keyboard.press("Tab"); pausa(ritmo)
        raise RuntimeError("no se llegó a " + sel)
    def escribir(t, d=150): pg.keyboard.type(t, delay=d); pausa(600)

    leyenda("MercaTab: registrar ventas y ver ganancias, sin internet y sin mouse", 5000)
    leyenda("Todo este recorrido se hace solo con el teclado: Tab, Shift+Tab, Enter, flechas y Esc", 5000)

    # 1. Skip link y foco visible
    leyenda("Primer Tab: aparece el enlace «Ir al contenido principal» (skip link)", 1200)
    tecla("Tab", 3500)
    leyenda("Enter: el foco salta directo al contenido", 1200)
    tecla("Enter", 3000)
    leyenda("El foco siempre es visible: contorno azul de 3 px", 1200)
    for _ in range(3): tecla("Tab", 1200)

    # 2. Errores de formulario
    tab_hasta("main a[href='#/ventas/nueva']")
    leyenda("Registrar venta: la acción principal de Inicio", 2200)
    tecla("Enter", 1500)
    tab_hasta("button[type=submit]", ritmo=250)
    leyenda("Guardar sin datos: los errores dicen qué corregir, con ícono y texto, no solo color", 1200)
    tecla("Enter", 5500)

    # 3. Venta con factura
    tab_hasta("#prod-0", ritmo=300)
    leyenda("Elegir el producto con las flechas", 1000)
    tecla("ArrowDown", 1800)
    tecla("Tab", 600); escribir("2", 250)
    leyenda("Cantidad 2: el total se calcula al escribir", 3500)
    tab_hasta("input[name=tipo]", ritmo=300)
    leyenda("Comprobante electrónico: se cambia de opción con las flechas", 1500)
    tecla("ArrowDown", 1000); tecla("ArrowDown", 2500)
    tab_hasta("#doc-numero", ritmo=300)
    leyenda("Factura: el RUC se valida con el dígito verificador de SUNAT", 1500)
    escribir("12345678901", 120)
    tecla("Tab", 600); tecla("Enter", 3500)
    leyenda("RUC inválido: el mensaje explica qué hacer", 3000)
    tab_hasta("#doc-numero", ritmo=300) if False else None
    pg.keyboard.press("Shift+Tab"); pausa(600)
    pg.keyboard.press("Control+a"); escribir(pg.evaluate("Sunat.ejemplos.rucs[0]"), 120)
    leyenda("Con un RUC válido, Consultar SUNAT trae la razón social (simulado)", 1200)
    tecla("Tab", 600); tecla("Enter", 1200)
    pg.wait_for_function("document.querySelector('#doc-nombre').value !== ''"); pausa(3500)
    tab_hasta("button[type=submit]", ritmo=300)
    leyenda("Guardar", 1500); tecla("Enter", 1200)
    leyenda("La venta queda registrada y el comprobante aceptado por SUNAT (simulado)", 4500)
    leyenda("Esc o Tab dentro del diálogo: el foco no se escapa", 3000)
    tecla("Tab", 1500); leyenda("Ver comprobante", 1200); tecla("Enter", 1500)
    leyenda("Factura con IGV de 18 %: base, IGV y total", 5500)

    # 4. Ganancias y tabla alternativa
    tab_hasta("a[data-nav=ganancias]", ritmo=250)
    leyenda("Ganancias desde la barra de navegación", 1500); tecla("Enter", 2000)
    tab_hasta("input[name=modo]", ritmo=300)
    leyenda("Semana, Mes o Fechas con las flechas", 1500); tecla("ArrowRight", 3500)
    tab_hasta("summary", ritmo=300)
    leyenda("El gráfico tiene una tabla alternativa con los mismos datos", 1500); tecla("Enter", 4500)

    # 5. Sin conexión
    tab_hasta("a[data-nav=perfil]", ritmo=250)
    leyenda("Perfil: interruptor para simular que no hay internet", 1500); tecla("Enter", 1500)
    tab_hasta("[data-accion=red]", ritmo=300); tecla("Enter", 1500)
    leyenda("Sin conexión: el aviso lo dice y la app sigue funcionando", 4500)
    tab_hasta("a[data-nav=ventas]", ritmo=250); tecla("Enter", 1200)
    tab_hasta("main a[href='#/ventas/nueva']", ritmo=250); tecla("Enter", 1200)
    tab_hasta("#prod-0", ritmo=250); tecla("ArrowDown", 600); tecla("Tab", 400); escribir("1", 250)
    tab_hasta("input[name=tipo]", ritmo=250); tecla("ArrowDown", 1200)
    tab_hasta("button[type=submit]", ritmo=250); tecla("Enter", 1200)
    leyenda("Sin internet la boleta queda «Pendiente de envío»", 4500)
    tecla("Escape", 1500)
    leyenda("La lista de ventas es larga: se recorre rápido con Tab hasta la barra", 1000)
    tab_hasta("a[data-nav=perfil]", maximo=250, ritmo=25); tecla("Enter", 1200)
    tab_hasta("[data-accion=red]", ritmo=300); tecla("Enter", 800)
    leyenda("Vuelve internet: los comprobantes pendientes se envían solos", 5000)

    # 6. Cambios sin guardar
    tab_hasta("a[data-nav=productos]", ritmo=250); tecla("Enter", 1200)
    tab_hasta("main a[href='#/productos/nuevo']", ritmo=250); tecla("Enter", 1200)
    tab_hasta("#nombre", ritmo=300); escribir("Fideos", 200)
    leyenda("Si hay cambios sin guardar, salir pide confirmación", 1500)
    tab_hasta("a[aria-label=Volver]", ritmo=200) if False else None
    pg.keyboard.press("Shift+Tab"); pausa(400); pg.keyboard.press("Shift+Tab"); pausa(1000)
    tab_hasta("a[aria-label=Volver]", maximo=20, ritmo=300); tecla("Enter", 3500)
    leyenda("«Continuar editando» está seleccionado por defecto; Esc también lo elige", 4000)
    tecla("Escape", 1500)

    leyenda("Todo el sistema se usa con teclado, con foco visible, errores con texto y sin depender del color", 6000)
    ruta = pg.video.path()
    ctx.close(); nav.close()

webm = os.path.join(SAL, "demo_3min.webm"); mp4 = os.path.join(SAL, "demo_3min.mp4")
shutil.move(ruta, webm); shutil.rmtree(TMP, ignore_errors=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", webm, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", mp4], check=True)
print("video:", mp4)
