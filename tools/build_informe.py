# -*- coding: utf-8 -*-
"""Genera el informe Word del PA3. [[texto]] = pendiente (resaltado amarillo); **texto** = negrita."""
import os, re, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image

RAIZ = r"D:\PruebasTareas\ihm_pa3"
EV = os.path.join(RAIZ, "evidencia")
OUT = os.path.join(RAIZ, "PA3_IHM_Guerrero_Salvador.docx")
BROWN = "6B3F26"
APP = "MercaTab"
REPO = "https://github.com/Xyzccords/mercatab"
SITIO = "https://xyzccords.github.io/mercatab/app/"
TEAM = [("Guerrero Mirez, Diego", "U22300281"), ("Salvador Silva, Lindel", "U22205904")]

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, m, Cm(2.5))

def fuente(estilo, tam, negrita=None, color=None):
    estilo.font.name = "Arial"; estilo.font.size = Pt(tam)
    rpr = estilo.element.get_or_add_rPr(); rf = rpr.find(qn("w:rFonts"))
    if rf is None: rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(a), "Arial")
    if negrita is not None: estilo.font.bold = negrita
    if color: estilo.font.color.rgb = RGBColor.from_string(color)

n = doc.styles["Normal"]; fuente(n, 12); n.paragraph_format.line_spacing = 1.5; n.paragraph_format.space_after = Pt(6)
for nombre, tam in (("Heading 1", 14), ("Heading 2", 12), ("Heading 3", 12)):
    h = doc.styles[nombre]; fuente(h, tam, True, BROWN if nombre != "Heading 3" else "000000")
    h.paragraph_format.space_before = Pt(14 if nombre == "Heading 1" else 10); h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True; h.paragraph_format.line_spacing = 1.5
doc.styles["Heading 3"].font.italic = True

def runs(par, texto, tam=None, negrita=None, cursiva=None, color=None):
    for parte in re.split(r"(\[\[.*?\]\]|\{\{.*?\}\}|\*\*.*?\*\*)", texto):
        if not parte: continue
        if parte.startswith("{{"):
            r = par.add_run("[" + (parte[2:-2].strip() or "   ") + "]"); r.font.highlight_color = WD_COLOR_INDEX.YELLOW; r.bold = True
        elif parte.startswith("[["):
            r = par.add_run("[PENDIENTE: " + parte[2:-2] + "]"); r.font.highlight_color = WD_COLOR_INDEX.YELLOW; r.bold = True
        elif parte.startswith("**"):
            r = par.add_run(parte[2:-2]); r.bold = True
        else:
            r = par.add_run(parte)
            if negrita: r.bold = True
        if cursiva: r.italic = True
        if tam: r.font.size = Pt(tam)
        if color and not parte.startswith("[["): r.font.color.rgb = RGBColor.from_string(color)
    return par

def P(texto, alinear=None, tam=None, negrita=None, cursiva=None, despues=None, mantener=False):
    p = doc.add_paragraph(); runs(p, texto, tam, negrita, cursiva)
    if alinear == "c": p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif alinear == "j": p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if despues is not None: p.paragraph_format.space_after = Pt(despues)
    if mantener: p.paragraph_format.keep_with_next = True
    return p

def H(texto, nivel=1): return doc.add_heading(texto, level=nivel)

def vineta(texto):
    p = doc.add_paragraph(style="List Bullet"); runs(p, texto)
    p.paragraph_format.line_spacing = 1.5; p.paragraph_format.space_after = Pt(2)

def enlace(par, url, tam=None):
    rid = doc.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    h = OxmlElement("w:hyperlink"); h.set(qn("r:id"), rid)
    r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "0563C1"); rpr.append(c)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rpr.append(u)
    if tam: sz = OxmlElement("w:sz"); sz.set(qn("w:val"), str(int(tam * 2))); rpr.append(sz)
    r.append(rpr); t = OxmlElement("w:t"); t.text = url; r.append(t); h.append(r); par._p.append(h)

def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr(); s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), color); tcPr.append(s)

def ajustar(path, ancho, alto=None):
    iw, ih = Image.open(path).size; h = ancho * ih / iw
    if alto and h > alto: h = alto; ancho = h * iw / ih
    return Cm(ancho), Cm(h)

def llenar(celda, contenido, tam=10, negrita=False, color=None, centro=False):
    celda.text = ""; p = celda.paragraphs[0]; p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(0)
    if centro: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if isinstance(contenido, tuple):
        _, ruta, ancho, *r = contenido; w, h = ajustar(ruta, ancho, r[0] if r else None)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(ruta, width=w, height=h); return
    for i, linea in enumerate(str(contenido).split("\n")):
        if i: p = celda.add_paragraph(); p.paragraph_format.line_spacing = 1.15; p.paragraph_format.space_after = Pt(0)
        runs(p, linea, tam, negrita, color=color)

