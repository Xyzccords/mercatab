# -*- coding: utf-8 -*-
"""Presentación del PA3: 9 diapositivas, palabras clave e imágenes."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image

RAIZ = r"D:\PruebasTareas\ihm_pa3"
EV = os.path.join(RAIZ, "evidencia")
OUT = os.path.join(RAIZ, "PA3_PPT_Guerrero_Salvador.pptx")
IM = lambda *r: os.path.join(EV, *r)

MARRON = RGBColor(0x7B, 0x4A, 0x2D); OSCURO = RGBColor(0x2B, 0x21, 0x18); DURAZNO = RGBColor(0xF4, 0xA2, 0x7A)
CREMA = RGBColor(0xF5, 0xEC, 0xE8); BLANCO = RGBColor(255, 255, 255); GRIS = RGBColor(0x5C, 0x4A, 0x3F)
ROJO = RGBColor(0xB3, 0x26, 0x1E); VERDE = RGBColor(0x1F, 0x6B, 0x3A); AMARILLO = RGBColor(0xFF, 0xF1, 0x76)
TITULO, CUERPO = "Arial", "Calibri"

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
VACIA = prs.slide_layouts[6]

def fondo(s, c): f = s.background.fill; f.solid(); f.fore_color.rgb = c

def texto(s, x, y, w, h, t, tam=18, neg=False, color=OSCURO, fuente=CUERPO, alin=PP_ALIGN.LEFT, ancla=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = ancla
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, ln in enumerate(t if isinstance(t, list) else [t]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = alin
        r = p.add_run(); r.text = ln; r.font.size = Pt(tam); r.font.bold = neg; r.font.name = fuente; r.font.color.rgb = color
    return tb

def forma(s, tipo, x, y, w, h, c, borde=None, radio=None):
    f = s.shapes.add_shape(tipo, Inches(x), Inches(y), Inches(w), Inches(h)); f.fill.solid(); f.fill.fore_color.rgb = c
    if borde: f.line.color.rgb = borde; f.line.width = Pt(2)
    else: f.line.fill.background()
    f.shadow.inherit = False
    if radio is not None and tipo == MSO_SHAPE.ROUNDED_RECTANGLE: f.adjustments[0] = radio
    return f

def imagen(s, ruta, x, y, w, h, alt):
    iw, ih = Image.open(ruta).size; e = min(w / iw, h / ih); pw, ph = iw * e, ih * e
    pic = s.shapes.add_picture(ruta, Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))
    pic._element.nvPicPr.cNvPr.set("descr", alt)
    return pic

def titulo(s, t, color=MARRON): texto(s, 0.6, 0.35, 12.1, 1.0, t, 30, True, color, TITULO, ancla=MSO_ANCHOR.MIDDLE)
def pie(s, claro=False): texto(s, 0.6, 7.05, 8, 0.3, "MercaTab · PA3", 11, False, DURAZNO if claro else GRIS)
def notas(s, t): s.notes_slide.notes_text_frame.text = t

def pendiente(s, x, y, w, h, t):
    f = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, AMARILLO, OSCURO, 0.15)
    texto(s, x + 0.15, y, w - 0.3, h, t, 14, True, OSCURO, alin=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)

# 1. Portada
s = prs.slides.add_slide(VACIA); fondo(s, MARRON)
texto(s, 0.8, 1.7, 11.5, 1.4, "MercaTab", 60, True, BLANCO, TITULO)
texto(s, 0.8, 3.0, 11.5, 0.6, "PA3 · Código accesible y validación final", 26, False, DURAZNO)
texto(s, 0.8, 3.7, 11.5, 0.5, "Versión PA3 · Interacción Hombre-Máquina · UTP", 20, False, BLANCO)
texto(s, 0.8, 5.0, 6, 1.2, ["Guerrero Mirez, Diego", "Salvador Silva, Lindel"], 20, False, BLANCO)
texto(s, 7.2, 5.0, 5.5, 1.2, ["Docente: Davila Hurtado, Luis Alberto", "2026"], 20, False, BLANCO)
notas(s, "Presentar el sistema, el curso y quién expone cada parte. Mencionar que el código está en el repositorio y desplegado.")

# 2. Del Figma al código
s = prs.slides.add_slide(VACIA); fondo(s, BLANCO)
titulo(s, "Del Figma al código: el mismo diseño, con las correcciones de la prueba")
for i, (n, alt) in enumerate([("inicio", "Inicio: Figma del PA2 junto a la pantalla programada"), ("productos", "Productos: Figma junto a la pantalla programada"), ("ganancias", "Ganancias: Figma junto a la pantalla programada")]):
    imagen(s, IM("comparacion", n + ".png"), 0.5 + i * 4.25, 1.5, 4.1, 4.7, alt)
texto(s, 0.6, 6.35, 12.1, 0.6, "Botón verde → contorno  ·  Ícono de caja registradora  ·  Valores en el gráfico  ·  Íconos de 44 px", 18, True, MARRON, alin=PP_ALIGN.CENTER)
pie(s); notas(s, "Izquierda Figma del PA2, derecha el sistema real. Cada cambio sale de un hallazgo del PA2: el verde no pasaba contraste, el ícono de Registrar venta se repetía con Ventas, el gráfico no tenía valores y los íconos de editar y eliminar estaban muy juntos.")

# 3. Accesibilidad
s = prs.slides.add_slide(VACIA); fondo(s, BLANCO)
titulo(s, "Se aplicaron los 11 criterios WCAG de la guía, no solo 8")
cajas = [("04", "Foco visible", 0.5, 1.5, 4.0, 2.2), ("09", "Skip link", 4.7, 1.5, 4.0, 2.2), ("05", "ARIA labels en íconos", 8.9, 1.5, 4.0, 2.2),
         ("06", "Áreas táctiles de 44 px", 0.5, 4.2, 4.0, 2.2), ("11", "Tipografía mínima 14 px", 4.7, 4.2, 4.0, 2.2)]
for n, nombre, x, y, w, h in cajas:
    forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h + 0.3, CREMA, None, 0.05)
    imagen(s, IM("codigo_ppt", n + ".png"), x + 0.1, y + 0.05, w - 0.2, h - 0.1, f"Fragmento de código: {nombre}")
    texto(s, x + 0.1, y + h - 0.05, w - 0.2, 0.35, nombre, 15, True, MARRON, alin=PP_ALIGN.CENTER)
texto(s, 8.9, 4.2, 4.0, 1.6, "11/11", 66, True, MARRON, TITULO, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
texto(s, 8.9, 5.8, 4.0, 0.6, "criterios con código y evidencia", 16, False, GRIS, alin=PP_ALIGN.CENTER)
pie(s); notas(s, "Los otros seis criterios (alt text, contraste, teclado, errores con texto, labels con autocomplete y estructura semántica) están en el informe con su código. Preparar para explicar cualquier línea en vivo.")

# 4. axe
s = prs.slides.add_slide(VACIA); fondo(s, BLANCO)
titulo(s, "axe-core: 0 violaciones en 10 pantallas del sistema real")
imagen(s, IM("axe", "informe_axe.png"), 0.5, 1.5, 7.6, 5.0, "Informe de axe-core con cero violaciones en diez pantallas")
for i, (g, t) in enumerate([("18 / 18", "pares de color ≥ 4,5:1"), ("0", "elementos táctiles < 44 px"), ("14 px", "texto más pequeño")]):
    texto(s, 8.5, 1.6 + i * 1.55, 4.3, 0.9, g, 40, True, MARRON, TITULO)
    texto(s, 8.5, 2.45 + i * 1.55, 4.3, 0.5, t, 18, False, GRIS)
pendiente(s, 8.5, 6.2, 4.3, 0.6, "Captura con extensión axe/WAVE: pendiente")
pie(s); notas(s, "El informe se generó con axe-core 4.10.2, el motor de axe DevTools, ejecutado por script. Falta repetirlo en Chrome con la extensión (axe DevTools o WAVE) en 3 pantallas y pegar la captura aquí.")

# 5. Prueba con usuarios
s = prs.slides.add_slide(VACIA); fondo(s, BLANCO)
titulo(s, "Comparativa PA2 vs PA3 con la misma tarea y usuarios reales")
filas = [("Métrica", "PA2 · Figma", "PA3 · Código"), ("Efectividad", "100 %", ""), ("Eficiencia", "41 · 53 · 35 s", ""), ("SUS", "94,2", ""), ("Errores", "12", "")]
for i, fila in enumerate(filas):
    for j, v in enumerate(fila):
        x = 0.6 + [0, 2.6, 5.2][j]; y = 1.6 + i * 0.95
        c = MARRON if i == 0 else (AMARILLO if (j == 2) else CREMA)
        forma(s, MSO_SHAPE.RECTANGLE, x, y, 2.5 if j == 0 else 2.5, 0.85, c)
        texto(s, x + 0.1, y, 2.3, 0.85, v if (v or i == 0) else "[   ]", 18, i == 0 or j == 0, BLANCO if i == 0 else OSCURO, alin=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)
f = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, 8.7, 1.6, 4.0, 3.8, BLANCO, GRIS, 0.04)
texto(s, 8.9, 1.6, 3.6, 3.8, "Foto o evidencia de la prueba", 18, True, GRIS, alin=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)
pendiente(s, 8.7, 5.7, 4.0, 0.7, "Falta ejecutar la prueba con ≥ 2 usuarios")
pie(s); notas(s, "Completar con la prueba real: mínimo 2 usuarios, uno del perfil del PA1; SUS por usuario; cronometrar solo la tarea. Los tiempos del PA2 son la duración de toda la sesión, así que conviene aclararlo al comparar.")

# 6. Hallazgos
s = prs.slides.add_slide(VACIA); fondo(s, BLANCO)
titulo(s, "Tres barreras del código real y cómo se resolvieron")
datos = [("2,83 → 6,31", ":1", "Contraste del botón verde del Figma", "Botón de contorno marrón"),
         ("20 → 44", " px", "Enlaces dentro de frases", "Enlaces con área táctil de 44 px"),
         ("362 → 320", " px", "Ancho de Ventas con scroll horizontal", "Filtros que se adaptan al ancho")]
for i, (cifra, un, mal, bien) in enumerate(datos):
    y = 1.6 + i * 1.75
    forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.6, y, 12.1, 1.5, CREMA, None, 0.06)
    texto(s, 0.9, y, 4.6, 1.5, cifra + un, 36, True, MARRON, TITULO, ancla=MSO_ANCHOR.MIDDLE)
    texto(s, 5.6, y + 0.25, 7.0, 0.5, mal, 20, True, OSCURO)
    texto(s, 5.6, y + 0.8, 7.0, 0.5, "→ " + bien, 20, False, GRIS)
pie(s); notas(s, "Los tres salieron de medir el sistema real, no de la revisión visual. axe no marcó los dos últimos: los encontraron las mediciones propias de tamaño táctil y la prueba de reflow a 320 px.")

# 7. Demo
s = prs.slides.add_slide(VACIA); fondo(s, OSCURO)
titulo(s, "Demo: registrar una venta con factura, solo con teclado", BLANCO)
for i, (n, alt) in enumerate([("inicio", "Pantalla de inicio"), ("venta_factura", "Venta con factura y consulta de SUNAT"), ("comprobante", "Comprobante emitido")]):
    imagen(s, IM("pantallas", n + ".png"), 0.7 + i * 3.35, 1.5, 3.1, 4.7, alt)
for i, t in enumerate(["Tab", "Enter", "Esc"]):
    forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, 11.0, 1.7 + i * 1.2, 1.7, 0.9, DURAZNO, None, 0.2)
    texto(s, 11.0, 1.7 + i * 1.2, 1.7, 0.9, t, 24, True, OSCURO, TITULO, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
texto(s, 0.7, 6.4, 12, 0.5, "Inicio → Registrar venta → Factura → Consultar SUNAT → Comprobante → Ganancias", 18, False, BLANCO)
pie(s, True); notas(s, "Abrir el sistema y no usar el mouse: skip link con el primer Tab, Registrar venta, elegir producto y cantidad, factura, RUC de ejemplo, Consultar SUNAT, Guardar, ver comprobante, Ganancias. Luego simular sin conexión desde Perfil.")

# 8. Ciclo DCU
s = prs.slides.add_slide(VACIA); fondo(s, BLANCO)
titulo(s, "El ciclo DCU se cerró: de un cuaderno a un sistema accesible")
pasos = [("Problema", "Cuaderno y errores"), ("PA1", "Perfiles y GOMS"), ("PA2", "Figma · 12 errores · SUS 94,2"), ("PA3", "Código · 11 criterios · axe 0")]
for i, (a, b) in enumerate(pasos):
    x = 0.5 + i * 3.15; ult = i == len(pasos) - 1
    forma(s, MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON, x, 2.4, 3.3, 1.6, DURAZNO if ult else MARRON)
    texto(s, x + 0.55, 2.4, 2.2, 1.6, a, 26, True, OSCURO if ult else BLANCO, TITULO, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    texto(s, x + 0.2, 4.2, 2.9, 1.0, b, 16, False, GRIS, alin=PP_ALIGN.CENTER)
texto(s, 0.6, 5.7, 12.1, 0.7, "Probar → detectar → corregir → volver a probar", 28, True, MARRON, TITULO, PP_ALIGN.CENTER)
pie(s); notas(s, "Mostrar que se entiende el ciclo: cada flecha tiene evidencia en el informe. El PA3 cierra con la validación con usuarios.")

# 9. Reflexión
s = prs.slides.add_slide(VACIA); fondo(s, MARRON)
texto(s, 0.9, 2.2, 11.5, 2.6, "MercaTab ya funciona sin internet y sin mouse; falta probarlo con un bodeguero mayor.", 40, True, BLANCO, TITULO, ancla=MSO_ANCHOR.MIDDLE)
texto(s, 0.9, 6.3, 8, 0.5, "MercaTab · PA3", 18, False, DURAZNO)
notas(s, "Una sola frase de impacto. Si la prueba con usuarios ya se hizo, ajustar la frase al resultado real.")

prs.save(OUT); print("OK", OUT, len(prs.slides._sldIdLst), "diapositivas")
