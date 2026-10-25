# Cálculos — prueba_04_incompatibilidad_indirecta

<!-- revision:7693e382bc19f0b41099815e6b720bf053d807dbe5acefc5f89ec5f747f3e11d -->
**Fuente:** `prueba_04_incompatibilidad_indirecta.txt`  
**Calculado:** 2026-10-25 05:33:31 UTC  
**Estado:** UNSAT  
**Motor:** PySAT (Glucose3)

## Átomos

- X1: el sensor detecta presencia
- X2: el robot inicia ciclo
- X3: la alarma se activa
- X4: el motor se detiene

## Reglas: texto, lógica y FNC

### R1

- Texto: Si el sensor detecta presencia, entonces el robot inicia ciclo.
- Lógica: `X1 → X2`
- FNC: `(¬X1 ∨ X2)`

### R2

- Texto: Si el robot inicia ciclo, entonces la alarma se activa.
- Lógica: `X2 → X3`
- FNC: `(¬X2 ∨ X3)`

### R3

- Texto: Si la alarma se activa, entonces el motor se detiene.
- Lógica: `X3 → X4`
- FNC: `(¬X3 ∨ X4)`

### R4

- Texto: El sensor detecta presencia.
- Lógica: `X1`
- FNC: `X1`

### R5

- Texto: El motor no se detiene.
- Lógica: `¬X4`
- FNC: `¬X4`

## FNC completa

`(¬X1 ∨ X2) ∧ (¬X2 ∨ X3) ∧ (¬X3 ∨ X4) ∧ X1 ∧ ¬X4`

## Cláusulas numéricas

`[[-1, 2], [-2, 3], [-3, 4], [1], [-4]]`

## DIMACS

```dimacs
p cnf 4 5
-1 2 0
-2 3 0
-3 4 0
1 0
-4 0
```

## Satisfacibilidad

- Solver: **UNSAT**
- Árbol: **UNSAT**
- ¿Coinciden?: **Sí**

### Mundos del solver (valores V/F)

Ninguno.

## Árbol semántico

- Ramas abiertas: 0
- Ramas cerradas: 4
- Nodos generados: 12

### Desarrollo de nodos

| Nodo | Padre | Regla/origen | Expresión | Estado |
|---|---|---|---|---|
| N1 | — | Conjunto de reglas | (X1 → X2) ∧ (X2 → X3) ∧ (X3 → X4) ∧ X1 ∧ ¬X4 | normal |
| N2 | N1 | R1 | X1 → X2 | normal |
| N3 | N2 | R2 | X2 → X3 | normal |
| N4 | N3 | R3 | X3 → X4 | normal |
| N5 | N4 | R4 | X1 | normal |
| N6 | N5 | R5 | ¬X4 | normal |
| N7 | N6 | R1 | ¬X1 | cerrada |
| N8 | N6 | R1 | X2 | normal |
| N9 | N8 | R2 | ¬X2 | cerrada |
| N10 | N8 | R2 | X3 | normal |
| N11 | N10 | R3 | ¬X3 | cerrada |
| N12 | N10 | R3 | X4 | cerrada |

### Contradicciones

- N7: X1 y su negación (N5 / N7).
- N9: X2 y su negación (N8 / N9).
- N11: X3 y su negación (N10 / N11).
- N12: X4 y su negación (N6 / N12).

El TXT es la fuente editable. Este reporte se reemplaza al volver a analizar ese dominio.
