# Segundo parcial — Intérprete de reglas

Programa en Python para identificar átomos (`X1`, `X2`...) y reglas (`R1`, `R2`...) a partir de oraciones en español.

## Uso

1. Escribe el problema en `entrada.txt`. Puedes utilizar varias líneas o un solo párrafo con oraciones separadas por puntos.
2. Abre una terminal en esta carpeta y ejecuta:

```bash
python -m src.main entrada.txt
```

También puedes indicar otro archivo `.txt` en el mismo comando.

## Expresiones admitidas

- `Si P, entonces Q` (con o sin coma).
- `P y Q`, `P o Q` y `No P`.
- `No es cierto que P y Q` (niega el conjunto).
- Paréntesis para agrupar condiciones.

Las oraciones que no pueden interpretarse se indican en la salida. Esta primera etapa **identifica y clasifica reglas**; aún no incluye FNC ni SAT.

## Pruebas

```bash
python -m unittest discover -s tests -v
```
