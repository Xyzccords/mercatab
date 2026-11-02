"""Prueba la hoja digital PRUEBA_CON_USUARIOS.html: SUS, cronómetro, errores, guardado, CSV y axe."""
import os, subprocess, sys
from playwright.sync_api import sync_playwright

URL = "file:///D:/PruebasTareas/ihm_pa3/PRUEBA_CON_USUARIOS.html"
AXE = open(r"D:\PruebasTareas\ihm_pa3\tools\axe.min.js", encoding="utf-8").read()
res = []
def ver(n, ok, det=""):
    res.append(ok); print(("OK    " if ok else "FALLA ") + n + (f"  [{det}]" if det and not ok else ""))

with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 390, "height": 844}, accept_downloads=True, locale="es-PE")
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(URL); pg.evaluate("localStorage.clear()"); pg.reload()

    pg.fill("#codigo", "U1"); pg.fill("#edad", "34"); pg.fill("#ocupacion", "Dueño de abarrotería"); pg.select_option("#perfil", "Don Teo")
    pg.check("input[name=consent_verbal]"); pg.check("input[name=ctx_teclado]")

    pg.click("#b-inicio"); pg.wait_for_timeout(1300); pg.click("#b-fin")
    t = float(pg.evaluate("tiempo"))
    ver("El cronómetro mide la tarea (≈1,3 s)", 1.1 <= t <= 2.0, str(t))
    ver("Detener deshabilita Detener y habilita Iniciar", pg.is_disabled("#b-fin") and not pg.is_disabled("#b-inicio"))

    for i in (1, 2, 3, 4): pg.check(f"input[name=paso{i}]")
    ver("4 de 5 pasos = 80 % de efectividad", pg.inner_text("#efectividad") == "80 %", pg.inner_text("#efectividad"))

    pg.click("#b-error"); pg.fill("#e-que-0", "Dudó entre los dos botones de Inicio"); pg.select_option("#e-tip-0", "Equivocación")
    ver("Anotar error crea una fila con el minuto del reloj", pg.input_value("#e-min-0").startswith("00:0"), pg.input_value("#e-min-0"))

    resp = [5, 1, 5, 1, 4, 1, 5, 1, 5, 2]
    for i, v in enumerate(resp, 1):
        pg.check(f"input[name=sus{i}][value='{v}']") if False else pg.locator(f"input[name=sus{i}][value='{v}']").check(force=True)
    calc = subprocess.run([sys.executable, r"D:\PruebasTareas\ihm_pa3\tools\sus.py", *map(str, resp)], capture_output=True, text=True).stdout
    ver("SUS de la hoja coincide con tools/sus.py (95)", pg.inner_text("#sus-puntaje") == "95" and "95" in calc, pg.inner_text("#sus-puntaje") + " / " + calc.strip())
    ver("Interpretación del SUS", "excelente" in pg.inner_text("#sus-texto"), pg.inner_text("#sus-texto"))

    pg.reload()
    ver("El borrador sobrevive a recargar la página", pg.input_value("#codigo") == "U1" and pg.inner_text("#sus-puntaje") == "95" and pg.input_value("#e-que-0") != "")

    pg.click("#b-guardar")
    ver("Guardar agrega al participante a la tabla", "U1" in pg.inner_text("#guardados") and "80 %" in pg.inner_text("#guardados"), pg.inner_text("#guardados"))
    pg.once("dialog", lambda d: d.accept()); pg.click("#b-nuevo")
    ver("Nuevo participante limpia el formulario", pg.input_value("#codigo") == "" and pg.inner_text("#sus-puntaje") == "—")
    pg.click("#b-guardar")
    ver("Guardar sin código lo pide con texto", "código" in pg.inner_text("#estado-guardar"))

    with pg.expect_download() as d: pg.click("#b-csv")
    ruta = d.value.path(); txt = open(ruta, encoding="utf-8-sig").read()
    ver("El CSV trae el participante, el SUS 95 y el error", "U1" in txt and '"95"' in txt and "Dudó entre los dos botones" in txt, txt[-300:])
    ver("El CSV tiene encabezado y 1 fila", len(txt.strip().split("\r\n")) == 2)

    pg.goto(URL); pg.keyboard.press("Tab")
    ver("El primer Tab cae en el skip link", pg.evaluate("document.activeElement.className") == "saltar")

    pg.add_script_tag(content=AXE)
    axe = pg.evaluate("() => axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','best-practice'] } }).then(r => r.violations.map(v => v.id + ' (' + v.nodes.length + ')'))")
    ver("axe-core sin violaciones en la hoja", not axe, str(axe))
    ver("Sin errores de JavaScript", not errs, str(errs))
    nav.close()

print(f"\n{sum(res)}/{len(res)} verificaciones correctas"); sys.exit(0 if all(res) else 1)