def tabla(filas, anchos, tam=10, centradas=()):
    t = doc.add_table(rows=len(filas), cols=len(anchos)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    m = OxmlElement("w:tblCellMar")
    for k, v in (("top", 40), ("left", 70), ("bottom", 40), ("right", 70)):
        e = OxmlElement(f"w:{k}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa"); m.append(e)
    t._tbl.tblPr.append(m)
    for j, w in enumerate(anchos): t.columns[j].width = Cm(w)
    for i, fila in enumerate(filas):
        for j, v in enumerate(fila):
            c = t.cell(i, j); c.width = Cm(anchos[j])
            if i == 0: llenar(c, v, tam, True, "FFFFFF", True); sombrear(c, BROWN)
            else: llenar(c, v, tam, centro=j in centradas)
        trPr = t.rows[i]._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); trPr.append(cs)
        if i == 0: th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def figura(ruta, ancho, pie, alto=None):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True; p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
    w, h = ajustar(ruta, ancho, alto); p.add_run().add_picture(ruta, width=w, height=h)
    c = P(pie, "c", 10, cursiva=True, despues=8); c.paragraph_format.line_spacing = 1.0

def fila_imagenes(items, ancho, alto):
    t = doc.add_table(rows=2, cols=len(items)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for j, (ruta, pie) in enumerate(items):
        c = t.cell(0, j); c.width = Cm(16 / len(items)); llenar(c, ("img", ruta, ancho, alto))
        l = t.cell(1, j); l.width = Cm(16 / len(items)); llenar(l, pie, 9, centro=True)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def salto(): doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def numero_pagina(seccion):
    fp = seccion.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r0 = fp.add_run(f"{APP} · PA3 · pág. "); r0.font.size = Pt(10)
    r = fp.add_run(); r.font.size = Pt(10)
    for tipo, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo: e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tipo)
        else: e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt
        r._r.append(e)

IM = lambda *rutas: os.path.join(EV, *rutas)
resumen_axe = json.load(open(IM("axe", "resumen.json"), encoding="utf-8"))
flujos = [l[6:].strip() for l in open(IM("flujos.txt"), encoding="utf-8").read().split("\n") if l.startswith("OK ")]
contraste = [l for l in open(IM("contraste.txt"), encoding="utf-8").read().split("\n") if l[:2] in ("OK", "FA")]

# ============ PORTADA ============
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(r"D:\PruebasTareas\ihm_pa2\img\last_0.png", width=Cm(7))
P("AVANCE DE PROYECTO FINAL 3 (PA3)", "c", 20, True, despues=0)
P("Implementación accesible y validación final", "c", 14, despues=14)
P(APP, "c", 22, True, despues=14)
P("**Curso:** Interacción Hombre-Máquina", "c", despues=0)
P("**Docente:** Davila Hurtado, Luis Alberto", "c", despues=10)
P("**Integrantes**", "c", despues=0)
for nombre, cod in TEAM: P(f"{nombre} ({cod})", "c", despues=0)
P("", despues=6)
q = P("**Repositorio:** ", "c", 11, despues=0); enlace(q, REPO, 10)
q = P("**Despliegue:** ", "c", 11, despues=0); enlace(q, SITIO, 10)
P("2026", "c", 14, True)
salto()

H("Índice")
for it in ["1. Portada e índice", "2. Resumen del PA1 y PA2", "3. Sistema implementado", "4. Accesibilidad implementada",
           "5. Evaluación con axe-core", "6. Validación con usuarios", "7. Conclusiones DCU", "8. Anexos"]:
    P(it, despues=0)
salto()
numero_pagina(sec)

# ============ 2. RESUMEN PA1 Y PA2 ============
H("2. Resumen del PA1 y PA2")
H("2.1 Problema, perfiles y tarea", 2)
P("Los dueños de bodegas y puestos de abarrotes del mercado del pueblo de Chiclayo siguen anotando sus ventas en un cuaderno. "
  "Eso produce errores de cálculo, hojas perdidas y ninguna idea clara de cuánto se ganó al cierre del día. Las aplicaciones de "
  "gestión que existen suelen exigir internet constante, algo que no encaja con datos móviles limitados.", "j")
P("El PA1 definió dos perfiles. **Don Teo**, bodeguero de 64 años con artritis leve, pocos datos móviles y miedo a borrar registros por error. "
  "**Jimena**, emprendedora de 28 años que atiende un puesto de abarrotes, hace varias cosas a la vez y trabaja bajo luz solar. La tarea del GOMS fue "
  "**registrar la venta de un producto y ver la ganancia**, con un método principal desde Inicio y otro desde Ventas.", "j")
