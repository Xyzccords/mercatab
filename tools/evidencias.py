"""Genera la evidencia del PA3: capturas del sistema real, comparación Figma vs código, informe axe y fragmentos de código."""
import json, os, re, html
from playwright.sync_api import sync_playwright
from PIL import Image

RAIZ = r"D:\PruebasTareas\ihm_pa3"
APP = os.path.join(RAIZ, "app")
URL = "file:///D:/PruebasTareas/ihm_pa3/app/index.html"
EV = os.path.join(RAIZ, "evidencia")
for d in ("pantallas", "comparacion", "codigo", "axe"):
    os.makedirs(os.path.join(EV, d), exist_ok=True)
os.makedirs(os.path.join(EV, "codigo_ppt"), exist_ok=True)
FIGMA = r"D:\PruebasTareas\ihm_pa2\img\figma"

# ---------- fragmentos de código ----------
CRITERIOS = [  # (n.º, nombre, archivo, patrón de inicio, líneas antes, líneas después)
    (1, "Alt text descriptivo", "js/vistas.js", "const fotoDe", 0, 3),
    (2, "Contraste mínimo 4.5:1", "css/estilos.css", ":root {", 0, 20),
    (3, "Navegación por teclado", "js/app.js", "function pintar(moverFoco", 0, 16),
    (4, "Foco visible", "css/estilos.css", ":focus-visible", 0, 2),
    (5, "ARIA labels en iconos", "js/vistas.js", 'class="acciones">', 0, 4),
    (6, "Áreas táctiles de 44 px", "css/estilos.css", ".boton {", 0, 7),
    (7, "Errores con texto, no solo color", "js/ui.js", "function campo(", 0, 14),
    (8, "Labels visibles y autocomplete", "js/vistas.js", "campo({ id: 'email'", 0, 1),
    (9, "Skip link", "index.html", 'class="saltar"', 0, 1),
    (10, "Estructura semántica", "index.html", "<header", 0, 1),
    (11, "Tipografía mínima de 14 px", "css/estilos.css", "body {", 0, 6),
]

def trozo(archivo, patron, antes, despues):
    ruta = os.path.join(APP, archivo)
    lineas = open(ruta, encoding="utf-8").read().split("\n")
    i = next(k for k, l in enumerate(lineas) if patron in l)
    a, b = max(0, i - antes), min(len(lineas), i + despues + 1)
    return [(k + 1, lineas[k]) for k in range(a, b)]

def pagina_codigo(titulo, bloques, ancho=760, fuente=15):
    cuerpo = ""
    for archivo, lineas in bloques:
        filas = "".join(f'<tr><td class="n">{n}</td><td class="c">{html.escape(t) or "&nbsp;"}</td></tr>' for n, t in lineas)
        cuerpo += f'<div class="arch">{html.escape(archivo)} · líneas {lineas[0][0]} a {lineas[-1][0]}</div><table>{filas}</table>'
    return f"""<html><head><meta charset="utf-8"><style>
      body{{margin:0;background:#fff;font-family:Consolas,'Courier New',monospace}}
      #caja{{display:inline-block;width:{ancho}px;background:#FBF8F5;border:1px solid #CDB8AC;border-radius:8px;overflow:hidden}}
      .tit{{font:700 16px Arial;background:#5A3420;color:#fff;padding:10px 14px}}
      .arch{{font:700 13px Arial;color:#5C4A3F;padding:8px 14px 2px}}
      table{{border-collapse:collapse;width:100%}} td{{padding:0 14px 0 0;font-size:{fuente}px;line-height:1.45;white-space:pre-wrap;word-break:break-word}}
      .n{{color:#8C7468;text-align:right;padding:0 10px 0 14px;user-select:none;width:36px}} .c{{color:#2B2118}}
    </style></head><body><div id="caja"><div class="tit">{html.escape(titulo)}</div>{cuerpo}</div></body></html>"""

def captura_elemento(pagina, sel, ruta):
    pagina.locator(sel).screenshot(path=ruta)

