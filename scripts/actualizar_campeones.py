#!/usr/bin/env python3
"""
Detecta si el torneo de Primera División Argentina en curso ya terminó y,
si es así, arma un "borrador" con el posible campeón para que lo revises
antes de que se publique en la app.

Por qué un borrador y no publicación directa: los formatos del fútbol
argentino cambiaron muchísimo (Apertura/Clausura, Superliga, Copa de la
Liga con playoffs, etc.), y en varias de esas épocas el primero en la
tabla NO es necesariamente el campeón (hay definiciones por playoff/final).
Ya nos pasó cargar mal un campeón por confiar ciegamente en una sola
fuente. Este script hace la parte mecánica (fijarse si terminó el torneo
y quién lidera la tabla) y te deja a vos el paso de confirmar el nombre
del torneo y que el campeón sea correcto, en particular si hubo playoffs.

Variables de entorno (Secrets/Variables en GitHub):
  API_FOOTBALL_KEY, LEAGUE_ID (default 128), SEASON (default 2026)
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parent.parent
BORRADOR_PATH = ROOT / "data" / "campeones_borrador.json"
CONFIRMADOS_PATH = ROOT / "data" / "campeones_confirmados.json"

API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY", "")
LEAGUE_ID = os.environ.get("LEAGUE_ID", "128")
SEASON = os.environ.get("SEASON", "2026")
# Nombre del torneo en curso: esto SÍ hay que actualizarlo a mano cada vez
# que arranca un torneo nuevo con nombre distinto (Apertura, Clausura,
# Copa de la Liga, etc.), porque ninguna API te da el nombre "oficial"
# como lo usa la prensa argentina.
NOMBRE_TORNEO_ACTUAL = os.environ.get("NOMBRE_TORNEO_ACTUAL", "Torneo (confirmar nombre)")

BASE = "https://v3.football.api-sports.io"


def get(endpoint):
    req = Request(f"{BASE}{endpoint}", headers={"x-apisports-key": API_FOOTBALL_KEY})
    try:
        with urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, HTTPError) as e:
        print(f"ERROR llamando a la API: {e}")
        sys.exit(1)


def torneo_termino():
    """Devuelve True si ya no quedan partidos programados (NS) en la temporada."""
    data = get(f"/fixtures?league={LEAGUE_ID}&season={SEASON}&status=NS")
    pendientes = len(data.get("response", []))
    return pendientes == 0


def lider_de_la_tabla():
    data = get(f"/standings?league={LEAGUE_ID}&season={SEASON}")
    try:
        tabla = data["response"][0]["league"]["standings"][0]
    except (KeyError, IndexError):
        return None
    return tabla[0]["team"]["name"] if tabla else None


def main():
    if not API_FOOTBALL_KEY:
        print("ERROR: falta API_FOOTBALL_KEY.")
        sys.exit(1)

    if not torneo_termino():
        print("El torneo todavía no terminó. No hay nada para proponer todavía.")
        return

    lider = lider_de_la_tabla()
    if not lider:
        print("No pude leer la tabla de posiciones.")
        return

    confirmados = []
    if CONFIRMADOS_PATH.exists():
        confirmados = json.loads(CONFIRMADOS_PATH.read_text(encoding="utf-8"))

    ya_confirmado = any(
        c.get("season") == SEASON and c.get("torneo") == NOMBRE_TORNEO_ACTUAL
        for c in confirmados
    )
    if ya_confirmado:
        print("Este torneo ya está confirmado, no hago nada.")
        return

    borrador = {
        "season": SEASON,
        "torneo_propuesto": NOMBRE_TORNEO_ACTUAL,
        "campeon_propuesto": lider,
        "confirmado": False,
        "advertencia": "Verificá con una fuente si este torneo se definió por tabla general o por playoff/final. Si fue por playoff, el líder de la tabla puede NO ser el campeón real.",
    }
    BORRADOR_PATH.write_text(json.dumps(borrador, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Borrador escrito: {lider} como posible campeón de {NOMBRE_TORNEO_ACTUAL} {SEASON}.")
    print("Revisalo en data/campeones_borrador.json antes de confirmarlo.")


if __name__ == "__main__":
    main()
