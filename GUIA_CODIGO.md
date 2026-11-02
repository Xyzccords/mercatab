# Guía del código de MercaTab (para estudiar antes de exponer)

La consigna del PA3 dice que el código debe poder explicarse **línea por línea** y que la docente puede **pedir cambios en vivo**. Esta guía sirve para eso. Léanla con el código abierto, en este orden.

## 1. Cómo arranca la app (el hilo de todo)

1. `app/index.html` carga seis scripts en este orden: `iconos.js`, `ui.js`, `datos.js`, `sunat.js`, `vistas.js`, `app.js`. El orden importa: cada archivo usa lo que definió el anterior.
2. `app/js/app.js` mira el hash de la dirección (`#/productos`, `#/ventas/nueva`…), busca la pantalla en la tabla `RUTAS` y llama a `pintar()`.
3. `pintar()` pide la pantalla a `Vistas`, pone el título, marca la pestaña activa con `aria-current="page"`, limpia los eventos de la pantalla anterior, dibuja la nueva y **mueve el foco al `h1`**.
4. Cada pantalla (`vistas.js`) escribe su HTML con `root.innerHTML = ...` y conecta sus eventos (`onclick`, `oninput`, `onsubmit`).
5. Los datos viven en `datos.js` y se guardan en `localStorage`. Nada sale del navegador.

## 2. Qué hace cada archivo

| Archivo | Para qué sirve | Lo que deben saber explicar |
|---|---|---|
| `index.html` | Estructura: skip link, `header`, `main`, `footer`, `nav`, `dialog` | Por qué hay un `main` con `tabindex="-1"` (para recibir el foco del skip link) |
| `css/estilos.css` | Colores (variables en `:root`), foco, tamaños | Qué es `:focus-visible`; por qué `min-height: 48px` en `.boton` |
| `js/iconos.js` | Íconos SVG | Siempre llevan `aria-hidden="true"`: el texto o el `aria-label` los explican |
| `js/ui.js` | `modal()`, `campo()`, `resumenErrores()`, `aviso()`, formatos | `campo()` crea label + ayuda + input + error enlazados con `aria-describedby` |
| `js/datos.js` | Productos, ventas, ganancias, respaldo | `resumen(desde, hasta)` suma ventas y costos; ganancia = ventas − inversión |
| `js/sunat.js` | SUNAT **simulada** | `digitoRUC()` es el algoritmo real (módulo 11); `consultar()` usa un padrón de ejemplo |
| `js/vistas.js` | Todas las pantallas | Formularios: `leer()` → `validar()` → guardar; errores con texto |
| `js/app.js` | Rutas, navegación, red | `hashchange` + aviso de cambios sin guardar; `actualizarRed()` |
| `sw.js` | Service worker (uso sin conexión) | Guarda los archivos en caché y los sirve si no hay internet |

## 3. Dónde está cada criterio de accesibilidad

| # | Criterio | Dónde buscarlo |
|---|---|---|
| 1 | Alt text | `vistas.js`, función `fotoDe()`: `alt="${p.altFoto ...}"`; datos de ejemplo con `altFoto` en `datos.js` |
| 2 | Contraste 4.5:1 | `estilos.css`, variables de `:root`; se calcula con `tools/contraste.py` |
| 3 | Teclado | Todo es `a`, `button`, `select`, `input`, `details` o `dialog` (nativos). `app.js` → `pintar()` mueve el foco al `h1` |
| 4 | Foco visible | `estilos.css`: `:focus-visible { outline: 3px solid var(--foco); outline-offset: 2px; }` |
| 5 | ARIA labels | Botones de solo ícono con `aria-label` en `vistas.js` (editar, eliminar, quitar, ver contraseña) |
| 6 | 44×44 px | `.boton` (`min-height: 48px; min-width: 44px`), `.boton--icono` (`width: 44px`), `.barra a` (`min-height: 56px`) |
| 7 | Errores con texto | `ui.js` → `campo()` (ícono + texto) y `resumenErrores()` (`role="alert"`, recibe el foco) |
| 8 | Labels y autocomplete | `ui.js` → `campo()` y `vistas.js` (`autocomplete="email"`, `new-password`, `name`, `organization`) |
| 9 | Skip link | `index.html` (primer elemento) y `.saltar` en `estilos.css`; el clic se maneja en `app.js` |
| 10 | Semántica | `index.html`: `header`, `main`, `footer`, `nav`; un `h1` por pantalla (`ui.encabezado`) |
| 11 | 14 px mínimo | `body { font: 400 1rem/1.5 ... }`; lo más pequeño usa `.875rem` (14 px) |

