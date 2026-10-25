# Cálculos — prueba_03_control_acceso

<!-- revision:f056ec0fb935d8f09b3f5465507fe2666df9b357a8fb08d0ff4ebfb3d4287146 -->
**Fuente:** `prueba_03_control_acceso.txt`  
**Calculado:** 2026-10-25 05:15:52 UTC  
**Estado:** SAT  
**Motor:** PySAT (Glucose3)

## Átomos

- X1: El boton funciona
- X2: el sensor detecta presencia
- X3: la puerta se activa
- X4: el motor gira
- X5: el registro inicia ciclo
- X6: El sistema falla

## Reglas: texto, lógica y FNC

### R1

- Texto: El boton funciona o el sensor detecta presencia.
- Lógica: `X1 ∨ X2`
- FNC: `(X1 ∨ X2)`

### R2

- Texto: Si el boton funciona, entonces la puerta se activa.
- Lógica: `X1 → X3`
- FNC: `(¬X1 ∨ X3)`

### R3

- Texto: Si el sensor detecta presencia, entonces el motor gira.
- Lógica: `X2 → X4`
- FNC: `(¬X2 ∨ X4)`

### R4

- Texto: Si la puerta se activa, entonces el registro inicia ciclo.
- Lógica: `X3 → X5`
- FNC: `(¬X3 ∨ X5)`

### R5

- Texto: El sistema no falla.
- Lógica: `¬X6`
- FNC: `¬X6`

## FNC completa

`(X1 ∨ X2) ∧ (¬X1 ∨ X3) ∧ (¬X2 ∨ X4) ∧ (¬X3 ∨ X5) ∧ ¬X6`

## Cláusulas numéricas

`[[1, 2], [-1, 3], [-2, 4], [-3, 5], [-6]]`

## DIMACS

```dimacs
p cnf 6 5
1 2 0
-1 3 0
-2 4 0
-3 5 0
-6 0
```

## Satisfacibilidad

- Solver: **SAT**
- Árbol: **SAT**
- ¿Coinciden?: **Sí**

### Mundos del solver (valores V/F)

1. X1=F, X2=V, X3=F, X4=V, X5=F, X6=F
2. X1=F, X2=V, X3=F, X4=V, X5=V, X6=F
3. X1=F, X2=V, X3=V, X4=V, X5=V, X6=F
4. X1=V, X2=V, X3=V, X4=V, X5=V, X6=F
5. X1=V, X2=F, X3=V, X4=V, X5=V, X6=F
6. X1=V, X2=F, X3=V, X4=F, X5=V, X6=F

## Árbol semántico

- Ramas abiertas: 5
- Ramas cerradas: 6
- Nodos generados: 26

### Desarrollo de nodos

| Nodo | Padre | Regla/origen | Expresión | Estado |
|---|---|---|---|---|
| N1 | — | Conjunto de reglas | (X1 ∨ X2) ∧ (X1 → X3) ∧ (X2 → X4) ∧ (X3 → X5) ∧ ¬X6 | normal |
| N2 | N1 | R1 | X1 ∨ X2 | normal |
| N3 | N2 | R2 | X1 → X3 | normal |
| N4 | N3 | R3 | X2 → X4 | normal |
| N5 | N4 | R4 | X3 → X5 | normal |
| N6 | N5 | R5 | ¬X6 | normal |
| N7 | N6 | R1 | X1 | normal |
| N8 | N6 | R1 | X2 | normal |
| N9 | N7 | R2 | ¬X1 | cerrada |
| N10 | N7 | R2 | X3 | normal |
| N11 | N10 | R3 | ¬X2 | normal |
| N12 | N10 | R3 | X4 | normal |
| N13 | N11 | R4 | ¬X3 | cerrada |
| N14 | N11 | R4 | X5 | abierta |
| N15 | N12 | R4 | ¬X3 | cerrada |
| N16 | N12 | R4 | X5 | abierta |
| N17 | N8 | R2 | ¬X1 | normal |
| N18 | N8 | R2 | X3 | normal |
| N19 | N17 | R3 | ¬X2 | cerrada |
| N20 | N17 | R3 | X4 | normal |
| N21 | N20 | R4 | ¬X3 | abierta |
| N22 | N20 | R4 | X5 | abierta |
| N23 | N18 | R3 | ¬X2 | cerrada |
| N24 | N18 | R3 | X4 | normal |
| N25 | N24 | R4 | ¬X3 | cerrada |
| N26 | N24 | R4 | X5 | abierta |

### Contradicciones

- N9: X1 y su negación (N7 / N9).
- N13: X3 y su negación (N10 / N13).
- N15: X3 y su negación (N10 / N15).
- N19: X2 y su negación (N8 / N19).
- N23: X2 y su negación (N8 / N23).
- N25: X3 y su negación (N18 / N25).

El TXT es la fuente editable. Este reporte se reemplaza al volver a analizar ese dominio.
