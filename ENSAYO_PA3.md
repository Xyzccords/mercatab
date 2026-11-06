# MercaTab PA3 · Ensayo de la exposición (12 a 15 min)

Reparto sugerido: **Diego** diapositivas 1 a 5, **Lindel** de la 6 a la 9 y la demo. Los dos deben poder responder cualquier pregunta: la docente puede preguntarle a cualquiera y pedir cambios en vivo.

## Guion corto (≈ 13 min)
1. **Portada (30 s).** MercaTab: una app para que dueños de bodegas registren ventas y vean su ganancia, aunque no tengan internet. Hoy: del Figma al código, accesibilidad y prueba con usuarios.
2. **Del Figma al código (1,5 min).** Mismo diseño, corregido con los hallazgos del PA2: botón verde a contorno (el verde daba contraste 2,83:1), ícono propio para Registrar venta, íconos de editar y eliminar de 44 px, valores en el gráfico.
3. **Accesibilidad (2 min).** Los 11 criterios de la guía, no solo 8. Mostrar tres: foco visible (`:focus-visible`), skip link, aria-label en íconos. Decir dónde está cada uno en el código.
4. **axe (1 min).** axe-core, 0 violaciones en 10 pantallas. Además se midió tamaño táctil, texto mínimo y reflow a 320 px. Decir con claridad que la captura con la extensión WAVE o axe DevTools [completar cuando esté].
5. **Prueba con usuarios (2 min).** [completar con los datos finales que confirmen]. Decir lo que se midió y lo que no.
6. **Hallazgos (1,5 min).** Tres barreras del código real: contraste del verde, enlaces de 20 px, scroll horizontal a 320 px. Y la de Ventas: 80 botones antes de la barra de navegación, corregida con «Mostrar más».
7. **Demo (3 min).** Solo teclado: primer Tab = skip link, Registrar venta, producto y cantidad, factura, RUC de ejemplo, Consultar SUNAT, comprobante, Ganancias. Luego Perfil → Simular sin conexión.
8. **Ciclo DCU (30 s).** Problema → PA1 → PA2 → PA3, probar, detectar, corregir.
9. **Cierre (20 s).** Una frase.

## Qué es real y qué es simulado (decirlo ustedes primero)
- **Real:** validación del RUC con el dígito verificador (módulo 11), cálculo de IGV 18 %, correlativos B001 y F001, estados aceptado y pendiente, modo sin conexión y datos guardados en el navegador.
- **Simulado:** la consulta a SUNAT (padrón de ejemplo con contribuyentes ficticios), el envío y la aceptación. No hay firma digital ni validez tributaria, y cada pantalla lo dice.
- Es un curso de solo frontend: no hay servidor, por eso los datos viven en un solo navegador.

## Preguntas probables
**¿Por qué sin framework?** Para poder explicar cada línea y abrirlo con doble clic. El curso es frontend.
**¿Dónde se guardan los datos?** En `localStorage`. Con `sw.js` los archivos quedan en caché y la app abre sin internet.
**¿Por qué el foco va al `h1` al cambiar de pantalla?** Es una app de una sola página: el navegador no recarga y el teclado o el lector de pantalla no sabrían que cambió la pantalla (`pintar()` en `app.js`).
**¿Por qué `<dialog>`?** El navegador atrapa el foco, bloquea el fondo y cierra con Esc, sin código extra.
**¿Qué detecta axe y qué no?** Contraste, nombres, etiquetas y estructura. No detecta si un texto alternativo es útil ni si el flujo se entiende: eso lo muestran las personas.
**¿Qué es el contraste 4.5:1?** La relación entre la luminosidad del texto y la del fondo; es el mínimo WCAG AA. Se calcula con `tools/contraste.py`.
**¿Qué pasa con el color solo?** Los errores llevan ícono, texto y un resumen con `role="alert"`, y el segmentado marca la opción con un ✓, no solo con color.
**¿Cómo se valida el RUC?** Se multiplica cada uno de los primeros 10 dígitos por 5,4,3,2,7,6,5,4,3,2, se suma, se toma 11 menos el resto de dividir entre 11, y ese resultado (10 pasa a 0 y 11 a 1) debe ser el dígito 11 (`digitoRUC()` en `sunat.js`).
**¿Por qué la boleta pide DNI desde S/ 700?** Es la regla de boletas por montos a partir de ese importe, en la constante `LIMITE_BOLETA_SIN_DNI`. [Verificar con la docente si quiere otro valor.]
**¿Se usó IA?** Sí, el código se escribió con apoyo de IA (Claude) y está declarado en el informe. Estudiar `GUIA_CODIGO.md`: hay que poder explicar cada línea y justificar cada decisión.
**¿Qué limitaciones tiene?** SUNAT simulada, sin servidor, pocas personas en la prueba, y la prueba automática no sustituye a las personas.
**¿Qué harían distinto?** Probar en celular real con un bodeguero mayor, cronometrar solo la tarea y repetir el SUS tras las correcciones.

## Cambios en vivo que pueden pedir (ver GUIA_CODIGO.md, sección 4)
Color principal (`--marron`), tamaño de letra (`body`), IGV (`IGV` en `sunat.js`), un campo nuevo en producto (`productoForm()`), quitar el foco para mostrar la diferencia (comentar `:focus-visible`), cantidad de ventas por página (`PASO` en `vistas.js`).

## Antes de entrar
Abrir el sitio publicado en el celular y en la laptop, con la sesión limpia (Perfil → Restablecer datos de ejemplo), y tener el código abierto en el editor.
