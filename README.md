# MercaTab

Ventas, productos y ganancias para bodegas y puestos de abarrotes. Funciona sin internet. Proyecto del curso Interacción Hombre-Máquina (UTP), avance PA3.

Es solo frontend: HTML, CSS y JavaScript sin dependencias. Los datos se guardan en el navegador. La conexión con SUNAT (consulta de RUC y DNI, boleta y factura) es una **simulación** sin validez tributaria.

## Cómo abrirlo

Abrir `app/index.html` en el navegador. Para probar el service worker (uso sin conexión) hay que servirlo por http:

```bash
cd app
python -m http.server 8000
# abrir http://localhost:8000
```

## Contenido

| Carpeta | Qué hay |
|---|---|
| `app/` | El sistema |
| `tools/` | Pruebas de flujo, auditoría de accesibilidad (axe-core), contraste y generación de evidencias |
| `evidencia/` | Capturas, informe de axe y fragmentos de código |
| `GUIA_CODIGO.md` | Explicación de cada archivo y cambios típicos |

## Accesibilidad

Implementa los 11 criterios de la guía del PA3: alt text, contraste 4.5:1, teclado completo, foco visible, ARIA labels, áreas táctiles de 44 px, errores con texto, labels y autocomplete, skip link, estructura semántica y tipografía mínima de 14 px.

## Pruebas

Requieren Python y Playwright (`pip install playwright` y `playwright install chromium`).

```bash
python tools/flujos.py
python tools/auditar.py
python tools/contraste.py
```

## Publicar en GitHub Pages

El archivo `.github/workflows/pages.yml` publica la carpeta `app`. Pasos: crear el repositorio, subir todo, y en Settings → Pages elegir **Source: GitHub Actions**.
