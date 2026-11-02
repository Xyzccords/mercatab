"""Calcula el puntaje SUS. Uso: python tools/sus.py 5 1 5 1 4 1 5 1 5 2   (las 10 respuestas, de 1 a 5, en orden)"""
import sys

def sus(r):
    return sum((v - 1) if i % 2 == 0 else (5 - v) for i, v in enumerate(r)) * 2.5

def interpretar(p):
    return "excelente" if p >= 85 else "aceptable" if p >= 70 else "marginal" if p >= 50 else "inaceptable"

if __name__ == "__main__":
    try:
        r = [int(x) for x in sys.argv[1:]]
    except ValueError:
        sys.exit("Escribe solo números del 1 al 5.")
    if len(r) != 10 or not all(1 <= v <= 5 for v in r):
        sys.exit("Se necesitan 10 respuestas, cada una de 1 a 5.")
    p = sus(r)
    print(f"SUS = {p:g} ({interpretar(p)})")
