"""Pruebas de flujo de MercaTab con Playwright. Cada verificación imprime OK o FALLA."""
import os, re, sys
from playwright.sync_api import sync_playwright

URL = "file:///D:/PruebasTareas/ihm_pa3/app/index.html"
resultados = []

def verificar(nombre, condicion, detalle=""):
    resultados.append((nombre, bool(condicion)))
    print(("OK    " if condicion else "FALLA ") + nombre + (f"  [{detalle}]" if detalle and not condicion else ""))

with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(viewport={"width": 390, "height": 844}, locale="es-PE")
    pg = ctx.new_page()
    errores = []
    pg.on("pageerror", lambda e: errores.append(str(e)))
    pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
    pg.goto(URL)
    pg.evaluate("localStorage.clear()"); pg.reload()
    pg.wait_for_selector("main h1")

    # --- Skip link: primer elemento focusable
    pg.keyboard.press("Tab")
    verificar("El primer Tab cae en 'Ir al contenido principal'", pg.evaluate("document.activeElement.id") == "saltar")
    pg.keyboard.press("Enter")
    verificar("El skip link lleva el foco a <main>", pg.evaluate("document.activeElement.id") == "contenido")

    # --- Producto nuevo: validación y guardado
    pg.goto(URL + "#/productos/nuevo"); pg.wait_for_selector("#nombre")
    pg.click("button[type=submit]")
    verificar("Formulario vacío muestra resumen de errores", pg.locator("#resumen-errores").count() == 1)
    verificar("El foco pasa al resumen de errores", pg.evaluate("document.activeElement.id") == "resumen-errores")
    verificar("Error del precio con texto (no solo color)", "mayor que 0" in pg.inner_text("#precio-error"))
    pg.fill("#nombre", "Fideos Don Vittorio (500g)"); pg.fill("#stock", "30"); pg.fill("#precio", "3.50"); pg.fill("#inversion", "75")
    pg.click("button[type=submit]")
    pg.wait_for_selector("dialog[open]")
    verificar("Aparece el modal ¡Producto registrado!", "Producto registrado" in pg.inner_text("#modal-titulo"))
    pg.keyboard.press("Escape")
    pg.wait_for_selector("main h1:has-text('Productos')")
    verificar("Esc cierra el modal y vuelve a la lista", "Fideos Don Vittorio" in pg.inner_text("main"))

    # --- Venta con factura y consulta SUNAT simulada
    pg.goto(URL + "#/ventas/nueva"); pg.wait_for_selector("#prod-0")
    pg.click("button[type=submit]")
    verificar("Venta vacía pide al menos un producto", "al menos un producto" in pg.inner_text("#resumen-errores"))
    pg.select_option("#prod-0", index=1); pg.fill("#cant-0", "999")
    pg.click("button[type=submit]")
    verificar("Cantidad mayor al stock muestra cuánto queda", "Solo quedan" in pg.inner_text("main"))
    pg.fill("#cant-0", "2")
    verificar("El total se calcula al escribir", "19.60" in pg.inner_text("#total"), pg.inner_text("#total"))
    pg.check("input[value=factura]")
    pg.click("button[type=submit]")
    verificar("Factura sin RUC muestra error de RUC", "RUC debe tener 11" in pg.inner_text("main"))
    ruc = pg.evaluate("Sunat.ejemplos.rucs[0]")
    pg.fill("#doc-numero", ruc); pg.click("[data-accion=consultar]")
    pg.wait_for_function("document.querySelector('#doc-nombre').value !== ''")
    verificar("Consultar SUNAT rellena la razón social", "EJEMPLO" in pg.input_value("#doc-nombre"))
    pg.click("button[type=submit]")
    pg.wait_for_selector("dialog[open]")
    verificar("Venta registrada con comprobante F001-00000001", "F001-00000001" in pg.inner_text("#modal"), pg.inner_text("#modal"))
    verificar("Con internet el comprobante queda aceptado", "Aceptado" in pg.inner_text("#modal"))
    pg.click("dialog button:has-text('Ver comprobante')")
    pg.wait_for_selector(".ticket")
    verificar("El comprobante calcula IGV 18 %", "IGV" in pg.inner_text(".ticket") and "2.99" in pg.inner_text(".ticket"), pg.inner_text(".ticket")[-200:])

    # --- Sin conexión: boleta pendiente y envío al volver internet
    pg.goto(URL + "#/perfil"); pg.wait_for_selector("[data-accion=red]")
    pg.click("[data-accion=red]")
    verificar("Interruptor de red tiene aria-checked=true", pg.get_attribute("[data-accion=red]", "aria-checked") == "true")
    verificar("Aparece el aviso 'Sin conexión'", "Sin conexión" in pg.inner_text("#red"))
    pg.goto(URL + "#/ventas/nueva"); pg.wait_for_selector("#prod-0")
    pg.select_option("#prod-0", index=2); pg.fill("#cant-0", "1"); pg.check("input[value=boleta]")
    pg.click("button[type=submit]"); pg.wait_for_selector("dialog[open]")
    verificar("Sin internet la boleta queda pendiente", "Pendiente" in pg.inner_text("#modal"), pg.inner_text("#modal"))
    pg.keyboard.press("Escape")
    pg.goto(URL + "#/perfil"); pg.wait_for_selector("[data-accion=red]")
    pg.click("[data-accion=red]")
    pg.wait_for_selector(".aviso")
    verificar("Al volver internet se envían los pendientes", "se enviaron" in pg.inner_text("#avisos"), pg.inner_text("#avisos"))

    # --- Cambios sin guardar
    pg.goto(URL + "#/productos/nuevo"); pg.wait_for_selector("#nombre")
    pg.fill("#nombre", "Algo"); pg.click("a[aria-label=Volver]")
    pg.wait_for_selector("dialog[open]")
    verificar("Salir con cambios pide confirmar", "sin guardar" in pg.inner_text("#modal-titulo"))
    pg.click("dialog button:has-text('Continuar editando')")
    verificar("Continuar editando se queda en el formulario", "nuevo" in pg.url)

    # --- Navegación por teclado: de la barra inferior a Ganancias
    pg.goto(URL + "#/inicio"); pg.wait_for_selector("dialog[open]")
    pg.click("dialog button:has-text('Sí, salir')"); pg.wait_for_selector("main h1:has-text('Resumen')")
    pg.reload(); pg.wait_for_selector("main h1")
    for _ in range(12):
        pg.keyboard.press("Tab")
        if pg.evaluate("document.activeElement.dataset && document.activeElement.dataset.nav") == "ganancias": break
    verificar("Con Tab se llega al botón Ganancias de la barra", pg.evaluate("document.activeElement.dataset.nav") == "ganancias")
    pg.keyboard.press("Enter"); pg.wait_for_selector("main h1:has-text('Ganancias')")
    verificar("Enter abre Ganancias y el foco pasa al título", pg.evaluate("document.activeElement.tagName") == "H1")
    pg.keyboard.press("Tab")
    verificar("El foco es visible (outline de 3 px)", pg.evaluate("parseFloat(getComputedStyle(document.activeElement).outlineWidth)") >= 3)

    verificar("Sin errores de JavaScript en toda la prueba", not errores, str(errores))
    nav.close()

fallas = [n for n, ok in resultados if not ok]
print(f"\n{len(resultados) - len(fallas)}/{len(resultados)} verificaciones correctas")
sys.exit(1 if fallas else 0)
