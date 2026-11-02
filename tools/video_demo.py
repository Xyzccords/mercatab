"""Graba una demostración del flujo completo usando solo teclado (sin voz). Sirve de base para el video de 3 min."""
import os, shutil
from playwright.sync_api import sync_playwright

URL = "file:///D:/PruebasTareas/ihm_pa3/app/index.html"
SAL = r"D:\PruebasTareas\ihm_pa3\evidencia\video"
TMP = os.path.join(SAL, "tmp"); os.makedirs(TMP, exist_ok=True)

TECLAS = """
(() => {
  const caja = document.createElement('div');
  caja.setAttribute('aria-hidden', 'true');
  caja.style.cssText = 'position:fixed;right:8px;top:8px;z-index:99999;background:#2B2118;color:#fff;font:700 18px Arial;padding:6px 12px;border-radius:8px;opacity:0;transition:opacity .15s';
  document.body.append(caja);
  let t;
  addEventListener('keydown', e => {
    const nombre = { ' ': 'Espacio', ArrowDown: '↓', ArrowUp: '↑', ArrowLeft: '←', ArrowRight: '→' }[e.key] || (e.key.length === 1 ? '' : e.key);
    if (!nombre) return;
    caja.textContent = (e.shiftKey ? 'Shift + ' : '') + nombre; caja.style.opacity = 1; clearTimeout(t); t = setTimeout(() => caja.style.opacity = 0, 900);
  }, true);
})();
"""

with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 390, "height": 844}, record_video_dir=TMP, record_video_size={"width": 390, "height": 844}, locale="es-PE")
    pg = ctx.new_page()
    pg.goto(URL); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_selector("main h1")
    pg.evaluate(TECLAS)
    pausa = lambda ms=600: pg.wait_for_timeout(ms)

    def tab_hasta(sel, maximo=40):
        for _ in range(maximo):
            if pg.evaluate("(s) => document.activeElement.matches(s)", sel): return
            pg.keyboard.press("Tab"); pausa(380)
        raise RuntimeError("no se llegó a " + sel)

    pausa(1500)
    pg.keyboard.press("Tab"); pausa(1500)                       # skip link visible
    pg.keyboard.press("Enter"); pausa(900)
    tab_hasta("main a[href='#/ventas/nueva']"); pausa(700); pg.keyboard.press("Enter"); pausa(1200)
    tab_hasta("#prod-0"); pg.keyboard.press("ArrowDown"); pausa(800)
    pg.keyboard.press("Tab"); pg.keyboard.type("2", delay=200); pausa(900)
    tab_hasta("input[name=tipo]"); pausa(500)
    pg.keyboard.press("ArrowDown"); pausa(500); pg.keyboard.press("ArrowDown"); pausa(1000)   # Factura
    tab_hasta("#doc-numero"); pg.keyboard.type(pg.evaluate("Sunat.ejemplos.rucs[0]"), delay=110); pausa(700)
    pg.keyboard.press("Tab"); pausa(500); pg.keyboard.press("Enter")                          # Consultar SUNAT
    pg.wait_for_function("document.querySelector('#doc-nombre').value !== ''"); pausa(1500)
    tab_hasta("button[type=submit]"); pausa(600); pg.keyboard.press("Enter"); pausa(1800)     # Guardar
    pg.keyboard.press("Tab"); pausa(600); pg.keyboard.press("Enter"); pausa(2500)             # Ver comprobante
    tab_hasta("a[data-nav=ganancias]"); pausa(500); pg.keyboard.press("Enter"); pausa(1800)   # Ganancias
    tab_hasta("input[name=modo]"); pausa(500); pg.keyboard.press("ArrowRight"); pausa(2200)   # Mes
    ruta = pg.video.path()
    ctx.close(); nav.close()

destino = os.path.join(SAL, "demo_teclado.webm")
shutil.move(ruta, destino); shutil.rmtree(TMP, ignore_errors=True)
print("video:", destino, round(os.path.getsize(destino) / 1e6, 2), "MB")
