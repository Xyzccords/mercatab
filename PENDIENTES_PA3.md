# PA3 · Lo que falta y solo ustedes pueden hacer

Todo lo que dependía de código, pruebas automáticas, informe y PPT ya está. Lo de abajo necesita personas, cuentas o datos reales. En el Word los huecos salen **resaltados en amarillo**.

## 1. Publicar el repositorio (15 min)
1. Crear un repositorio en GitHub y subir toda la carpeta `ihm_pa3` (la app está en `app/`).
2. En Settings → Pages elegir **Source: GitHub Actions**; el archivo `.github/workflows/pages.yml` publica la carpeta `app`.
3. Pegar las dos URLs (repositorio y sitio publicado) en la portada del Word, en la sección 3.6, y en la diapositiva final si quieren.

## 2. Captura con la extensión axe DevTools o WAVE (15 min)
La consigna pide el reporte "sobre el sistema real" en al menos 3 pantallas. El informe actual usa el motor de axe por script; conviene repetirlo con la extensión en Chrome:
1. Abrir el sitio publicado, instalar axe DevTools o WAVE, analizar Inicio, Ventas y Agregar venta.
2. Pegar las capturas en la sección 5 del Word y en la diapositiva 4. Si aparece algo, anotarlo en la tabla 5.1.

## 3. Prueba con usuarios (lo más importante que falta)
Mínimo **2 personas**, una de los perfiles del PA1. Recomendado: una con contexto de accesibilidad (usar solo una mano, solo Tab/Enter, o zoom al 200 %).
1. Explicar que se evalúa el sistema y no a la persona; pedir que piense en voz alta; **consentimiento** (verbal grabado o escrito).
2. Tarea: registrar una venta y ver la ganancia. **No ayudar.** Cronometrar solo la tarea y anotar los errores.
3. Exploración libre 3-5 min y entrevista (¿qué fue lo más difícil?, ¿qué cambió respecto al Figma?, ¿confiarías en el sistema?).
4. SUS (10 preguntas, el formulario del PA2 sirve). Calcular e interpretar: 70 o más aceptable, 85 o más excelente.
5. Guardar **una evidencia por usuario** (grabación, foto o notas).
6. Completar en el Word las secciones 6.2, 6.3, 6.4 y el Anexo B, y la diapositiva 5. **No inventar resultados**: si salen malos, se explican.

## 4. Video demo de 3 minutos
Hay una base sin voz en `evidencia/video/demo_teclado.webm` (32 s, solo Tab, Enter y flechas, con la tecla pulsada en pantalla). Graben el suyo con voz: recorrer el flujo, mostrar el skip link, el foco visible, un error de formulario, el modo sin conexión (Perfil → Simular sin conexión) y la factura con SUNAT.

## 5. Estudiar el código
La docente puede pedir cambios en vivo. Lean `GUIA_CODIGO.md` con el código abierto y practiquen los cambios de la sección 4 (color, tamaño de letra, IGV, un campo nuevo).

## 6. Dudas para la docente
- "Conectar con SUNAT" se implementó como **simulación**, porque el curso es frontend. Confirmar que eso es lo esperado.
- Mandarme la lista completa de correcciones que dio: aquí solo estaba la de SUNAT.

## 7. Revisión final
- Buscar texto amarillo en el Word y completarlo o quitarlo.
- Revisar la nota sobre uso de IA en la sección 3.1: está escrita tal como ocurrió; la consigna exige poder explicar cada línea.
- Nombres de archivo ya correctos: `PA3_IHM_Guerrero_Salvador.docx` y `PA3_PPT_Guerrero_Salvador.pptx`.
