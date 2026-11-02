"""Prueba de humo: abre cada pantalla de la app, anota errores de consola y guarda una captura."""
import sys, os
from playwright.sync_api import sync_playwright

RAIZ = r"D:\PruebasTareas\ihm_pa3"
URL = "file:///D:/PruebasTareas/ihm_pa3/app/index.html"
SALIDA = os.path.join(RAIZ, "evidencia", "capturas")
os.makedirs(SALIDA, exist_ok=True)

RUTAS = ["inicio", "productos", "productos/nuevo", "productos/editar/p1", "ventas", "ventas/nueva", "ganancias",
         "perfil", "login", "registro", "premium", "negocio", "comprobantes"]

errores = []
with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, locale="es-PE")
    pag = ctx.new_page()
    pag.on("console", lambda m: errores.append(("consola", m.type, m.text)) if m.type in ("error", "warning") else None)
    pag.on("pageerror", lambda e: errores.append(("excepción", str(e))))
    pag.goto(URL)
    pag.wait_for_selector("main h1")
    for i, r in enumerate(RUTAS, 1):
        pag.evaluate(f"location.hash = '#/{r}'")
        pag.wait_for_timeout(250)
        titulo = pag.inner_text("main h1")
        pag.screenshot(path=os.path.join(SALIDA, f"{i:02d}_{r.replace('/', '-')}.png"), full_page=True)
        print(f"{i:02d} #{r:22s} h1={titulo!r}")
    nav.close()

print("\nERRORES:", errores if errores else "ninguno")
