# -*- coding: utf-8 -*-
"""Hoja imprimible para aplicar la prueba con usuario del PA3 (consentimiento, tarea, errores, entrevista y SUS)."""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"D:\PruebasTareas\ihm_pa3\HOJA_DE_PRUEBA.docx"
MARRON = "6B3F26"
doc = Document()
s = doc.sections[0]
s.page_width, s.page_height = Cm(21), Cm(29.7)
for m in ("left_margin", "right_margin"): setattr(s, m, Cm(2))
s.top_margin = s.bottom_margin = Cm(1.8)

n = doc.styles["Normal"]; n.font.name = "Arial"; n.font.size = Pt(11)
n.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial"); n.paragraph_format.space_after = Pt(4); n.paragraph_format.line_spacing = 1.2
for nombre, tam in (("Heading 1", 14), ("Heading 2", 12)):
    h = doc.styles[nombre]; h.font.name = "Arial"; h.font.size = Pt(tam); h.font.bold = True; h.font.color.rgb = RGBColor.from_string(MARRON)
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial"); h.paragraph_format.space_before = Pt(10); h.paragraph_format.space_after = Pt(4)

def P(t, neg=False, cur=False, tam=None):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = neg; r.italic = cur
    if tam: r.font.size = Pt(tam)
    return p

def sombra(c, color):
    pr = c._tc.get_or_add_tcPr(); e = OxmlElement("w:shd"); e.set(qn("w:val"), "clear"); e.set(qn("w:color"), "auto"); e.set(qn("w:fill"), color); pr.append(e)

def tabla(filas, anchos, alto=None, cabecera=True, tam=10):
    t = doc.add_table(rows=len(filas), cols=len(anchos)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for j, w in enumerate(anchos): t.columns[j].width = Cm(w)
    for i, fila in enumerate(filas):
        if alto and i > 0 or (alto and not cabecera):
            t.rows[i].height = Cm(alto)
        for j, v in enumerate(fila):
            c = t.cell(i, j); c.width = Cm(anchos[j]); c.text = ""
            r = c.paragraphs[0].add_run(v); r.font.size = Pt(tam)
            c.paragraphs[0].paragraph_format.space_after = Pt(0)
            if cabecera and i == 0:
                r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); sombra(c, MARRON)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def caja(titulo, alto_cm):
    t = doc.add_table(rows=1, cols=1); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.rows[0].height = Cm(alto_cm); c = t.cell(0, 0); c.text = ""
    r = c.paragraphs[0].add_run(titulo); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = RGBColor(0x5C, 0x4A, 0x3F)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

doc.add_heading("MercaTab · Hoja de prueba con usuario (PA3)", 1)
P("Una hoja por participante. Mínimo 2 participantes y una evidencia por persona (grabación, foto o estas notas). No se ayuda durante la tarea.", cur=True)

doc.add_heading("A. Datos del participante", 2)
tabla([["Campo", "Respuesta"], ["Código (U1, U2…)", ""], ["Fecha y lugar", ""], ["Facilitador y observador", ""], ["Edad", ""],
       ["Ocupación y relación con el rubro de abarrotes", ""], ["Perfil del PA1 al que se parece (Don Teo, Jimena u otro)", ""],
       ["Dispositivo y navegador", ""],
       ["Contexto de accesibilidad\n[  ] ninguno  [  ] una sola mano  [  ] solo Tab y Enter  [  ] zoom al 200 %\n[  ] pantalla con poco brillo  [  ] lector de pantalla  [  ] otro: ________", ""]],
      [8, 9], alto=0.9, tam=10)

doc.add_heading("B. Bienvenida y consentimiento (2 min)", 2)
P("Decir: “Estamos probando el sistema, no a ti. No hay respuestas buenas o malas. Mientras lo uses, di en voz alta lo que piensas. "
  "Si algo te confunde, es culpa del sistema y nos ayuda saberlo. No te vamos a ayudar durante la tarea, pero puedes dejar la prueba cuando quieras.”", cur=True)
P("Consentimiento: “Voy a participar en una prueba de un sistema para un trabajo del curso Interacción Hombre-Máquina de la UTP. Entiendo que se evalúa el sistema y no mi desempeño, "
  "que puedo dejar la prueba cuando quiera y que la sesión se graba solo para el análisis del trabajo.”")
P("[  ] Consentimiento verbal grabado        [  ] Consentimiento escrito       Nombre: ______________________   Firma: ____________   Fecha: ________")

