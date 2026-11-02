"""Auditoría de accesibilidad de MercaTab: axe-core + comprobaciones propias (tamaño táctil, tipografía, alt, labels)."""
import json, os, sys
from playwright.sync_api import sync_playwright

RAIZ = r"D:\PruebasTareas\ihm_pa3"
URL = "file:///D:/PruebasTareas/ihm_pa3/app/index.html"
AXE = open(os.path.join(RAIZ, "tools", "axe.min.js"), encoding="utf-8").read()
SALIDA = os.path.join(RAIZ, "evidencia", "axe")
os.makedirs(SALIDA, exist_ok=True)

PANTALLAS = [("Inicio", "inicio"), ("Productos", "productos"), ("Agregar producto", "productos/nuevo"), ("Ventas", "ventas"),
             ("Agregar venta", "ventas/nueva"), ("Ganancias", "ganancias"), ("Perfil", "perfil"), ("Iniciar sesión", "login"),
             ("Crear cuenta", "registro"), ("Comprobantes", "comprobantes")]

MIDE = """() => {
  const visible = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && !el.closest('.solo-lector'); };
  const chicos = [];
  document.querySelectorAll('a[href], button, select, summary, input:not([type=hidden]):not([type=radio])').forEach(el => {
    if (!visible(el) || el.id === 'saltar') return;
    const r = el.getBoundingClientRect();
    if (r.width < 43.5 || r.height < 43.5) chicos.push({ el: el.tagName + (el.id ? '#' + el.id : '') + ' ' + (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 30), w: Math.round(r.width), h: Math.round(r.height) });
  });
  document.querySelectorAll('.segmentado label, .opciones label').forEach(el => { const r = el.getBoundingClientRect(); if (r.height < 43.5) chicos.push({ el: 'LABEL ' + el.textContent.trim(), w: Math.round(r.width), h: Math.round(r.height) }); });
  let minFuente = 99, dondeMin = '';
  const it = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (it.nextNode()) {
    const n = it.currentNode; if (!n.textContent.trim()) continue;
    const el = n.parentElement; if (!el || el.closest('svg') || el.closest('.solo-lector') || el.closest('script')) continue;
    if (!visible(el)) continue;
    const f = parseFloat(getComputedStyle(el).fontSize);
    if (f < minFuente) { minFuente = f; dondeMin = n.textContent.trim().slice(0, 30); }
  }
  const sinAlt = [...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).length;
  const conAlt = document.querySelectorAll('img[alt]').length;
  const iconosBoton = [...document.querySelectorAll('button, a')].filter(b => !b.textContent.trim() && !b.getAttribute('aria-label') && !b.getAttribute('aria-labelledby')).length;
  const campos = [...document.querySelectorAll('input:not([type=hidden]):not([type=radio]):not([type=file]), select')];
  const sinLabel = campos.filter(c => !c.labels || !c.labels.length).length;
  const sinAuto = campos.filter(c => !c.hasAttribute('autocomplete')).length;
  const puntos = ['header', 'nav', 'main', 'footer'].map(t => t + ':' + document.querySelectorAll(t).length).join(' ');
  return { chicos, minFuente, dondeMin, sinAlt, conAlt, iconosBoton, camposTotal: campos.length, sinLabel, sinAuto, puntos, h1: document.querySelectorAll('h1').length, lang: document.documentElement.lang };
}"""

resumen = []
with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_context(viewport={"width": 390, "height": 844}, locale="es-PE").new_page()
    pg.goto(URL); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_selector("main h1")
    pg.add_script_tag(content=AXE)
    for nombre, ruta in PANTALLAS:
        pg.evaluate(f"location.hash = '#/{ruta}'"); pg.wait_for_timeout(300)
        axe = pg.evaluate("""() => axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'] } })
          .then(r => ({ violations: r.violations.map(v => ({ id: v.id, impact: v.impact, ayuda: v.help, nodos: v.nodes.length, wcag: v.tags.filter(t => /^wcag\\d/.test(t)) })),
                        pasadas: r.passes.length, incompletas: r.incomplete.map(v => v.id), noAplica: r.inapplicable.length }))""")
        propio = pg.evaluate(MIDE)
        json.dump({"pantalla": nombre, "axe": axe, "propio": propio}, open(os.path.join(SALIDA, ruta.replace("/", "-") + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        resumen.append({"pantalla": nombre, "ruta": ruta, "axe": axe, "propio": propio})
        print(f"\n== {nombre}: axe -> {len(axe['violations'])} violaciones, {axe['pasadas']} reglas pasadas, {len(axe['incompletas'])} por revisar a mano")
        for v in axe["violations"]: print("   VIOLACION", v["id"], v["impact"], f"({v['nodos']} nodos)", v["ayuda"])
        print(f"   Táctil <44px: {len(propio['chicos'])} {propio['chicos'][:4]} | fuente mínima {propio['minFuente']}px ('{propio['dondeMin']}') | img sin alt {propio['sinAlt']} | botones sin nombre {propio['iconosBoton']} | campos {propio['camposTotal']} sin label {propio['sinLabel']} sin autocomplete {propio['sinAuto']} | {propio['puntos']} h1:{propio['h1']} lang:{propio['lang']}")
    nav.close()

json.dump(resumen, open(os.path.join(SALIDA, "resumen.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
total = sum(len(r["axe"]["violations"]) for r in resumen)
print(f"\nTOTAL violaciones axe en {len(resumen)} pantallas: {total}")
sys.exit(1 if total else 0)