with sync_playwright() as p:
    nav = p.chromium.launch()

    # 1) fragmentos de código
    pc = nav.new_context(viewport={"width": 1100, "height": 700}, device_scale_factor=2).new_page()
    for n, nombre, archivo, patron, antes, despues in CRITERIOS:
        bloques = [(archivo, trozo(archivo, patron, antes, despues))]
        if n == 9: bloques.append(("css/estilos.css", trozo("css/estilos.css", ".saltar {", 0, 4)))
        if n == 10:
            lin = [(k, l) for k, l in trozo("index.html", "<header", 0, 40) if re.search(r"<(header|nav|main|footer|/header|/footer)", l)]
            bloques = [("index.html", lin)]
        pc.set_content(pagina_codigo(f"Criterio {n}: {nombre}", bloques))
        captura_elemento(pc, "#caja", os.path.join(EV, "codigo", f"{n:02d}.png"))
        pc.set_content(pagina_codigo(f"Criterio {n}: {nombre}", bloques, 480, 17))
        captura_elemento(pc, "#caja", os.path.join(EV, "codigo_ppt", f"{n:02d}.png"))

    # 2) capturas del sistema real
    pg = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, locale="es-PE").new_page()
    pg.goto(URL); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_selector("main h1")
    def ir(ruta):
        pg.evaluate(f"location.hash = '#/{ruta}'"); pg.wait_for_timeout(300)
    def foto(nombre): pg.screenshot(path=os.path.join(EV, "pantallas", nombre + ".png"))

    pg.evaluate("Datos.negocio = { ruc: Sunat.ejemplos.rucs[1], razon: 'ABARROTES LA ESQUINA E.I.R.L.' }")
    ir("inicio"); foto("inicio")
    ir("productos"); foto("productos")
    ir("productos/nuevo"); pg.click("button[type=submit]"); pg.wait_for_timeout(200); foto("producto_errores")
    ir("ventas"); foto("ventas")
    ir("ventas/nueva"); pg.select_option("#prod-0", index=1); pg.fill("#cant-0", "3"); pg.check("input[value=factura]")
    pg.fill("#doc-numero", pg.evaluate("Sunat.ejemplos.rucs[0]")); pg.click("[data-accion=consultar]")
    pg.wait_for_function("document.querySelector('#doc-nombre').value !== ''")
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight)"); pg.wait_for_timeout(150); foto("venta_factura")
    pg.click("button[type=submit]"); pg.wait_for_selector("dialog[open]"); foto("venta_registrada")
    pg.click("dialog button:has-text('Ver comprobante')"); pg.wait_for_selector(".ticket"); pg.wait_for_timeout(200); foto("comprobante")
    ir("ganancias"); foto("ganancias")
    pg.check("#modo-mes", force=True); pg.wait_for_timeout(200); foto("ganancias_mes")
    ir("perfil"); foto("perfil")
    ir("login"); pg.click("button[type=submit]"); pg.wait_for_timeout(200); foto("login_errores")
    ir("registro"); foto("registro")
    ir("perfil"); pg.click("[data-accion=red]"); ir("inicio"); foto("inicio_sin_conexion")
    pg.evaluate("Red.simulada = false")

    # 3) comparación Figma (PA2) vs código (PA3)
    pares = [("inicio", "s3_2.png", "inicio"), ("productos", "s2_3.png", "productos"), ("ganancias", "s6_0.png", "ganancias")]
    for nombre, figma, codigo in pares:
        a = Image.open(os.path.join(FIGMA, figma)).convert("RGB"); b = Image.open(os.path.join(EV, "pantallas", codigo + ".png")).convert("RGB")
        H = 780
        a = a.resize((int(a.width * H / a.height), H), Image.LANCZOS); b = b.resize((int(b.width * H / b.height), H), Image.LANCZOS)
        lienzo = Image.new("RGB", (a.width + b.width + 60, H + 50), "white")
        lienzo.paste(a, (20, 40)); lienzo.paste(b, (a.width + 40, 40))
        from PIL import ImageDraw
        d = ImageDraw.Draw(lienzo); f = None
        d.text((20, 12), "PA2 · Figma", fill=(43, 33, 24)); d.text((a.width + 40, 12), "PA3 · Código real", fill=(43, 33, 24))
        lienzo.save(os.path.join(EV, "comparacion", nombre + ".png"))

    # 4) informe de axe como imagen
    resumen = json.load(open(os.path.join(EV, "axe", "resumen.json"), encoding="utf-8"))
    filas = ""
    for r in resumen:
        ax, pr = r["axe"], r["propio"]
        filas += (f"<tr><td>{html.escape(r['pantalla'])}</td><td class='n'>{len(ax['violations'])}</td><td class='n'>{ax['pasadas']}</td>"
                  f"<td class='n'>{len(ax['incompletas'])}</td><td class='n'>{len(pr['chicos'])}</td><td class='n'>{pr['minFuente']:.0f} px</td><td class='n'>{pr['sinAlt']}</td></tr>")
    total_v = sum(len(r["axe"]["violations"]) for r in resumen)
    pr = nav.new_context(viewport={"width": 900, "height": 600}, device_scale_factor=2).new_page()
    pr.set_content(f"""<html><head><meta charset="utf-8"><style>
      body{{margin:0;font-family:Arial,sans-serif;color:#2B2118}} #caja{{display:inline-block;padding:24px 28px;background:#fff;min-width:820px}}
      h1{{font-size:20px;margin:0 0 4px}} p{{margin:0 0 14px;color:#5C4A3F;font-size:14px}}
      table{{border-collapse:collapse;width:100%;font-size:15px}} th,td{{border-bottom:1px solid #E3D3CA;padding:8px 10px;text-align:left}} th{{background:#5A3420;color:#fff}}
      .n{{text-align:right}} .tot{{font-weight:700;background:#E4F3E9;color:#1F6B3B}}
    </style></head><body><div id="caja"><h1>Informe de accesibilidad: axe-core 4.10.2 sobre el sistema real</h1>
    <p>Reglas WCAG 2.0 y 2.1 niveles A y AA más buenas prácticas. Navegador Chromium, ancho 390 px.</p>
    <table><thead><tr><th>Pantalla</th><th class="n">Violaciones</th><th class="n">Reglas pasadas</th><th class="n">Por revisar</th><th class="n">Táctiles &lt; 44 px</th><th class="n">Fuente mínima</th><th class="n">Img sin alt</th></tr></thead>
    <tbody>{filas}<tr class="tot"><td>Total ({len(resumen)} pantallas)</td><td class="n">{total_v}</td><td colspan="5"></td></tr></tbody></table></div></body></html>""")
    captura_elemento(pr, "#caja", os.path.join(EV, "axe", "informe_axe.png"))
    nav.close()
print("evidencias generadas en", EV)
