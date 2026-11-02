"""Calcula el contraste WCAG de los pares texto/fondo de la paleta de MercaTab (mínimo 4.5:1 en texto, 3:1 en componentes)."""
def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def razon(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

PARES = [  # (descripción, texto, fondo, mínimo)
    ("Texto principal sobre crema", "#2B2118", "#F5ECE8", 4.5),
    ("Texto principal sobre blanco", "#2B2118", "#FFFFFF", 4.5),
    ("Texto secundario sobre crema", "#5C4A3F", "#F5ECE8", 4.5),
    ("Texto secundario sobre blanco", "#5C4A3F", "#FFFFFF", 4.5),
    ("Botón primario: blanco sobre marrón", "#FFFFFF", "#7B4A2D", 4.5),
    ("Botón secundario: marrón sobre crema", "#7B4A2D", "#F5ECE8", 4.5),
    ("Botón peligro: blanco sobre rojo", "#FFFFFF", "#B3261E", 4.5),
    ("Error: rojo sobre blanco", "#B3261E", "#FFFFFF", 4.5),
    ("Error: rojo sobre fondo de error", "#B3261E", "#FCE9E7", 4.5),
    ("Menú activo: tinta sobre durazno", "#2B2118", "#F4A27A", 4.5),
    ("Etiqueta aceptado: verde sobre verde claro", "#1F6B3B", "#E4F3E9", 4.5),
    ("Etiqueta pendiente: marrón oscuro sobre aviso", "#5A3420", "#FDE3D3", 4.5),
    ("Aviso emergente: blanco sobre tinta", "#FFFFFF", "#2B2118", 4.5),
    ("Borde de campo sobre blanco (componente)", "#8C7468", "#FFFFFF", 3.0),
    ("Barra ganancia sobre blanco (gráfico)", "#5A3420", "#FFFFFF", 3.0),
    ("Barra inversión sobre blanco (gráfico)", "#B4501A", "#FFFFFF", 3.0),
    ("Barra ganancia contra barra inversión", "#5A3420", "#B4501A", 1.5),
    ("Foco azul sobre crema (componente)", "#0B3D91", "#F5ECE8", 3.0),
]
if __name__ == "__main__":
    mal = 0
    for desc, t, f, minimo in PARES:
        r = razon(t, f); ok = r >= minimo; mal += not ok
        print(f"{'OK   ' if ok else 'FALLA'} {r:5.2f}:1 (mín {minimo})  {desc}")
    print(f"\n{len(PARES) - mal}/{len(PARES)} pares correctos")
