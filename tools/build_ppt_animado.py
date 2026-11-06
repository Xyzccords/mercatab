# -*- coding: utf-8 -*-
"""PowerPoint animado del PA3 (9 diapositivas). Animaciones: barridos (wipe), fundidos y trayectorias para que las imágenes
salgan de detrás de un panel; transiciones distintas entre diapositivas. Todo es OOXML estándar (p:timing, p:transition)."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml import parse_xml
from PIL import Image

RAIZ = r"D:\PruebasTareas\ihm_pa3"
EV = os.path.join(RAIZ, "evidencia")
OUT = os.path.join(RAIZ, "PA3_PPT_Guerrero_Salvador.pptx")
IM = lambda *r: os.path.join(EV, *r)
NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
SW, SH = 13.333, 7.5

MARRON = RGBColor(0x7B, 0x4A, 0x2D); OSCURO = RGBColor(0x2B, 0x21, 0x18); DURAZNO = RGBColor(0xF4, 0xA2, 0x7A)
CREMA = RGBColor(0xF5, 0xEC, 0xE8); BLANCO = RGBColor(255, 255, 255); GRIS = RGBColor(0x5C, 0x4A, 0x3F)
VERDE = RGBColor(0x1F, 0x6B, 0x3A); AMARILLO = RGBColor(0xFF, 0xF1, 0x76)
TITULO, CUERPO = "Arial", "Calibri"

prs = Presentation(); prs.slide_width, prs.slide_height = Inches(SW), Inches(SH)
VACIA = prs.slide_layouts[6]

# ---------- formas ----------
def fondo(s, c): f = s.background.fill; f.solid(); f.fore_color.rgb = c

def texto(s, x, y, w, h, t, tam=20, neg=False, color=OSCURO, fuente=CUERPO, alin=PP_ALIGN.LEFT, ancla=MSO_ANCHOR.TOP):
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
    p = s.shapes.add_picture(ruta, Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))
    p._element.nvPicPr.cNvPr.set("descr", alt)
    return p

def titulo(s, t, color=MARRON): return texto(s, 0.6, 0.3, 12.1, 1.0, t, 28, True, color, TITULO, ancla=MSO_ANCHOR.MIDDLE)
def notas(s, t): s.notes_slide.notes_text_frame.text = t
def chip_pendiente(s, x, y, w, h, t):
    forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, AMARILLO, OSCURO, 0.15)
    texto(s, x + 0.12, y, w - 0.24, h, t, 14, True, OSCURO, alin=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)

# ---------- animaciones y transiciones (OOXML) ----------
WIPE = {"l": (8, "wipe(left)"), "r": (2, "wipe(right)"), "u": (1, "wipe(up)"), "d": (4, "wipe(down)")}

ANIM_LOG = []

def animar(slide, clicks):
    """clicks: lista de grupos; cada grupo es una lista de efectos que ocurren juntos tras un clic.
    efecto = dict(kind: wipe|fade|wipe_out|fade_out|path, shape, dir, dur, delay, dx, dy)  (dx, dy en pulgadas para path)."""
    ANIM_LOG.append((slide, clicks))
    n = [2]
    def nid(): n[0] += 1; return n[0]
    animados = {}

    def visibilidad(spid, valor, retraso):
        return (f'<p:set><p:cBhvr><p:cTn id="{nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="{retraso}"/></p:stCondLst></p:cTn>'
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
                f'<p:to><p:strVal val="{valor}"/></p:to></p:set>')

    def efecto(e, tipo_nodo):
        sh = e["shape"]; spid = sh.shape_id; k = e["kind"]; dur = e.get("dur", 600); retraso = e.get("delay", 0)
        es_img = sh.shape_type == MSO_SHAPE_TYPE.PICTURE
        if not es_img: animados[spid] = sh
        grp = "" if es_img else ' grpId="0"'
        pid = nid()
        if k in ("wipe", "fade", "wipe_out", "fade_out"):
            sale = k.endswith("_out"); base = k.replace("_out", "")
            preset = 22 if base == "wipe" else 10
            sub, filtro = WIPE[e.get("dir", "l")] if base == "wipe" else (0, "fade")
            cuerpo = (visibilidad(spid, "visible", 0) if not sale else "")
            cuerpo += (f'<p:animEffect transition="{"out" if sale else "in"}" filter="{filtro}"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}"/>'
                       f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>')
            cuerpo += (visibilidad(spid, "hidden", dur - 1) if sale else "")
            clase = "exit" if sale else "entr"
        else:  # trayectoria
            dx, dy = e["dx"] / SW, e["dy"] / SH; preset, sub, clase = 0, 0, "path"
            cuerpo = (f'<p:animMotion origin="layout" path="M 0 0 L {dx:.5f} {dy:.5f} E" pathEditMode="relative" rAng="0" ptsTypes="AA">'
                      f'<p:cBhvr><p:cTn id="{nid()}" dur="{dur}" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
                      f'<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr>'
                      f'<p:rCtr x="{dx / 2:.5f}" y="{dy / 2:.5f}"/></p:animMotion>')
        return (f'<p:par><p:cTn id="{pid}" presetID="{preset}" presetClass="{clase}" presetSubtype="{sub}" fill="hold"{grp} nodeType="{tipo_nodo}">'
                f'<p:stCondLst><p:cond delay="{retraso}"/></p:stCondLst><p:childTnLst>{cuerpo}</p:childTnLst></p:cTn></p:par>')

    grupos = []
    for clic in clicks:
        externo, interno = nid(), nid()
        efs = "".join(efecto(e, "clickEffect" if j == 0 else "withEffect") for j, e in enumerate(clic))
        grupos.append(f'<p:par><p:cTn id="{externo}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
                      f'<p:par><p:cTn id="{interno}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{efs}</p:childTnLst></p:cTn></p:par>'
                      f'</p:childTnLst></p:cTn></p:par>')
    def bldp(i, sh):
        anim_bg = "" if sh.shape_type == MSO_SHAPE_TYPE.TEXT_BOX else ' animBg="1"'
        return '<p:bldP spid="%d" grpId="0"%s/>' % (i, anim_bg)
    bld = "".join(bldp(i, sh) for i, sh in animados.items())
    bld_xml = ('<p:bldLst>' + bld + '</p:bldLst>') if bld else ''
    xml = (f'<p:timing xmlns:p="{NS}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
           f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{"".join(grupos)}</p:childTnLst></p:cTn>'
           f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           f'</p:childTnLst></p:cTn></p:par></p:tnLst>{bld_xml}</p:timing>')
    slide._element.append(parse_xml(xml))

def transicion(slide, interno):
    el = parse_xml(f'<p:transition xmlns:p="{NS}" spd="med">{interno}</p:transition>')
    t = slide._element.find(f"{{{NS}}}timing")
    if t is not None: t.addprevious(el)
    else: slide._element.append(el)

def nueva(color=BLANCO):
    s = prs.slides.add_slide(VACIA); fondo(s, color); return s

# ====================== 1. PORTADA ======================
s = nueva(MARRON)
forma(s, MSO_SHAPE.RECTANGLE, 8.6, 0, 4.733, SH, RGBColor(0x5A, 0x34, 0x20))
logo = imagen(s, r"D:\PruebasTareas\ihm_pa2\img\last_0.png", 9.1, 0.5, 3.7, 1.2, "Logo de la Universidad Tecnológica del Perú")
t1 = texto(s, 0.8, 1.9, 7.6, 1.4, "MercaTab", 64, True, BLANCO, TITULO)
t2 = texto(s, 0.8, 3.3, 7.6, 1.0, "PA3 · Código accesible y validación final", 26, False, DURAZNO)
t3 = texto(s, 0.8, 4.6, 7.6, 1.4, ["Guerrero Mirez, Diego", "Salvador Silva, Lindel"], 22, False, BLANCO)
t4 = texto(s, 9.1, 3.3, 3.7, 1.8, ["Interacción", "Hombre-Máquina", "Docente: Davila Hurtado, Luis Alberto"], 18, False, BLANCO)
animar(s, [[dict(kind="wipe", shape=t1, dir="l", dur=800), dict(kind="wipe", shape=t2, dir="l", dur=700, delay=400),
            dict(kind="fade", shape=t3, dur=800, delay=900), dict(kind="fade", shape=t4, dur=800, delay=1200)]])
transicion(s, "<p:fade/>")
notas(s, "Presentar el sistema, el curso y quién expone cada parte. El sistema está publicado en xyzccords.github.io/mercatab/app/.")

# ====================== 2. DEL FIGMA AL CÓDIGO ======================
s = nueva()
titulo(s, "Del Figma al código: el mismo diseño, corregido con lo que mostró la prueba")
comp = {}
for n, alt in (("ganancias", "Ganancias: Figma junto a la pantalla programada"), ("productos", "Productos: Figma junto a la pantalla programada"),
               ("inicio", "Inicio: Figma junto a la pantalla programada")):   # el último queda arriba; el panel tapa a todos
    comp[n] = imagen(s, IM("comparacion", n + ".png"), 0.6, 1.6, 4.5, 4.9, alt)
panel = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.4, 1.4, 4.8, 5.3, MARRON, None, 0.04)
k1 = texto(s, 0.8, 1.9, 4.0, 1.3, ["Botón verde → contorno", "Ícono propio de caja"], 24, True, BLANCO, TITULO)
k2 = texto(s, 0.8, 3.4, 4.0, 1.3, ["Editar y eliminar", "de 44 px, separados"], 24, True, BLANCO, TITULO)
k3 = texto(s, 0.8, 4.9, 4.0, 1.3, ["Valores sobre las barras", "y tabla alternativa"], 24, True, BLANCO, TITULO)
x_final = 7.3; dx = x_final - 0.6
animar(s, [
    [dict(kind="path", shape=comp["inicio"], dx=dx, dy=0, dur=1000), dict(kind="fade", shape=k1, dur=700, delay=500)],
    [dict(kind="path", shape=comp["inicio"], dx=-dx, dy=0, dur=800), dict(kind="path", shape=comp["productos"], dx=dx, dy=0, dur=1000, delay=300),
     dict(kind="fade", shape=k2, dur=700, delay=600)],
    [dict(kind="path", shape=comp["productos"], dx=-dx, dy=0, dur=800), dict(kind="path", shape=comp["ganancias"], dx=dx, dy=0, dur=1000, delay=300),
     dict(kind="fade", shape=k3, dur=700, delay=600)]])
transicion(s, '<p:wipe dir="r"/>')
notas(s, "Cada imagen sale de detrás del panel: izquierda es el Figma del PA2, derecha el sistema real. Tres clics: Inicio, Productos y Ganancias. Cada cambio sale de un hallazgo: el verde no pasaba contraste, el ícono se repetía con Ventas, los íconos de editar y eliminar estaban juntos y el gráfico no tenía valores.")

# ====================== 3. ACCESIBILIDAD ======================
s = nueva()
titulo(s, "Se aplicaron los 11 criterios WCAG de la guía, no solo 8")
forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.4, 1.5, 3.2, 5.2, MARRON, None, 0.05)
big = texto(s, 0.4, 2.2, 3.2, 1.6, "11/11", 64, True, BLANCO, TITULO, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
sub = texto(s, 0.7, 4.0, 2.6, 1.6, "criterios con código y evidencia", 20, False, DURAZNO, CUERPO, PP_ALIGN.CENTER)
cajas = [("04", "Foco visible", 3.85, 1.5), ("09", "Skip link", 6.95, 1.5), ("05", "ARIA labels", 10.05, 1.5),
         ("06", "Táctil de 44 px", 3.85, 4.1), ("11", "Texto de 14 px", 6.95, 4.1)]
fotos = []; rotulos = []
for n, nombre, x, y in cajas:
    forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, 2.95, 2.5, CREMA, None, 0.05)
    fotos.append(imagen(s, IM("codigo_ppt", n + ".png"), x + 0.08, y + 0.08, 2.79, 1.95, f"Fragmento de código: {nombre}"))
    rotulos.append(texto(s, x + 0.08, y + 2.08, 2.79, 0.4, nombre, 15, True, MARRON, alin=PP_ALIGN.CENTER))
animar(s, [
    [dict(kind="wipe", shape=big, dir="l", dur=600), dict(kind="fade", shape=sub, dur=600, delay=300)] +
    [dict(kind="wipe", shape=fotos[i], dir="d", dur=600, delay=500 + i * 250) for i in range(3)] +
    [dict(kind="fade", shape=rotulos[i], dur=500, delay=700 + i * 250) for i in range(3)],
    [dict(kind="wipe", shape=fotos[i], dir="l", dur=600, delay=i * 250) for i in (3, 4)] +
    [dict(kind="fade", shape=rotulos[i], dur=500, delay=200 + (i - 3) * 250) for i in (3, 4)]])
transicion(s, '<p:push dir="u"/>')
notas(s, "Los otros seis criterios (alt text, contraste, teclado, errores con texto, labels con autocomplete y estructura semántica) están en el informe con su código. Estar listos para explicar cualquier línea en vivo.")

# ====================== 4. AXE ======================
s = nueva()
titulo(s, "axe-core no encontró violaciones en 10 pantallas del sistema")
axe = imagen(s, IM("axe", "informe_axe.png"), 0.5, 1.5, 7.7, 4.9, "Informe de axe-core con cero violaciones en diez pantallas")
stats = []
for i, (g, t) in enumerate([("18 / 18", "pares de color ≥ 4,5:1"), ("0", "elementos táctiles < 44 px"), ("14 px", "texto más pequeño")]):
    stats.append((texto(s, 8.6, 1.5 + i * 1.5, 4.2, 0.9, g, 40, True, MARRON, TITULO), texto(s, 8.6, 2.35 + i * 1.5, 4.2, 0.5, t, 18, False, GRIS)))
chip_pendiente(s, 8.6, 6.1, 4.2, 0.7, "Captura con la extensión axe/WAVE: pendiente")
animar(s, [[dict(kind="wipe", shape=axe, dir="l", dur=900)],
           [dict(kind="wipe", shape=a, dir="d", dur=500, delay=i * 350) for i, (a, b) in enumerate(stats)] +
           [dict(kind="fade", shape=b, dur=500, delay=250 + i * 350) for i, (a, b) in enumerate(stats)]])
transicion(s, "<p:fade/>")
notas(s, "El informe se generó con axe-core 4.10.2, el motor de axe DevTools, sobre el sistema publicado. Falta repetirlo con la extensión en Chrome (axe DevTools o WAVE) en 3 pantallas y pegar la captura aquí.")

# ====================== 5. PRUEBA CON USUARIOS ======================
s = nueva()
titulo(s, "Tres personas completaron la tarea sin ayuda, una con discapacidad auditiva")
u1 = imagen(s, IM("prueba", "U1.png"), 0.8, 1.6, 2.5, 3.9, "Celular de la participante U1 mostrando la pantalla de ganancias")
u2 = imagen(s, IM("prueba", "U2.png"), 0.8, 1.6, 2.5, 3.9, "Pantalla de ganancias durante la prueba de U2")
u3 = imagen(s, IM("prueba", "U3.png"), 0.8, 1.6, 2.5, 3.9, "Diálogo de venta registrada durante la prueba de U3")
forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.4, 1.4, 4.0, 5.4, MARRON, None, 0.04)
texto(s, 0.7, 1.55, 3.4, 0.9, "100 %", 44, True, BLANCO, TITULO); texto(s, 0.7, 2.4, 3.4, 0.4, "efectividad: 3 de 3 personas", 16, False, DURAZNO)
texto(s, 0.7, 3.0, 3.4, 0.9, "≈ 23 s", 44, True, BLANCO, TITULO); texto(s, 0.7, 3.85, 3.4, 0.7, "por tarea (KLM estimado: 14,4 s)", 16, False, DURAZNO)
texto(s, 0.7, 4.65, 3.4, 0.9, "1 duda", 44, True, BLANCO, TITULO); texto(s, 0.7, 5.5, 3.4, 0.4, "observada en las 3 sesiones", 16, False, DURAZNO)
chip_pendiente(s, 0.7, 6.1, 3.4, 0.55, "SUS: pendiente de datos")
xs = [4.9, 7.65, 10.4]; casos = [("U1 · 40 años", "celular", "≈ 20 s"), ("U2 · 22 años", "discapacidad auditiva", "≈ 27 s"), ("U3 · 22 años", "bodega propia", "≈ 22 s")]
caps = []
for (a, b, c), x in zip(casos, xs):
    caps.append(texto(s, x, 5.6, 2.6, 1.2, [a, b, c], 16, True, MARRON, alin=PP_ALIGN.CENTER))
dxs = [x - 0.75 for x in xs]
animar(s, [[dict(kind="path", shape=u1, dx=dxs[0], dy=0, dur=1000), dict(kind="fade", shape=caps[0], dur=600, delay=600)],
           [dict(kind="path", shape=u2, dx=dxs[1], dy=0, dur=1000), dict(kind="fade", shape=caps[1], dur=600, delay=600)],
           [dict(kind="path", shape=u3, dx=dxs[2], dy=0, dur=1000), dict(kind="fade", shape=caps[2], dur=600, delay=600)]])
transicion(s, '<p:cover dir="l"/>')
notas(s, "Tiempos medidos en los videos desde “empiece” hasta que aparece la ganancia (aprox. ±2 s): U1 20 s, U2 27 s, U3 22 s. U1 usó un celular real; U2 y U3 la computadora. U2 tiene discapacidad auditiva real: no se encontraron barreras en el sistema (no usa sonido); la barrera fue del protocolo, porque la tarea se dio también por escrito. Única duda: U2 fue primero a Ventas a registrar y luego encontró Nueva venta. El SUS se completa cuando estén las respuestas.")

# ====================== 6. HALLAZGOS ======================
s = nueva()
titulo(s, "Tres barreras del código real, resueltas")
datos = [("2,83 → 6,31:1", "Contraste del botón verde del Figma", "Botón de contorno marrón"),
         ("20 → 44 px", "Enlaces dentro de frases", "Área táctil de 44 px"),
         ("362 → 320 px", "Ventas con scroll horizontal", "Filtros que se adaptan al ancho")]
filas = []
for i, (cifra, mal, bien) in enumerate(datos):
    y = 1.6 + i * 1.75
    fondo_f = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.6, y, 12.1, 1.5, CREMA, None, 0.06)
    c = texto(s, 0.9, y, 4.6, 1.5, cifra, 36, True, MARRON, TITULO, ancla=MSO_ANCHOR.MIDDLE)
    a = texto(s, 5.6, y + 0.25, 7.0, 0.5, mal, 22, True, OSCURO); b = texto(s, 5.6, y + 0.8, 7.0, 0.5, "→ " + bien, 22, False, GRIS)
    filas.append((fondo_f, c, a, b))
animar(s, [[dict(kind="wipe", shape=f, dir="l", dur=700), dict(kind="fade", shape=c, dur=600, delay=300), dict(kind="fade", shape=a, dur=600, delay=450),
            dict(kind="fade", shape=b, dur=600, delay=700)] for f, c, a, b in filas])
transicion(s, '<p:wipe dir="l"/>')
notas(s, "Los tres salieron de medir el sistema, no de mirarlo. axe no marcó los dos últimos: los encontraron las mediciones propias de tamaño táctil y la prueba de reflow a 320 px.")

# ====================== 7. DEMO ======================
s = nueva(OSCURO)
titulo(s, "Demo: registrar una venta con factura, solo con teclado", BLANCO)
fones = []
for i, (n, alt) in enumerate([("inicio", "Pantalla de inicio"), ("venta_factura", "Venta con factura y consulta de SUNAT"), ("comprobante", "Comprobante emitido")]):
    fones.append(imagen(s, IM("pantallas", n + ".png"), 0.7 + i * 3.4, 1.5, 3.1, 4.7, alt))
chips = []
for i, t in enumerate(["Tab", "Enter", "Esc"]):
    f = forma(s, MSO_SHAPE.ROUNDED_RECTANGLE, 11.0, 1.7 + i * 1.2, 1.7, 0.9, DURAZNO, None, 0.2)
    tx = texto(s, 11.0, 1.7 + i * 1.2, 1.7, 0.9, t, 24, True, OSCURO, TITULO, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE); chips.append((f, tx))
url = texto(s, 0.7, 6.4, 12, 0.5, "xyzccords.github.io/mercatab/app", 20, True, DURAZNO)
animar(s, [[dict(kind="wipe", shape=fones[0], dir="l", dur=700)], [dict(kind="wipe", shape=fones[1], dir="l", dur=700)],
           [dict(kind="wipe", shape=fones[2], dir="l", dur=700)] + [dict(kind="fade", shape=x, dur=500, delay=200 + i * 250) for i, c in enumerate(chips) for x in c] +
           [dict(kind="fade", shape=url, dur=600, delay=1000)]])
transicion(s, '<p:push dir="u"/>')
notas(s, "Abrir el sistema publicado y no usar el mouse: skip link con el primer Tab, Registrar venta, producto y cantidad, factura, RUC de ejemplo, Consultar SUNAT, Guardar, ver comprobante, Ganancias. Luego simular sin conexión desde Perfil. Hay un video de 3 minutos con este recorrido.")

# ====================== 8. CICLO DCU ======================
s = nueva()
titulo(s, "El ciclo se cerró: de un cuaderno a un sistema accesible")
pasos = [("Problema", "Cuaderno y errores"), ("PA1", "Perfiles y GOMS"), ("PA2", "Figma · 12 errores"), ("PA3", "Código · 11 criterios · 3 pruebas")]
cheva = []
for i, (a, b) in enumerate(pasos):
    x = 0.5 + i * 3.15; ult = i == len(pasos) - 1
    f = forma(s, MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON, x, 2.4, 3.3, 1.6, DURAZNO if ult else MARRON)
    t = texto(s, x + 0.55, 2.4, 2.2, 1.6, a, 26, True, OSCURO if ult else BLANCO, TITULO, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    d = texto(s, x + 0.2, 4.2, 2.9, 1.0, b, 16, False, GRIS, alin=PP_ALIGN.CENTER); cheva.append((f, t, d))
frase = texto(s, 0.6, 5.7, 12.1, 0.7, "Probar → detectar → corregir → volver a probar", 28, True, MARRON, TITULO, PP_ALIGN.CENTER)
animar(s, [[dict(kind="wipe", shape=x, dir="l", dur=600, delay=i * 450) for i, c in enumerate(cheva) for x in c[:2]] +
           [dict(kind="fade", shape=c[2], dur=500, delay=300 + i * 450) for i, c in enumerate(cheva)],
           [dict(kind="wipe", shape=frase, dir="l", dur=800)]])
transicion(s, "<p:fade/>")
notas(s, "Cada flecha tiene evidencia en el informe. El PA3 cerró con tres personas: dos comunes y una con discapacidad auditiva.")

# ====================== 9. REFLEXIÓN ======================
s = nueva(MARRON)
fr = texto(s, 0.9, 2.0, 11.5, 2.8, "MercaTab ya funciona sin internet y sin mouse, y tres personas lo usaron sin ayuda.", 40, True, BLANCO, TITULO, ancla=MSO_ANCHOR.MIDDLE)
pie = texto(s, 0.9, 6.2, 11.5, 0.5, "xyzccords.github.io/mercatab/app", 20, True, DURAZNO)
animar(s, [[dict(kind="wipe", shape=fr, dir="l", dur=1200), dict(kind="fade", shape=pie, dur=800, delay=1000)]])
transicion(s, '<p:wipe dir="r"/>')
notas(s, "Una sola frase de impacto. Falta probarlo con un bodeguero mayor en un celular real, que es el siguiente paso.")

prs.save(OUT); print("OK", OUT, len(prs.slides._sldIdLst), "diapositivas")

# Copia de depuración: sin animaciones y con las trayectorias ya aplicadas, para revisar el estado final de cada diapositiva
import sys
if len(sys.argv) > 1:
    for sl, cl in ANIM_LOG:
        for clic in cl:
            for e in clic:
                if e["kind"] == "path":
                    e["shape"].left += Inches(e["dx"]); e["shape"].top += Inches(e["dy"])
        t = sl._element.find("{%s}timing" % NS)
        if t is not None: sl._element.remove(t)
    prs.save(sys.argv[1]); print("copia final:", sys.argv[1])
