# -*- coding: utf-8 -*-
"""Pasa a build_informe.py los datos reales de las tres sesiones (videos) y las URLs publicadas. El SUS queda pendiente."""
p = r"D:\PruebasTareas\ihm_pa3\tools\build_informe.py"
s = open(p, encoding="utf-8").read()

def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)

# --- URLs
rep('APP = "MercaTab"', 'APP = "MercaTab"\nREPO = "https://github.com/Xyzccords/mercatab"\nSITIO = "https://xyzccords.github.io/mercatab/app/"')
rep('P("**Repositorio:** [[URL del repositorio en GitHub]]", "c", 11, despues=0)\nP("**Despliegue:** [[URL del sitio publicado, por ejemplo GitHub Pages]]", "c", 11, despues=0)',
    'q = P("**Repositorio:** ", "c", 11, despues=0); enlace(q, REPO, 10)\nq = P("**Despliegue:** ", "c", 11, despues=0); enlace(q, SITIO, 10)')
rep('p = P("**Repositorio:** [[URL del repositorio]]  ·  **Despliegue:** [[URL del sitio publicado]]", "j")',
    'q = P("**Repositorio:** ", "j"); enlace(q, REPO, 11)\nq = P("**Sitio publicado:** ", "j"); enlace(q, SITIO, 11)')

# --- Sección 6 completa
a = s.index("# ============ 6. VALIDACIÓN ============")
b = s.index("# ============ 7. CONCLUSIONES ============")
nuevo = '''# ============ 6. VALIDACIÓN ============
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

'''
s = s[:a] + nuevo + s[b:]

# --- Conclusiones
a = s.index('P("**¿Resolvió el problema inicial?**')
b = s.index('P("**Limitaciones.**')
s = s[:a] + '''P("**¿Resolvió el problema inicial?** En lo técnico sí: el sistema permite registrar una venta, emitir un comprobante simulado y ver la ganancia sin internet y sin mouse. "
  "Las tres personas que lo probaron completaron la tarea sin ayuda, en unos 23 segundos en promedio y con una sola duda, y las tres dijeron que lo usarían o que confiarían en él. "
  "La satisfacción medida con el SUS queda por completar. {{Resultado del SUS}}", "j")
''' + s[b:]
rep('ningún participante del PA2 tenía las limitaciones motrices de Don Teo.', 'solo se probó con tres personas y ninguna tenía las limitaciones motrices de Don Teo ni era un bodeguero mayor.')

# --- Anexo A
rep('cuando quiera y que la sesión se graba solo para el análisis del trabajo.” [[Adjuntar el consentimiento firmado o grabado de cada participante]]',
    'cuando quiera y que la sesión se graba solo para el análisis del trabajo.” En las tres sesiones el consentimiento se dio de forma verbal y quedó grabado al inicio del video.')

open(p, "w", encoding="utf-8").write(s)
print("informe parcheado")