H("2.2 Resultados del PA2", 2)
P("En el PA2 se construyó el prototipo de alta fidelidad en Figma y se probó con tres personas del rubro de abarrotes (20, 32 y 49 años). "
  "Los tiempos corresponden a la duración de cada sesión grabada, con pausas y comentarios en voz alta.", "j")
tabla([["Métrica PA2", "Resultado"],
       ["Efectividad", "100 % (3 de 3 usuarios completaron los 5 pasos)"],
       ["Duración de la sesión", "41 s, 53 s y 35 s (promedio 43 s); KLM estimado 14,4 s"],
       ["Satisfacción (SUS)", "95, 90 y 97,5 (promedio 94,2)"],
       ["Errores y dudas registrados", "12 (3 de U1, 4 de U2, 5 de U3)"]], [5.2, 10.8])
P("Los hallazgos que más pesaron en este avance: el menú no indicaba la sección activa, los dos botones principales de Inicio tenían el mismo peso, "
  "el ícono de Registrar venta era el mismo que el de la pestaña Ventas, los íconos de editar y eliminar eran pequeños y estaban juntos, y el gráfico de "
  "ganancias no mostraba valores. Cada uno se atendió en el código (sección 3.4).", "j")

# ============ 3. SISTEMA IMPLEMENTADO ============
H("3. Sistema implementado")
H("3.1 Tecnología y estructura", 2)
P("El sistema es una aplicación web de una sola página escrita en HTML, CSS y JavaScript sin frameworks ni dependencias. Los datos se guardan en el "
  "navegador (localStorage), así que funciona sin servidor y sin internet, y un service worker guarda los archivos para abrirla sin conexión. "
  "Como el curso es solo frontend, no hay base de datos ni API: se eligió esta base para poder explicar cada archivo y abrir la aplicación con "
  "doble clic sobre index.html.", "j")
tabla([["Archivo", "Responsabilidad"],
       ["index.html", "Estructura semántica (cabecera, navegación, contenido principal, pie), skip link y diálogo modal"],
       ["css/estilos.css", "Paleta, tipografía, foco visible, tamaños táctiles y diseño responsive"],
       ["js/app.js", "Rutas con hash, barra de navegación, estado de red y aviso de cambios sin guardar"],
       ["js/vistas.js", "Todas las pantallas y sus formularios, con validación"],
       ["js/datos.js", "Productos, ventas, ganancias y respaldo en localStorage"],
       ["js/sunat.js", "Conexión con SUNAT simulada: RUC, DNI, boleta y factura"],
       ["js/ui.js, js/iconos.js", "Diálogos, avisos, campos de formulario con error e iconos"],
       ["sw.js", "Service worker para uso sin conexión"]], [4.2, 11.8], 10)
P("Nota sobre el desarrollo: el código se escribió con apoyo de IA generativa (Claude, de Anthropic). Las decisiones de accesibilidad se justifican en la "
  "sección 4 y la guía de código incluida en el repositorio describe cada archivo y función.", "j", 11, cursiva=True)

H("3.2 Pantallas", 2)
P("Se programaron las pantallas del Figma del PA2 (Inicio, Productos, Agregar y editar producto, Ventas, Agregar venta, Ganancias, Perfil, Iniciar sesión, "
  "Crear cuenta y los diálogos de confirmación, error y sin conexión) y se agregó el módulo de comprobantes.", "j")
fila_imagenes([(IM("pantallas", "inicio.png"), "Inicio"), (IM("pantallas", "productos.png"), "Productos"), (IM("pantallas", "ganancias.png"), "Ganancias")], 4.6, 9.8)
figura(IM("pantallas", "perfil.png"), 4.6, "Figura 1. Pantallas del sistema real. Debajo, Perfil con la opción de simular la falta de conexión.", 9.8)

H("3.3 Conexión con SUNAT (simulada)", 2)
P("La corrección de la docente pide que el sistema se conecte con SUNAT. Como el curso es solo frontend, la conexión se **simula** y se aísla en un solo archivo "
  "(js/sunat.js): si más adelante hubiera un servicio real, solo cambiaría ese archivo. Lo que sí funciona de verdad en el navegador:", "j")
for t in ["**Validación del RUC** con el dígito verificador de SUNAT (módulo 11), el mismo algoritmo real.",
          "**Consulta de RUC y DNI** contra un padrón de ejemplo con contribuyentes ficticios; muestra razón social, estado y condición.",
          "**Boleta y factura electrónicas** con serie y correlativo (B001, F001), base imponible e IGV de 18 %. La factura exige RUC válido y la boleta pide DNI desde S/ 700.",
          "**Sin conexión**, el comprobante queda *pendiente de envío* y pasa a *aceptado* cuando vuelve internet.",
          ]: vineta(t)
