# Cálculos — prueba_05_negacion_compuesta

<!-- revision:838aa63f58f0f04c5ee1261f9320411b7df1170ec0bcd56a29c01b439306d61e -->
**Fuente:** `prueba_05_negacion_compuesta.txt`  
**Calculado:** 2026-10-25 05:44:36 UTC  
**Estado:** SAT  
**Motor:** PySAT (Glucose3)

## Átomos

- X1: el motor funciona
- X2: la alarma se activa
- X3: el ventilador gira
- X4: el robot se detiene
- X5: El sensor detecta presencia
- X6: el sensor detecta falla

## Reglas: texto, lógica y FNC

### R1

- Texto: No es cierto que el motor funciona y la alarma se activa.
- Lógica: `¬(X1 ∧ X2)`
- FNC: `(¬X1 ∨ ¬X2)`

### R2

- Texto: El motor funciona.
- Lógica: `X1`
- FNC: `X1`

### R3

- Texto: Si el motor funciona, entonces el ventilador gira.
- Lógica: `X1 → X3`
- FNC: `(¬X1 ∨ X3)`

### R4

- Texto: Si el ventilador gira, entonces el robot se detiene.
- Lógica: `X3 → X4`
- FNC: `(¬X3 ∨ X4)`

### R5

- Texto: El sensor detecta presencia o el sensor detecta falla.
- Lógica: `X5 ∨ X6`
- FNC: `(X5 ∨ X6)`

## FNC completa

`(¬X1 ∨ ¬X2) ∧ X1 ∧ (¬X1 ∨ X3) ∧ (¬X3 ∨ X4) ∧ (X5 ∨ X6)`

## Cláusulas numéricas

`[[-1, -2], [1], [-1, 3], [-3, 4], [5, 6]]`

## DIMACS

```dimacs
p cnf 6 5
-1 -2 0
1 0
-1 3 0
-3 4 0
5 6 0
```

## Satisfacibilidad

- Solver: **SAT**
- Árbol: **SAT**
- ¿Coinciden?: **Sí**

### Mundos del solver (valores V/F)

1. X1=V, X2=F, X3=V, X4=V, X5=V, X6=F
2. X1=V, X2=F, X3=V, X4=V, X5=V, X6=V
3. X1=V, X2=F, X3=V, X4=V, X5=F, X6=V

## Árbol semántico

- Ramas abiertas: 2
- Ramas cerradas: 3
- Nodos generados: 14

### Desarrollo de nodos

| Nodo | Padre | Regla/origen | Expresión | Estado |
|---|---|---|---|---|
| N1 | — | Conjunto de reglas | ¬(X1 ∧ X2) ∧ X1 ∧ (X1 → X3) ∧ (X3 → X4) ∧ (X5 ∨ X6) | normal |
| N2 | N1 | R1 | ¬(X1 ∧ X2) | normal |
| N3 | N2 | R2 | X1 | normal |
| N4 | N3 | R3 | X1 → X3 | normal |
| N5 | N4 | R4 | X3 → X4 | normal |
| N6 | N5 | R5 | X5 ∨ X6 | normal |
| N7 | N6 | R1 | ¬X1 | cerrada |
| N8 | N6 | R1 | ¬X2 | normal |
| N9 | N8 | R3 | ¬X1 | cerrada |
| N10 | N8 | R3 | X3 | normal |
| N11 | N10 | R4 | ¬X3 | cerrada |
| N12 | N10 | R4 | X4 | normal |
| N13 | N12 | R5 | X5 | abierta |
| N14 | N12 | R5 | X6 | abierta |

### Contradicciones

- N7: X1 y su negación (N3 / N7).
- N9: X1 y su negación (N3 / N9).
- N11: X3 y su negación (N10 / N11).

El TXT es la fuente editable. Este reporte se reemplaza al volver a analizar ese dominio.
