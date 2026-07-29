# Campeones automáticos (con revisión tuya antes de publicar)

## Cómo funciona, en criollo

1. Todos los lunes, un robot gratis (GitHub Actions) se fija si el
   torneo argentino en curso ya terminó.
2. Si terminó, escribe un "borrador" (`data/campeones_borrador.json`)
   proponiendo al líder de la tabla como campeón. **No lo publica solo.**
3. Vos entrás una vez por semana (o cuando te llegue la notificación de
   que hubo un commit nuevo), revisás ese borrador, y si está bien, lo
   pasás a mano al archivo `data/campeones_confirmados.json`.
4. La app lee `campeones_confirmados.json` y lo suma a la lista que ya
   tiene incorporada en el código.

## Por qué no lo publico 100% solo

Porque en el fútbol argentino, un montón de veces el que lidera la tabla
al final NO es el campeón: hay playoffs, finales, y formatos que cambian
todo el tiempo (viste lo que costó dejar bien la lista actual). Prefiero
que el robot te avise "che, esto terminó y el candidato es tal equipo",
y que vos confirmes con una fuente (o simplemente porque ya lo sabés,
si seguiste el torneo) antes de que quede escrito en la app para
siempre. Es la única forma honesta de automatizar esto sin arriesgarme
a que se repita un error como los que ya tuvimos.

## Setup (igual que hicimos con promedios)

1. Subí esta carpeta a tu repo de GitHub (la misma app, o un repo aparte).
2. Conseguí tu key gratis en api-football.com.
3. `Settings → Secrets and variables → Actions`:
   - Secret `API_FOOTBALL_KEY`: tu key.
   - Variables (no secretas): `LEAGUE_ID` (confirmá cuál es en la
     documentación de la API), `SEASON` (ej. `2026`), y
     `NOMBRE_TORNEO_ACTUAL` (ej. `"Clausura 2026"` — esto lo tenés que
     cambiar vos a mano cada vez que arranca un torneo con nombre nuevo,
     ninguna API te lo dice).

## Cuando llega un borrador

Abrí `data/campeones_borrador.json`. Va a tener algo así:

```json
{
  "season": "2026",
  "torneo_propuesto": "Clausura 2026",
  "campeon_propuesto": "Racing Club",
  "confirmado": false,
  "advertencia": "Verificá si fue por tabla general o por playoff/final..."
}
```

Si estás de acuerdo, copiá esa info a `data/campeones_confirmados.json`
(que es una lista), agregando tu entrada:

```json
[
  { "year": "2026", "torneo": "Clausura", "campeon": "Racing Club" }
]
```

## Conectar la app

En el archivo de la app hay una constante `CAMPEONES_EXTRA_JSON_URL`.
Pegá ahí la URL de tu `campeones_confirmados.json` (por ejemplo, vía
jsDelivr: `https://cdn.jsdelivr.net/gh/tu-usuario/tu-repo@main/data/campeones_confirmados.json`).
La app va a mostrar esos campeones sumados arriba de la lista que ya
trae incorporada, marcados como "agregado por vos" para diferenciarlos.
