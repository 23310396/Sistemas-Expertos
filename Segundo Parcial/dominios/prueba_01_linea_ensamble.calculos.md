# Cálculos — prueba_01_linea_ensamble

<!-- revision:860809e4f1e68a46a9195b66f0faea96b54df677dcc8083a7cdf00fd50539670 -->
**Fuente:** `prueba_01_linea_ensamble.txt`  
**Calculado:** 2026-10-25 06:27:50 UTC  
**Estado:** SAT  
**Motor:** PySAT (Glucose3)

## Átomos

- p: el sensor detecta pieza
- q: el robot inicia ciclo
- r: la camara revisa pieza
- s: el motor funciona
- t: el actuador activa prensa
- u: la banda se detiene

## Reglas: texto, lógica y FNC

### R1

- Texto: Si el sensor detecta pieza, entonces el robot inicia ciclo.
- Lógica: `p → q`
- FNC: `(¬p ∨ q)`

### R2

- Texto: Si el robot inicia ciclo, entonces la camara revisa pieza.
- Lógica: `q → r`
- FNC: `(¬q ∨ r)`

### R3

- Texto: Si la camara revisa pieza y el motor funciona, entonces el actuador activa prensa.
- Lógica: `(r ∧ s) → t`
- FNC: `(¬r ∨ ¬s ∨ t)`

### R4

- Texto: Si el actuador activa prensa, entonces la banda se detiene.
- Lógica: `t → u`
- FNC: `(¬t ∨ u)`

### R5

- Texto: El sensor detecta pieza.
- Lógica: `p`
- FNC: `p`

### R6

- Texto: El motor funciona.
- Lógica: `s`
- FNC: `s`

## FNC completa

`(¬p ∨ q) ∧ (¬q ∨ r) ∧ (¬r ∨ ¬s ∨ t) ∧ (¬t ∨ u) ∧ p ∧ s`

## Cláusulas numéricas

`[[-1, 2], [-2, 3], [-3, -4, 5], [-5, 6], [1], [4]]`

## DIMACS

```dimacs
p cnf 6 6
-1 2 0
-2 3 0
-3 -4 5 0
-5 6 0
1 0
4 0
```

## Satisfacibilidad

- Solver: **SAT**
- Árbol: **SAT**
- ¿Coinciden?: **Sí**

### Mundos del solver (valores V/F)

1. p=V, q=V, r=V, s=V, t=V, u=V

## Árbol semántico

- Ramas abiertas: 1
- Ramas cerradas: 5
- Nodos generados: 17

### Desarrollo de nodos

| Nodo | Padre | Regla/origen | Expresión | Estado |
|---|---|---|---|---|
| N1 | — | Conjunto de reglas | (p → q) ∧ (q → r) ∧ ((r ∧ s) → t) ∧ (t → u) ∧ p ∧ s | normal |
| N2 | N1 | R1 | p → q | normal |
| N3 | N2 | R2 | q → r | normal |
| N4 | N3 | R3 | (r ∧ s) → t | normal |
| N5 | N4 | R4 | t → u | normal |
| N6 | N5 | R5 | p | normal |
| N7 | N6 | R6 | s | normal |
| N8 | N7 | R1 | ¬p | cerrada |
| N9 | N7 | R1 | q | normal |
| N10 | N9 | R2 | ¬q | cerrada |
| N11 | N9 | R2 | r | normal |
| N12 | N11 | R3 | ¬(r ∧ s) | normal |
| N13 | N11 | R3 | t | normal |
| N14 | N12 | R3 | ¬r | cerrada |
| N15 | N12 | R3 | ¬s | cerrada |
| N16 | N13 | R4 | ¬t | cerrada |
| N17 | N13 | R4 | u | abierta |

### Contradicciones

- N8: p y su negación (N6 / N8).
- N10: q y su negación (N9 / N10).
- N14: r y su negación (N11 / N14).
- N15: s y su negación (N7 / N15).
- N16: t y su negación (N13 / N16).

El TXT es la fuente editable. Este reporte se reemplaza al volver a analizar ese dominio.
