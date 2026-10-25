# Cálculos — prueba_02_control_calidad

<!-- revision:60c49c0ec0d34f19a3f9c1f6217a7936a859b0a9e9293f78f664cb1135c1a7e9 -->
**Fuente:** `prueba_02_control_calidad.txt`  
**Calculado:** 2026-10-25 05:14:54 UTC  
**Estado:** SAT  
**Motor:** PySAT (Glucose3)

## Átomos

- X1: la camara detecta defecto
- X2: el sensor detecta falla
- X3: el robot se detiene
- X4: la alarma se activa
- X5: El motor funciona
- X6: El motor falla

## Reglas: texto, lógica y FNC

### R1

- Texto: Si la camara detecta defecto o el sensor detecta falla, entonces el robot se detiene.
- Lógica: `(X1 ∨ X2) → X3`
- FNC: `(¬X1 ∨ X3) ∧ (¬X2 ∨ X3)`

### R2

- Texto: Si el robot se detiene, entonces la alarma se activa.
- Lógica: `X3 → X4`
- FNC: `(¬X3 ∨ X4)`

### R3

- Texto: La camara detecta defecto o el sensor detecta falla.
- Lógica: `X1 ∨ X2`
- FNC: `(X1 ∨ X2)`

### R4

- Texto: El motor funciona.
- Lógica: `X5`
- FNC: `X5`

### R5

- Texto: El motor no falla.
- Lógica: `¬X6`
- FNC: `¬X6`

## FNC completa

`(¬X1 ∨ X3) ∧ (¬X2 ∨ X3) ∧ (¬X3 ∨ X4) ∧ (X1 ∨ X2) ∧ X5 ∧ ¬X6`

## Cláusulas numéricas

`[[-1, 3], [-2, 3], [-3, 4], [1, 2], [5], [-6]]`

## DIMACS

```dimacs
p cnf 6 6
-1 3 0
-2 3 0
-3 4 0
1 2 0
5 0
-6 0
```

## Satisfacibilidad

- Solver: **SAT**
- Árbol: **SAT**
- ¿Coinciden?: **Sí**

### Mundos del solver (valores V/F)

1. X1=F, X2=V, X3=V, X4=V, X5=V, X6=F
2. X1=V, X2=V, X3=V, X4=V, X5=V, X6=F
3. X1=V, X2=F, X3=V, X4=V, X5=V, X6=F

## Árbol semántico

- Ramas abiertas: 2
- Ramas cerradas: 5
- Nodos generados: 20

### Desarrollo de nodos

| Nodo | Padre | Regla/origen | Expresión | Estado |
|---|---|---|---|---|
| N1 | — | Conjunto de reglas | ((X1 ∨ X2) → X3) ∧ (X3 → X4) ∧ (X1 ∨ X2) ∧ X5 ∧ ¬X6 | normal |
| N2 | N1 | R1 | (X1 ∨ X2) → X3 | normal |
| N3 | N2 | R2 | X3 → X4 | normal |
| N4 | N3 | R3 | X1 ∨ X2 | normal |
| N5 | N4 | R4 | X5 | normal |
| N6 | N5 | R5 | ¬X6 | normal |
| N7 | N6 | R1 | ¬(X1 ∨ X2) | normal |
| N8 | N6 | R1 | X3 | normal |
| N9 | N7 | R1 | ¬X1 | normal |
| N10 | N9 | R1 | ¬X2 | normal |
| N11 | N10 | R2 | ¬X3 | normal |
| N12 | N10 | R2 | X4 | normal |
| N13 | N11 | R3 | X1 | cerrada |
| N14 | N11 | R3 | X2 | cerrada |
| N15 | N12 | R3 | X1 | cerrada |
| N16 | N12 | R3 | X2 | cerrada |
| N17 | N8 | R2 | ¬X3 | cerrada |
| N18 | N8 | R2 | X4 | normal |
| N19 | N18 | R3 | X1 | abierta |
| N20 | N18 | R3 | X2 | abierta |

### Contradicciones

- N13: X1 y su negación (N9 / N13).
- N14: X2 y su negación (N10 / N14).
- N15: X1 y su negación (N9 / N15).
- N16: X2 y su negación (N10 / N16).
- N17: X3 y su negación (N8 / N17).

El TXT es la fuente editable. Este reporte se reemplaza al volver a analizar ese dominio.