P("Los comprobantes se muestran como representación simulada y no tienen validez tributaria: no hay firma digital ni proveedor autorizado.", "j")
fila_imagenes([(IM("pantallas", "venta_factura.png"), "Factura con consulta SUNAT"), (IM("pantallas", "comprobante.png"), "Comprobante emitido")], 5.6, 11.5)

H("3.4 Del Figma al código", 2)
P("El diseño visual se mantuvo. Los cambios respecto al Figma responden a los hallazgos del PA2 y a la revisión de accesibilidad.", "j")
for c in ["inicio", "productos", "ganancias"]:
    pass
figura(IM("comparacion", "inicio.png"), 11.5, "Figura 2. Inicio: Figma del PA2 (izquierda) y sistema real (derecha).", 10.5)
tabla([["Cambio", "Motivo"],
       ["“Agregar productos” pasó de verde a botón con contorno marrón", "El texto blanco sobre el verde del Figma daba 2,83:1; ahora cumple y además se distingue de la acción principal"],
       ["“Registrar venta” usa el ícono de caja registradora", "Era el mismo recibo de la pestaña Ventas y U3 lo dudó"],
       ["Valores sobre las barras y tabla alternativa en Ganancias", "U1 dijo que no entendía las barras; el mapa de atención mostró que el gráfico pasaba desapercibido"],
       ["Editar y eliminar en botones de 44 px separados 8 px", "U1 señaló que estaban muy juntos; el riesgo mayor es para Don Teo"],
       ["Ayudas bajo Precio por unidad e Inversión total", "U3 dudó entre ambos campos"],
       ["Campo de cantidad con etiqueta completa y en su propia fila", "U2 dijo que le costaba ver dónde poner la cantidad"],
       ["Aviso “Sin conexión · Guardado en tu celular” y diálogo con texto de respaldo", "El PA2 decía “se perdió la conexión”, que contradice una app que funciona sin internet"]], [6.6, 9.4], 9.5)

H("3.5 Modo sin conexión y respaldo", 2)
P("Registrar ventas, ver productos, stock y ganancias no depende de internet. Internet se usa para dos cosas: enviar comprobantes a SUNAT y el respaldo en la nube "
  "de la membresía Premium (simulada, sin cobro y con precio por definir). En Perfil hay un interruptor para simular la falta de conexión durante las demostraciones.", "j")
figura(IM("pantallas", "inicio_sin_conexion.png"), 4.6, "Figura 3. Aviso de modo sin conexión en Inicio.", 9.8)

H("3.6 Enlaces y ejecución", 2)
q = P("**Repositorio:** ", "j"); enlace(q, REPO, 11)
q = P("**Sitio publicado:** ", "j"); enlace(q, SITIO, 11)
P("Para ejecutarlo en local basta abrir app/index.html en el navegador. Para el service worker y la instalación como aplicación se necesita servirlo por http, "
  "por ejemplo con python -m http.server dentro de la carpeta app.", "j")

# ============ 4. ACCESIBILIDAD ============
H("4. Accesibilidad implementada")
P("La consigna pide implementar al menos 8 de 11 criterios. Se implementaron los 11. Cada uno indica dónde se aplicó, el fragmento de código y cómo se verificó.", "j")
CRIT = [
 (1, "Alt text descriptivo en todas las imágenes", "1.1.1 (A)", "Fotos de productos en Productos y en el formulario", "axe image-alt: 0 fallos en 10 pantallas; 0 imágenes sin alt"),
 (2, "Contraste de texto mínimo 4.5:1", "1.4.3 (AA)", "Paleta global (variables CSS)", "Cálculo de 18 pares con tools/contraste.py y regla color-contrast de axe"),
 (3, "Navegación completa por teclado", "2.1.1 (A)", "Toda la app: enlaces y botones nativos, diálogo con <dialog>", "Prueba de flujos con teclado: 29 verificaciones correctas"),
 (4, "Foco visible", "2.4.7 (AA)", "Todos los elementos interactivos", "Contorno de 3 px comprobado con Tab; contraste del foco 8,63:1"),
 (5, "ARIA labels en íconos sin texto", "4.1.2 (A)", "Editar, eliminar, volver, mostrar contraseña, quitar producto", "axe button-name y link-name: 0 fallos; 0 botones sin nombre"),
 (6, "Áreas táctiles de 44×44 px", "2.5.5 (AA)", "Botones, enlaces, campos y barra de navegación", "Medición del tamaño de cada elemento: 0 menores de 44 px"),
 (7, "Errores con texto explicativo, no solo color", "1.4.1 (A)", "Formularios de producto, venta, cuenta y negocio", "Formularios enviados vacíos: icono + texto + resumen con foco"),
 (8, "Formularios con labels visibles y autocomplete", "1.3.5 (AA)", "Todos los campos de formulario", "0 campos sin label; 0 sin autocomplete"),
 (9, "Skip link", "2.4.1 (A)", "Primer elemento del documento", "Primer Tab cae en el enlace; Enter lleva el foco al contenido"),
 (10, "Estructura semántica HTML", "1.3.1 (A)", "index.html y cada pantalla", "header, nav, main, footer y un h1 por pantalla; lang=es"),
 (11, "Tipografía mínima de 14 px", "P7 Diseño Universal", "Texto del cuerpo, etiquetas y barra", "Medición de cada texto: mínimo 14 px")]