doc.add_heading("C. Tarea principal (5 a 10 min)", 2)
P("Decir: “Tienes un puesto de abarrotes. Un cliente compró productos y necesitas registrar la venta y luego ver tu ganancia. Hazlo sin ayuda y comenta lo que piensas.”", cur=True)
tabla([["Hora de inicio", "Hora de fin", "Tiempo de la tarea (s)", "Duración de la sesión (s)"], ["", "", "", ""]], [4.25] * 4, alto=0.9)
tabla([["Paso del GOMS", "¿Lo completó sin ayuda?"],
       ["1. Registrar venta", "[  ] sí   [  ] no"], ["2. Seleccionar producto", "[  ] sí   [  ] no"], ["3. Ingresar cantidad", "[  ] sí   [  ] no"],
       ["4. Confirmar (Guardar)", "[  ] sí   [  ] no"], ["5. Ver el resultado (ganancia)", "[  ] sí   [  ] no"]], [9, 8], alto=0.7)
P("Efectividad = pasos completados ÷ 5 × 100:  ______ %", neg=True)
P("Errores observados (anotar lo que realmente pasó):", neg=True)
tabla([["Minuto", "Pantalla", "Qué pasó o qué dijo", "Tipo"]] + [["", "", "", ""] for _ in range(7)], [1.8, 3.2, 9, 3], alto=1.0)
P("Tipo: lapsus (toque automático equivocado) · equivocación (creyó que algo servía para otra cosa) · basado en reglas (usó algo de otras apps que aquí no vale) · de conocimiento (no supo qué hacer).", cur=True, tam=9)

doc.add_heading("D. Exploración libre (3 a 5 min)", 2)
P("Decir: “Ahora navega como quieras.” Observar qué toca, qué ignora y dónde se detiene.", cur=True)
caja("Notas del observador", 3.2)

doc.add_heading("E. Entrevista (5 min)", 2)
for q in ("1. ¿Qué fue lo más difícil?", "2. ¿Qué cambiarías? (¿qué cambió respecto al diseño en Figma del PA2? lo responde el grupo en el informe)", "3. ¿Confiarías en este sistema para tu trabajo real?"):
    P(q, neg=True); caja("Respuesta", 1.9)

doc.add_page_break()
doc.add_heading("F. Cuestionario SUS (2 min)", 2)
P("Marcar con un círculo: 1 = totalmente en desacuerdo, 5 = totalmente de acuerdo.", cur=True)
SUS = ["Creo que me gustaría usar esta app con frecuencia.", "Encontré que la app es innecesariamente compleja.", "Pensé que era fácil de usar.",
       "Creo que necesitaría apoyo de alguien técnico para poder usar la app.", "Las funciones de la app estaban bien integradas.", "Pensé que había demasiada inconsistencia en esta app.",
       "Imagino que la mayoría de personas aprendería a usar esta app rápidamente.", "La app me pareció muy difícil de usar.", "Me sentí muy seguro usando la app.",
       "Necesité aprender muchas cosas antes de poder usar el sistema."]
tabla([["N.º", "Afirmación", "1", "2", "3", "4", "5"]] + [[str(i), t, "", "", "", "", ""] for i, t in enumerate(SUS, 1)], [1, 11, 1, 1, 1, 1, 1], alto=1.0)
P("Cálculo: en las preguntas impares (1, 3, 5, 7, 9) restar 1 a la respuesta; en las pares (2, 4, 6, 8, 10) restar la respuesta a 5. Sumar los diez valores y multiplicar por 2,5.")
P("O usar el programa: python tools/sus.py 5 1 5 1 4 1 5 1 5 2  (las diez respuestas en orden).", cur=True)
tabla([["Suma de los diez valores", "Puntaje SUS (suma × 2,5)", "Interpretación"], ["", "", "[  ] menos de 50 inaceptable  [  ] 50 a 70 marginal\n[  ] 70 o más aceptable  [  ] 85 o más excelente"]], [4.5, 5, 7.5], alto=1.6)

doc.add_heading("G. Cierre del facilitador", 2)
P("Evidencia guardada:  [  ] grabación   [  ] foto   [  ] estas notas escaneadas.    Archivo: ______________________________")
P("No exponer datos personales del participante en el informe: solo código, edad, ocupación y relación con los perfiles.", cur=True, tam=10)
doc.save(OUT); print("OK", OUT)
