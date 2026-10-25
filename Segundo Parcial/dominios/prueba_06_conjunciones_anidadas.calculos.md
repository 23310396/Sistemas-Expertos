# Cálculos — prueba_06_conjunciones_anidadas

<!-- revision:425aeb146fad6d11dbc13d40152ad7daaf4c4f69f1b929b0c569eb3e54540e2f -->
**Fuente:** `prueba_06_conjunciones_anidadas.txt`  
**Calculado:** 2026-10-25 05:45:34 UTC  
**Estado:** SAT  
**Motor:** PySAT (Glucose3)

## Átomos

- X1: el sensor detecta falla
- X2: la camara detecta defecto
- X3: el motor funciona
- X4: el robot se detiene
- X5: el operador revisa equipo

## Reglas: texto, lógica y FNC

### R1

- Texto: Si (el sensor detecta falla o la camara detecta defecto) y el motor funciona, entonces el robot se detiene.
- Lógica: `((X1 ∨ X2) ∧ X3) → X4`
- FNC: `(¬X1 ∨ ¬X3 ∨ X4) ∧ (¬X2 ∨ ¬X3 ∨ X4)`

### R2

- Texto: Si el robot se detiene, entonces el operador revisa equipo.
- Lógica: `X4 → X5`
- FNC: `(¬X4 ∨ X5)`

### R3

- Texto: El motor funciona.
- Lógica: `X3`
- FNC: `X3`

### R4

- Texto: El sensor detecta falla o la camara detecta defecto.
- Lógica: `X1 ∨ X2`
- FNC: `(X1 ∨ X2)`

### R5

- Texto: El operador revisa equipo.
- Lógica: `X5`
- FNC: `X5`

## FNC completa

`(¬X1 ∨ ¬X3 ∨ X4) ∧ (¬X2 ∨ ¬X3 ∨ X4) ∧ (¬X4 ∨ X5) ∧ X3 ∧ (X1 ∨ X2) ∧ X5`

## Cláusulas numéricas

`[[-1, -3, 4], [-2, -3, 4], [-4, 5], [3], [1, 2], [5]]`

## DIMACS

```dimacs
p cnf 5 6
-1 -3 4 0
-2 -3 4 0
-4 5 0
3 0
1 2 0
5 0
```

## Satisfacibilidad

- Solver: **SAT**
- Árbol: **SAT**
- ¿Coinciden?: **Sí**

### Mundos del solver (valores V/F)

1. X1=F, X2=V, X3=V, X4=V, X5=V
2. X1=V, X2=V, X3=V, X4=V, X5=V
3. X1=V, X2=F, X3=V, X4=V, X5=V

## Árbol semántico

- Ramas abiertas: 2
- Ramas cerradas: 6
- Nodos generados: 22

### Desarrollo de nodos

| Nodo | Padre | Regla/origen | Expresión | Estado |
|---|---|---|---|---|
| N1 | — | Conjunto de reglas | (((X1 ∨ X2) ∧ X3) → X4) ∧ (X4 → X5) ∧ X3 ∧ (X1 ∨ X2) ∧ X5 | normal |
| N2 | N1 | R1 | ((X1 ∨ X2) ∧ X3) → X4 | normal |
| N3 | N2 | R2 | X4 → X5 | normal |
| N4 | N3 | R3 | X3 | normal |
| N5 | N4 | R4 | X1 ∨ X2 | normal |
| N6 | N5 | R5 | X5 | normal |
| N7 | N6 | R1 | ¬((X1 ∨ X2) ∧ X3) | normal |
| N8 | N6 | R1 | X4 | normal |
| N9 | N7 | R1 | ¬(X1 ∨ X2) | normal |
| N10 | N7 | R1 | ¬X3 | cerrada |
| N11 | N9 | R1 | ¬X1 | normal |
| N12 | N11 | R1 | ¬X2 | normal |
| N13 | N12 | R2 | ¬X4 | normal |
| N14 | N12 | R2 | X5 | normal |
| N15 | N13 | R4 | X1 | cerrada |
| N16 | N13 | R4 | X2 | cerrada |
| N17 | N14 | R4 | X1 | cerrada |
| N18 | N14 | R4 | X2 | cerrada |
| N19 | N8 | R2 | ¬X4 | cerrada |
| N20 | N8 | R2 | X5 | normal |
| N21 | N20 | R4 | X1 | abierta |
| N22 | N20 | R4 | X2 | abierta |

### Contradicciones

- N10: X3 y su negación (N4 / N10).
- N15: X1 y su negación (N11 / N15).
- N16: X2 y su negación (N12 / N16).
- N17: X1 y su negación (N11 / N17).
- N18: X2 y su negación (N12 / N18).
- N19: X4 y su negación (N8 / N19).

El TXT es la fuente editable. Este reporte se reemplaza al volver a analizar ese dominio.