tabla([["N.º", "Criterio", "WCAG", "Dónde"]] + [[str(c[0]), c[1], c[2], c[3]] for c in CRIT], [1.1, 6.4, 2.6, 5.9], 9.5, centradas=(0,))

NOTAS = {
 1: "Las fotos usan una descripción que dice qué se ve (por ejemplo, “Botella de aceite vegetal de un litro”); las que sube el usuario reciben “Foto de” más el nombre del producto. Los iconos son decorativos y llevan aria-hidden.",
 2: "Todos los pares texto/fondo superan 4,5:1 y los componentes (bordes, barras, foco) superan 3:1. El botón verde del Figma no cumplía y se reemplazó.",
 3: "Se usaron elementos nativos (a, button, select, input, details, dialog), de modo que Tab y Enter funcionan sin código extra. Al cambiar de pantalla el foco pasa al título para que el teclado y el lector de pantalla sepan dónde están, y los diálogos atrapan el foco y se cierran con Esc.",
 4: "Se usa :focus-visible con un contorno azul de 3 px y separación de 2 px, visible tanto sobre el fondo crema como sobre los botones marrón.",
 5: "Los botones de editar, eliminar, volver y mostrar contraseña no tienen texto visible; cada uno lleva un aria-label que nombra la acción y el elemento, como “Editar Azúcar Rubia (1kg)”.",
 6: "Los botones miden al menos 48 px de alto y los de solo ícono 44×44 px, separados 8 px. Los enlaces dentro de frases también se llevaron a 44 px.",
 7: "Cada error aparece como icono, texto que dice qué corregir y cómo, con aria-invalid y aria-describedby en el campo. Además un resumen con role alert recibe el foco y enlaza a cada campo.",
 8: "Cada campo tiene una etiqueta visible, ayuda cuando hace falta y el atributo autocomplete que corresponde: email, current-password, new-password, name y organization; en los campos de datos del negocio se usa off.",
 9: "El primer elemento del DOM es el enlace “Ir al contenido principal”, oculto fuera de pantalla hasta que recibe el foco.",
 10: "Cada pantalla tiene un solo h1, la navegación es un nav con nombre, el contenido está en main y la lengua declarada es español.",
 11: "El cuerpo usa 16 px y el texto más pequeño, como etiquetas de la barra y pie, usa 14 px. La fuente es Atkinson Hyperlegible, diseñada para mejorar la legibilidad.",
}
VISUAL = {
 1: [(IM("pantallas", "productos.png"), "Productos con fotos y texto alternativo", 4.2, 8.5)],
 4: [(IM("pantallas", "foco_boton.png"), "Foco sobre “Registrar venta”", 7.5, 6)],
 7: [(IM("pantallas", "producto_errores.png"), "Producto sin datos", 4.2, 8.5), (IM("pantallas", "login_errores.png"), "Inicio de sesión sin datos", 4.2, 8.5)],
 8: [(IM("pantallas", "registro.png"), "Crear cuenta con etiquetas visibles", 4.2, 8.5)],
 9: [(IM("pantallas", "foco_skip.png"), "Primer Tab: skip link visible", 7.5, 4)],
}
for num, nombre, wcag, donde, verif in CRIT:
    H(f"4.{num} Criterio {num}: {nombre} ({wcag})", 2)
    P(NOTAS[num], "j")
    P(f"**Dónde:** {donde}. **Verificación:** {verif}.", "j", 11)
    figura(IM("codigo", f"{num:02d}.png"), 13, f"Código del criterio {num}.", 9)
    if num in VISUAL:
        its = VISUAL[num]
        if len(its) == 1: figura(its[0][0], its[0][2], f"Evidencia: {its[0][1]}.", its[0][3])
        else: fila_imagenes([(r, t) for r, t, _, _ in its], its[0][2], its[0][3])
    if num == 2:
        tabla([["Resultado", "Par texto / fondo"]] + [[l.split("  ")[0].replace("OK    ", "OK ").strip(), l.split("  ", 1)[1].strip()] for l in contraste], [3.8, 12.2], 9)
    if num == 3:
        P("Verificaciones automáticas de teclado y flujos (Playwright, tools/flujos.py):", None, 11, True, mantener=True)
        tabla([["N.º", "Verificación"]] + [[str(i), t] for i, t in enumerate(flujos, 1)], [1.2, 14.8], 9, centradas=(0,))

