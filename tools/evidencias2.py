"""Capturas de foco visible y skip link, y lectura del reflow a 320 px."""
import os
from playwright.sync_api import sync_playwright
URL = "file:///D:/PruebasTareas/ihm_pa3/app/index.html"
SAL = r"D:\PruebasTareas\ihm_pa3\evidencia\pantallas"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, locale="es-PE").new_page()
    pg.goto(URL); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_selector("main h1")
    pg.keyboard.press("Tab")
    pg.screenshot(path=os.path.join(SAL, "foco_skip.png"), clip={"x": 0, "y": 0, "width": 390, "height": 200})
    for _ in range(2): pg.keyboard.press("Tab")
    pg.screenshot(path=os.path.join(SAL, "foco_boton.png"), clip={"x": 0, "y": 250, "width": 390, "height": 330})
    pg2 = b.new_context(viewport={"width": 320, "height": 640}, device_scale_factor=2, locale="es-PE").new_page()
    pg2.goto(URL + "#/ventas"); pg2.wait_for_selector("main h1")
    pg2.screenshot(path=os.path.join(SAL, "reflow_320.png"))
    b.close()