## 4. Cambios que la docente podría pedir en vivo (y cómo hacerlos)

| Pedido | Qué tocar |
|---|---|
| Cambiar el color principal | `estilos.css`, variable `--marron` en `:root` (y revisar contraste con `python tools/contraste.py`) |
| Agrandar el texto | `estilos.css`, `body { font: 400 1rem/1.5 ... }` → `1.125rem` |
| Quitar el foco para mostrar la diferencia | Comentar la regla `:focus-visible` en `estilos.css` y recargar |
| Cambiar el IGV | `sunat.js`, constante `IGV = 0.18` |
| Cambiar desde qué monto la boleta pide DNI | `sunat.js`, constante `LIMITE_BOLETA_SIN_DNI = 700` |
| Agregar una pestaña al menú | `app.js`: tabla `NAV` y tabla `RUTAS`; en `vistas.js` una función nueva; icono en `iconos.js` |
| Agregar un campo al producto (por ejemplo, marca) | `vistas.js` → `productoForm()`: el objeto `v`, el HTML con `campo({...})`, `leer()`, `validar()` y el objeto `p` al guardar |
| Cambiar un mensaje de error | Buscar el texto en `vistas.js` (están dentro de `validar()`) |
| Hacer un botón más grande | `estilos.css`, `.boton { min-height: 48px }` |
| Poner otro texto alternativo | `datos.js`, campo `altFoto` del producto |
| Mostrar que un ícono tiene nombre accesible | Inspeccionar el botón con DevTools y mostrar `aria-label` |
| Probar sin mouse | `Tab`, `Shift+Tab`, `Enter`, `Esc`, flechas en los grupos de opciones |

## 5. Qué es real y qué es simulado (SUNAT)

- **Real en el navegador:** validación del RUC con el dígito verificador, validación del DNI, cálculo de base imponible e IGV, correlativos B001 y F001, reglas de boleta y factura, estados *aceptado* y *pendiente*.
- **Simulado:** la consulta a SUNAT (usa un padrón de ejemplo con contribuyentes ficticios), el envío y la aceptación del comprobante.
- **No existe:** firma digital, proveedor autorizado, validez tributaria. Por eso cada pantalla lo dice.
- Para conectar algo real solo habría que cambiar `consultar()`, `emitir()` y `enviarPendientes()` en `sunat.js`, y tendría que haber un servidor.

## 5.1 Qué es el padrón de ejemplo (para no confundirse)

Los RUC `20600000013` y similares y el DNI `12345678` **no son reales**: salen de `PADRON_RUC` y `PADRON_DNI` en `sunat.js`. Un RUC que no esté ahí responde “no se encontró”.

## 6. Cómo correr las pruebas

```bash
# desde la carpeta ihm_pa3, con Python y Playwright instalados
python tools/flujos.py        # 25 verificaciones de flujo y teclado
python tools/auditar.py       # axe-core en 10 pantallas + tamaño táctil, fuente, alt, labels
python tools/contraste.py     # contraste de la paleta
python tools/evidencias.py    # regenera capturas y fragmentos de código del informe
```

## 7. Preguntas probables y respuestas cortas

- **¿Por qué sin framework?** Para poder explicar cada línea y abrirlo con doble clic. El curso es solo frontend.
- **¿Dónde se guardan los datos?** En `localStorage` del navegador. No hay servidor.
- **¿Cómo funciona sin internet?** Los datos ya están en el navegador y `sw.js` guarda los archivos en caché.
- **¿Por qué el foco va al `h1` al cambiar de pantalla?** Es una app de una sola página: el navegador no recarga, así que el teclado y el lector de pantalla no sabrían que cambió la pantalla.
- **¿Por qué `<dialog>`?** El navegador atrapa el foco, bloquea el fondo y cierra con Esc sin código extra.
- **¿Qué detecta axe y qué no?** Reglas automáticas (contraste, nombres, etiquetas, estructura). No detecta si el texto alternativo es útil ni si el flujo es entendible: eso requiere personas.
- **¿Qué cambió respecto al Figma?** Ver sección 3.4 del informe: botón verde, ícono de caja, valores en el gráfico, íconos de 44 px, ayudas en precio e inversión, aviso sin conexión.
- **¿Se usó IA?** Sí, el código se escribió con apoyo de IA (Claude) y así consta en el informe. Estudien esta guía: hay que poder explicar cada decisión.