# ============ 5. EVALUACIÓN AXE ============
H("5. Evaluación con axe-core")
P("Se ejecutó la extensión WAVE de WebAIM sobre el sitio publicado en 3 pantallas (Inicio, Ventas y Agregar venta): 0 errores de contraste y 0 alertas de contraste, y 1 error de referencia ARIA rota, ya corregido. Además se ejecutó axe-core 4.10.2, el motor que usa la extensión axe DevTools, sobre el sistema real en 10 pantallas, con las reglas WCAG 2.0 y 2.1 de nivel A y AA "
  "más buenas prácticas. El resultado fue de **0 violaciones** en todas. Además se midieron por separado el tamaño táctil, la tipografía, los textos alternativos y las etiquetas.", "j")
figura(IM("axe", "informe_axe.png"), 15, "Figura 4. Informe de axe-core sobre las 10 pantallas del sistema real.", 12)
P("[[Repetir el análisis con la extensión axe DevTools o WAVE en Chrome sobre al menos 3 pantallas y pegar aquí las capturas; este informe se generó con el motor por script]]", "j", 11)
H("5.1 Defectos encontrados y corregidos", 2)
P("axe no marcó fallos en la primera ejecución completa. Los defectos que se corrigieron salieron de las comprobaciones propias y de las pruebas de flujo:", "j")
tabla([["Hallazgo", "Cómo se detectó", "Corrección"],
       ["Dos enlaces dentro de frases (“Regístrate”, “Inicia sesión”) medían 20 px de alto", "Medición de tamaño táctil", "Pasaron a 44 px con display inline-flex"],
       ["La pantalla Ventas desbordaba a 320 px (scroll horizontal)", "Prueba de reflow a 320 y 640 px", "Filtros de fecha con auto-fit y min-width 0"],
       ["Una pantalla heredaba los manejadores de eventos de la anterior y activaba el aviso de cambios sin guardar", "Generación de evidencias: Ganancias mostraba el aviso", "app.js limpia los manejadores al cambiar de pantalla"],
       ["Texto blanco sobre el botón verde del Figma: 2,83:1", "Medición de contraste en el PA2", "Botón de contorno marrón: 6,31:1"],
       ["WAVE marcó 1 error en las 3 pantallas: referencia ARIA rota (el diálogo apuntaba a un título que solo existe cuando está abierto)", "Extensión WAVE sobre el sitio publicado", "aria-labelledby se pone solo mientras el diálogo está abierto; prueba automática que busca referencias rotas en 10 pantallas"],
       ["En Ventas la barra de navegación quedaba después de unos 80 botones: con solo teclado había que pulsar Tab decenas de veces", "Grabación del video demo con teclado", "Lista de 15 ventas con botón «Mostrar 15 más»; la barra se alcanza en menos de 50 pulsaciones (probado)"]], [6.4, 4.8, 4.8], 9.5)
P("Una regla de axe quedó “por revisar a mano” en Ganancias (color-contrast sobre el gráfico). Se verificó con el cálculo propio: texto tinta sobre blanco 15,75:1.", "j", 11)
H("5.2 Pruebas situacionales técnicas", 2)
P("Sin reemplazar la prueba con personas, se comprobó que el sistema funciona **solo con teclado** (sección 4.3), que no hay scroll horizontal a **320 px** ni a **640 px** en 12 pantallas "
  "(equivale a un zoom de 400 % y 200 % en una pantalla de 1280 px) y que el modo **sin conexión** conserva todas las funciones de registro.", "j")
figura(IM("pantallas", "reflow_320.png"), 4.0, "Figura 5. Pantalla Ventas a 320 px de ancho, sin scroll horizontal.", 8.5)

# ============ 6. VALIDACIÓN ============
H("6. Validación con usuarios")
P("Se probó el sistema publicado con tres personas a inicios de noviembre de 2026: dos sin condición de accesibilidad (U1 y U3) y una con discapacidad auditiva real (U2). "
  "Las sesiones se grabaron, con el consentimiento verbal dado al inicio de cada una. Los datos salen de esos videos y de las respuestas que cada participante dio durante la sesión.", "j")
H("6.1 Protocolo", 2)
tabla([["Fase", "Duración", "Qué se hace"],
       ["1. Bienvenida", "2 min", "Se explica que se evalúa el sistema, no a la persona, y se obtiene consentimiento"],
       ["2. Tarea principal", "5-10 min", "Registrar la venta de un producto y ver la ganancia (misma tarea del GOMS), sin ayuda"],
       ["3. Exploración libre", "3-5 min", "El participante navega y comenta lo que observa"],
       ["4. Entrevista", "5 min", "¿Qué fue lo más difícil? ¿Qué cambiarías? ¿Confiarías en este sistema?"],
       ["5. SUS", "2 min", "Cuestionario SUS de 10 preguntas"]], [3.4, 2.2, 10.4], 9.5)
