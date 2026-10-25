# Cálculos — Base

<!-- revision:a99e24d1f2dcb0667de7c588eab3b07ecdd55f5a974e1a9f804c36f3e31dff4d -->
**Fuente:** `Base.txt`  
**Calculado:** 2026-10-25 06:29:23 UTC  
**Estado:** SAT  
**Motor:** PySAT (Glucose3)

## Átomos

- p: es de día
- q: voy a trabajar
- r: llueve

## Reglas: texto, lógica y FNC

### R1

- Texto: Si es de día, entonces voy a trabajar.
- Lógica: `p → q`
- FNC: `(¬p ∨ q)`

### R2

- Texto: Si llueve, entonces no voy a trabajar.
- Lógica: `r → ¬q`
- FNC: `(¬r ∨ ¬q)`

### R3

- Texto: Es de día.
- Lógica: `p`
- FNC: `p`

## FNC completa

`(¬p ∨ q) ∧ (¬r ∨ ¬q) ∧ p`

## Cláusulas numéricas

`[[-1, 2], [-3, -2], [1]]`

## DIMACS

```dimacs
p cnf 3 3
-1 2 0
-3 -2 0
1 0
```

## Satisfacibilidad

- Solver: **SAT**
- Árbol: **SAT**
- ¿Coinciden?: **Sí**

### Mundos del solver (valores V/F)

1. p=V, q=V, r=F

## Árbol semántico

- Ramas abiertas: 1
- Ramas cerradas: 2
- Nodos generados: 8

### Desarrollo de nodos

| Nodo | Padre | Regla/origen | Expresión | Estado |
|---|---|---|---|---|
| N1 | — | Conjunto de reglas | (p → q) ∧ (r → ¬q) ∧ p | normal |
| N2 | N1 | R1 | p → q | normal |
| N3 | N2 | R2 | r → ¬q | normal |
| N4 | N3 | R3 | p | normal |
| N5 | N4 | R1 | ¬p | cerrada |
| N6 | N4 | R1 | q | normal |
| N7 | N6 | R2 | ¬r | abierta |
| N8 | N6 | R2 | ¬q | cerrada |

### Contradicciones

- N5: p y su negación (N4 / N5).
- N8: q y su negación (N6 / N8).

El TXT es la fuente editable. Este reporte se reemplaza al volver a analizar ese dominio.