P("U1 usó un celular; U2 y U3 usaron una computadora con Chrome. A U2 la tarea se le dio también por escrito, por su discapacidad auditiva. "
  "En las tres sesiones se pidió pensar en voz alta y el facilitador no ayudó durante la tarea.", "j", 11)
H("6.2 Participantes", 2)
tabla([["Código", "Edad", "Ocupación y relación con los perfiles del PA1", "Contexto y dispositivo"],
       ["U1", "40", "Ama de casa sin negocio propio {{confirmar}}. No coincide con los perfiles del PA1", "Primera vez con el sistema; celular real"],
       ["U2", "22", "Estudiante con un pequeño negocio aparte. Relación parcial con Jimena", "Discapacidad auditiva real; laptop con Chrome"],
       ["U3", "22", "Estudiante de Ingeniería de Sistemas con bodega propia {{confirmar}}. Coincide con Jimena", "Sin condición; computadora con Chrome"]],
      [1.6, 1.4, 8.0, 5.0], 9.5, centradas=(0, 1))
P("No se publican nombres: solo código, edad, ocupación y relación con los perfiles. El consentimiento de U2, con discapacidad real, quedó grabado al inicio de su sesión.", "j", 11)
fila_imagenes([(IM("prueba", "U1.png"), "U1 · celular en mano"), (IM("prueba", "U2.png"), "U2 · pantalla de Ganancias"), (IM("prueba", "U3.png"), "U3 · venta registrada")], 4.3, 8.0)
P("Figura 6. Fotogramas de las sesiones (se recortaron para no mostrar rostros ni nombres).", "c", 10, cursiva=True)
H("6.3 Comparativa PA2 y PA3", 2)
tabla([["Métrica", "PA2 (Figma)", "PA3 (código)", "Observación"],
       ["Efectividad", "100 % (3 de 3)", "100 % (3 de 3)", "Los tres completaron los 5 pasos sin ayuda"],
       ["Eficiencia (tiempo)", "41 s, 53 s y 35 s (sesión completa)", "≈ 20 s, ≈ 27 s y ≈ 22 s (solo la tarea; promedio ≈ 23 s)", "No son comparables directamente. Frente al KLM de 14,4 s: 1,4, 1,9 y 1,5 veces"],
       ["Satisfacción SUS", "94,2 (95, 90 y 97,5)", "{{SUS de U1, U2 y U3}}", "{{interpretación}}"],
       ["Errores detectados", "12 (errores y dudas)", "1 duda", "Ver 6.4"]], [3.2, 3.8, 4.4, 4.6], 9.5)
P("Cómo se midió el tiempo: se tomó de los videos, desde que el facilitador dice “empiece” hasta que aparece la ganancia en pantalla. En U2 y U3 se detectó el cambio de pantalla "
  "en la grabación; en U1 se vio en el celular. El margen es de unos 2 segundos. No se usó cronómetro.", "j", 11)
H("6.4 Errores, observaciones y entrevista", 2)
tabla([["Usuario", "Pantalla", "Qué pasó", "Tipo", "Solución propuesta"],
       ["U2", "Ventas", "Fue primero a la pestaña Ventas buscando registrar la venta y dijo que ahí no la registraba; después usó el botón Nueva venta",
        "Equivocación", "Mantener el registro desde Inicio; evaluar renombrar la pestaña como “Historial de ventas” y repetir la prueba"]], [1.6, 2.0, 6.4, 2.4, 3.6], 9)
P("En U1 y U3 no se observó ningún error. U1 llenó la cantidad con el teclado numérico del celular, que aparece solo, y probó el filtro de fechas en Ganancias. "
  "U3 exploró Productos, el selector de fechas de Ventas, Ganancias por mes y por fechas, y Perfil. U2 exploró Ventas, la edición, Ganancias con el gráfico y los filtros.", "j")
tabla([["Pregunta", "U1", "U2", "U3"],
       ["¿Qué fue lo más difícil?", "Nada; le parece entendible", "Nada; le parece muy intuitivo y fácil de usar", "Nada; lo más fácil fue la interfaz simple y registrar la venta directo"],
       ["¿Qué cambiarías?", "Nada", "Nada; lo ve sencillo", "Nada; lo ve bien distribuido"],
       ["¿Confiarías en el sistema?", "Sí; le ahorra tiempo", "Sí, lo utilizaría", "Sí; lo ve útil"]], [3.4, 4.0, 4.4, 4.2], 9)
P("Las respuestas de la tabla son un resumen de lo dicho en los videos, no citas textuales.", "j", 10, cursiva=True)
H("6.5 Accesibilidad con la persona con discapacidad auditiva", 2)
P("No se encontraron barreras en el sistema: no usa sonido ni video, y los mensajes de error, confirmación y estado son visuales y con texto. La barrera estuvo en el protocolo, "
  "porque las instrucciones eran habladas, y se resolvió entregando la tarea por escrito. Para próximas pruebas conviene tener el guion de la tarea escrito para todos los participantes. "
  "No hubo prueba con una persona con discapacidad visual o motora real: esos casos solo se comprobaron de forma automática (teclado, zoom y reflow, secciones 4 y 5.2).", "j")
P("Satisfacción (SUS): {{respuestas del cuestionario SUS de U1, U2 y U3, con puntaje e interpretación}}", "j")

# ============ 7. CONCLUSIONES ============
H("7. Conclusiones DCU")
P("**El ciclo.** El PA1 definió el problema, los perfiles y la tarea. El PA2 llevó el diseño a un prototipo de alta fidelidad y lo probó con tres personas, con 12 errores y dudas registrados. "
  "El PA3 convirtió esos hallazgos en un sistema funcional que cumple los 11 criterios de accesibilidad de la guía y pasa 29 verificaciones de flujo y teclado y la auditoría de axe sin violaciones.", "j")
P("**¿Resolvió el problema inicial?** En lo técnico sí: el sistema permite registrar una venta, emitir un comprobante simulado y ver la ganancia sin internet y sin mouse. "
  "Las tres personas que lo probaron completaron la tarea sin ayuda, en unos 23 segundos en promedio y con una sola duda, y las tres dijeron que lo usarían o que confiarían en él. "
  "La satisfacción medida con el SUS queda por completar. {{Resultado del SUS}}", "j")
P("**Limitaciones.** La conexión con SUNAT es una simulación sin validez tributaria; no hay servidor, por lo que los datos viven en un solo navegador; la auditoría de axe y las pruebas "
  "automatizadas detectan solo una parte de los problemas y no reemplazan a las personas; solo se probó con tres personas y ninguna tenía las limitaciones motrices de Don Teo ni era un bodeguero mayor.", "j")
P("**Qué haría diferente.** Probar en un celular real con un bodeguero mayor y no en laptop con trackpad, cronometrar solo la tarea, repetir el SUS después de las correcciones y, "
  "en un proyecto con backend, reemplazar sunat.js por un servicio autorizado de facturación electrónica.", "j")

# ============ 8. ANEXOS ============
H("8. Anexos")
H("Anexo A. Consentimiento informado", 2)
P("“Voy a participar en una prueba de un sistema para un trabajo del curso Interacción Hombre-Máquina de la UTP. Entiendo que se evalúa el sistema y no mi desempeño, que puedo dejar la prueba "
  "cuando quiera y que la sesión se graba solo para el análisis del trabajo.” En las tres sesiones el consentimiento se dio de forma verbal y quedó grabado al inicio del video.", "j")
H("Anexo B. Cuestionario SUS", 2)
P("Escala de 1 (totalmente en desacuerdo) a 5 (totalmente de acuerdo). Puntaje: en las preguntas impares se resta 1 a la respuesta, en las pares se resta la respuesta a 5; se suma y se multiplica por 2,5.", "j", 11)
SUS = ["Creo que me gustaría usar esta app con frecuencia.", "Encontré que la app es innecesariamente compleja.", "Pensé que era fácil de usar.",
       "Creo que necesitaría apoyo de alguien técnico para poder usar la app.", "Las funciones de la app estaban bien integradas.", "Pensé que había demasiada inconsistencia en esta app.",
       "Imagino que la mayoría de personas aprendería a usar esta app rápidamente.", "La app me pareció muy difícil de usar.", "Me sentí muy seguro usando la app.",
       "Necesité aprender muchas cosas antes de poder usar el sistema."]
tabla([["N.º", "Afirmación", "U1", "U2"]] + [[str(i), t, "{{ }}", "{{ }}"] for i, t in enumerate(SUS, 1)], [1.1, 11.3, 1.8, 1.8], 9.5, centradas=(0, 2, 3))
H("Anexo C. Archivos de evidencia en el repositorio", 2)
tabla([["Carpeta o archivo", "Contenido"],
       ["evidencia/axe/", "Resultados de axe-core por pantalla (JSON) e informe en imagen"],
       ["evidencia/pantallas/", "Capturas del sistema real"],
       ["evidencia/codigo/", "Fragmentos de código de los 11 criterios"],
       ["tools/", "Scripts de prueba: flujos, auditoría de accesibilidad, contraste y generación de evidencias"]], [5.2, 10.8], 9.5)

doc.core_properties.title = f"PA3 - Interacción Hombre-Máquina - {APP}"
doc.save(OUT); print("OK", OUT)
