# Cálculos — prueba_07_estres_ramas

<!-- revision:93f1a64eb3d8f13d0603958b288b727e28e33a2fbc7ca923c504fc23111733b3 -->
**Fuente:** `prueba_07_estres_ramas.txt`  
**Calculado:** 2026-10-25 05:46:53 UTC  
**Estado:** SAT  
**Motor:** PySAT (Glucose3)

## Átomos

- X1: El sensor detecta zona1
- X2: el motor gira zona1
- X3: El sensor detecta zona2
- X4: el motor gira zona2
- X5: El sensor detecta zona3
- X6: el motor gira zona3
- X7: El sensor detecta zona4
- X8: el motor gira zona4
- X9: El sensor detecta zona5
- X10: el motor gira zona5
- X11: El sensor detecta zona6
- X12: el motor gira zona6
- X13: El sensor detecta zona7
- X14: el motor gira zona7

## Reglas: texto, lógica y FNC

### R1

- Texto: El sensor detecta zona1 o el motor gira zona1.
- Lógica: `X1 ∨ X2`
- FNC: `(X1 ∨ X2)`

### R2

- Texto: El sensor detecta zona2 o el motor gira zona2.
- Lógica: `X3 ∨ X4`
- FNC: `(X3 ∨ X4)`

### R3

- Texto: El sensor detecta zona3 o el motor gira zona3.
- Lógica: `X5 ∨ X6`
- FNC: `(X5 ∨ X6)`

### R4

- Texto: El sensor detecta zona4 o el motor gira zona4.
- Lógica: `X7 ∨ X8`
- FNC: `(X7 ∨ X8)`

### R5

- Texto: El sensor detecta zona5 o el motor gira zona5.
- Lógica: `X9 ∨ X10`
- FNC: `(X9 ∨ X10)`

### R6

- Texto: El sensor detecta zona6 o el motor gira zona6.
- Lógica: `X11 ∨ X12`
- FNC: `(X11 ∨ X12)`

### R7

- Texto: El sensor detecta zona7 o el motor gira zona7.
- Lógica: `X13 ∨ X14`
- FNC: `(X13 ∨ X14)`

## FNC completa

`(X1 ∨ X2) ∧ (X3 ∨ X4) ∧ (X5 ∨ X6) ∧ (X7 ∨ X8) ∧ (X9 ∨ X10) ∧ (X11 ∨ X12) ∧ (X13 ∨ X14)`

## Cláusulas numéricas

`[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12], [13, 14]]`

## DIMACS

```dimacs
p cnf 14 7
1 2 0
3 4 0
5 6 0
7 8 0
9 10 0
11 12 0
13 14 0
```

## Satisfacibilidad

- Solver: **SAT**
- Árbol: **SAT**
- ¿Coinciden?: **Sí**

### Mundos del solver (valores V/F)

1. X1=V, X2=F, X3=V, X4=F, X5=V, X6=F, X7=V, X8=F, X9=V, X10=F, X11=V, X12=F, X13=V, X14=F
2. X1=V, X2=V, X3=V, X4=F, X5=V, X6=F, X7=V, X8=F, X9=V, X10=F, X11=V, X12=F, X13=V, X14=F
3. X1=V, X2=V, X3=V, X4=V, X5=V, X6=F, X7=V, X8=F, X9=V, X10=F, X11=V, X12=F, X13=V, X14=F
4. X1=V, X2=V, X3=V, X4=V, X5=V, X6=F, X7=V, X8=F, X9=V, X10=V, X11=V, X12=F, X13=V, X14=F
5. X1=V, X2=V, X3=V, X4=V, X5=V, X6=F, X7=V, X8=F, X9=F, X10=V, X11=V, X12=F, X13=V, X14=F
6. X1=V, X2=V, X3=V, X4=V, X5=V, X6=F, X7=V, X8=F, X9=F, X10=V, X11=V, X12=V, X13=V, X14=F
7. X1=V, X2=V, X3=V, X4=V, X5=V, X6=F, X7=V, X8=F, X9=F, X10=V, X11=F, X12=V, X13=V, X14=F
8. X1=V, X2=V, X3=V, X4=V, X5=V, X6=F, X7=V, X8=F, X9=F, X10=V, X11=F, X12=V, X13=V, X14=V
9. X1=V, X2=V, X3=V, X4=F, X5=V, X6=F, X7=V, X8=F, X9=F, X10=V, X11=F, X12=V, X13=V, X14=V
10. X1=V, X2=V, X3=V, X4=F, X5=V, X6=F, X7=V, X8=F, X9=F, X10=V, X11=F, X12=V, X13=F, X14=V
11. X1=F, X2=V, X3=V, X4=F, X5=V, X6=F, X7=V, X8=F, X9=F, X10=V, X11=F, X12=V, X13=F, X14=V
12. X1=F, X2=V, X3=V, X4=F, X5=V, X6=F, X7=V, X8=V, X9=F, X10=V, X11=F, X12=V, X13=F, X14=V
13. X1=F, X2=V, X3=V, X4=F, X5=V, X6=F, X7=F, X8=V, X9=F, X10=V, X11=F, X12=V, X13=F, X14=V
14. X1=F, X2=V, X3=V, X4=F, X5=V, X6=F, X7=F, X8=V, X9=F, X10=V, X11=V, X12=V, X13=F, X14=V
15. X1=F, X2=V, X3=V, X4=F, X5=V, X6=F, X7=F, X8=V, X9=F, X10=V, X11=V, X12=F, X13=F, X14=V
16. X1=F, X2=V, X3=V, X4=V, X5=V, X6=F, X7=F, X8=V, X9=F, X10=V, X11=V, X12=F, X13=F, X14=V

Se muestran solo las primeras soluciones (límite de visualización).

## Árbol semántico

- Ramas abiertas: 128
- Ramas cerradas: 0
- Nodos generados: 262

### Desarrollo de nodos

| Nodo | Padre | Regla/origen | Expresión | Estado |
|---|---|---|---|---|
| N1 | — | Conjunto de reglas | (X1 ∨ X2) ∧ (X3 ∨ X4) ∧ (X5 ∨ X6) ∧ (X7 ∨ X8) ∧ (X9 ∨ X10) ∧ (X11 ∨ X12) ∧ (X13 ∨ X14) | normal |
| N2 | N1 | R1 | X1 ∨ X2 | normal |
| N3 | N2 | R2 | X3 ∨ X4 | normal |
| N4 | N3 | R3 | X5 ∨ X6 | normal |
| N5 | N4 | R4 | X7 ∨ X8 | normal |
| N6 | N5 | R5 | X9 ∨ X10 | normal |
| N7 | N6 | R6 | X11 ∨ X12 | normal |
| N8 | N7 | R7 | X13 ∨ X14 | normal |
| N9 | N8 | R1 | X1 | normal |
| N10 | N8 | R1 | X2 | normal |
| N11 | N9 | R2 | X3 | normal |
| N12 | N9 | R2 | X4 | normal |
| N13 | N11 | R3 | X5 | normal |
| N14 | N11 | R3 | X6 | normal |
| N15 | N13 | R4 | X7 | normal |
| N16 | N13 | R4 | X8 | normal |
| N17 | N15 | R5 | X9 | normal |
| N18 | N15 | R5 | X10 | normal |
| N19 | N17 | R6 | X11 | normal |
| N20 | N17 | R6 | X12 | normal |
| N21 | N19 | R7 | X13 | abierta |
| N22 | N19 | R7 | X14 | abierta |
| N23 | N20 | R7 | X13 | abierta |
| N24 | N20 | R7 | X14 | abierta |
| N25 | N18 | R6 | X11 | normal |
| N26 | N18 | R6 | X12 | normal |
| N27 | N25 | R7 | X13 | abierta |
| N28 | N25 | R7 | X14 | abierta |
| N29 | N26 | R7 | X13 | abierta |
| N30 | N26 | R7 | X14 | abierta |
| N31 | N16 | R5 | X9 | normal |
| N32 | N16 | R5 | X10 | normal |
| N33 | N31 | R6 | X11 | normal |
| N34 | N31 | R6 | X12 | normal |
| N35 | N33 | R7 | X13 | abierta |
| N36 | N33 | R7 | X14 | abierta |
| N37 | N34 | R7 | X13 | abierta |
| N38 | N34 | R7 | X14 | abierta |
| N39 | N32 | R6 | X11 | normal |
| N40 | N32 | R6 | X12 | normal |
| N41 | N39 | R7 | X13 | abierta |
| N42 | N39 | R7 | X14 | abierta |
| N43 | N40 | R7 | X13 | abierta |
| N44 | N40 | R7 | X14 | abierta |
| N45 | N14 | R4 | X7 | normal |
| N46 | N14 | R4 | X8 | normal |
| N47 | N45 | R5 | X9 | normal |
| N48 | N45 | R5 | X10 | normal |
| N49 | N47 | R6 | X11 | normal |
| N50 | N47 | R6 | X12 | normal |
| N51 | N49 | R7 | X13 | abierta |
| N52 | N49 | R7 | X14 | abierta |
| N53 | N50 | R7 | X13 | abierta |
| N54 | N50 | R7 | X14 | abierta |
| N55 | N48 | R6 | X11 | normal |
| N56 | N48 | R6 | X12 | normal |
| N57 | N55 | R7 | X13 | abierta |
| N58 | N55 | R7 | X14 | abierta |
| N59 | N56 | R7 | X13 | abierta |
| N60 | N56 | R7 | X14 | abierta |
| N61 | N46 | R5 | X9 | normal |
| N62 | N46 | R5 | X10 | normal |
| N63 | N61 | R6 | X11 | normal |
| N64 | N61 | R6 | X12 | normal |
| N65 | N63 | R7 | X13 | abierta |
| N66 | N63 | R7 | X14 | abierta |
| N67 | N64 | R7 | X13 | abierta |
| N68 | N64 | R7 | X14 | abierta |
| N69 | N62 | R6 | X11 | normal |
| N70 | N62 | R6 | X12 | normal |
| N71 | N69 | R7 | X13 | abierta |
| N72 | N69 | R7 | X14 | abierta |
| N73 | N70 | R7 | X13 | abierta |
| N74 | N70 | R7 | X14 | abierta |
| N75 | N12 | R3 | X5 | normal |
| N76 | N12 | R3 | X6 | normal |
| N77 | N75 | R4 | X7 | normal |
| N78 | N75 | R4 | X8 | normal |
| N79 | N77 | R5 | X9 | normal |
| N80 | N77 | R5 | X10 | normal |
| N81 | N79 | R6 | X11 | normal |
| N82 | N79 | R6 | X12 | normal |
| N83 | N81 | R7 | X13 | abierta |
| N84 | N81 | R7 | X14 | abierta |
| N85 | N82 | R7 | X13 | abierta |
| N86 | N82 | R7 | X14 | abierta |
| N87 | N80 | R6 | X11 | normal |
| N88 | N80 | R6 | X12 | normal |
| N89 | N87 | R7 | X13 | abierta |
| N90 | N87 | R7 | X14 | abierta |
| N91 | N88 | R7 | X13 | abierta |
| N92 | N88 | R7 | X14 | abierta |
| N93 | N78 | R5 | X9 | normal |
| N94 | N78 | R5 | X10 | normal |
| N95 | N93 | R6 | X11 | normal |
| N96 | N93 | R6 | X12 | normal |
| N97 | N95 | R7 | X13 | abierta |
| N98 | N95 | R7 | X14 | abierta |
| N99 | N96 | R7 | X13 | abierta |
| N100 | N96 | R7 | X14 | abierta |
| N101 | N94 | R6 | X11 | normal |
| N102 | N94 | R6 | X12 | normal |
| N103 | N101 | R7 | X13 | abierta |
| N104 | N101 | R7 | X14 | abierta |
| N105 | N102 | R7 | X13 | abierta |
| N106 | N102 | R7 | X14 | abierta |
| N107 | N76 | R4 | X7 | normal |
| N108 | N76 | R4 | X8 | normal |
| N109 | N107 | R5 | X9 | normal |
| N110 | N107 | R5 | X10 | normal |
| N111 | N109 | R6 | X11 | normal |
| N112 | N109 | R6 | X12 | normal |
| N113 | N111 | R7 | X13 | abierta |
| N114 | N111 | R7 | X14 | abierta |
| N115 | N112 | R7 | X13 | abierta |
| N116 | N112 | R7 | X14 | abierta |
| N117 | N110 | R6 | X11 | normal |
| N118 | N110 | R6 | X12 | normal |
| N119 | N117 | R7 | X13 | abierta |
| N120 | N117 | R7 | X14 | abierta |
| N121 | N118 | R7 | X13 | abierta |
| N122 | N118 | R7 | X14 | abierta |
| N123 | N108 | R5 | X9 | normal |
| N124 | N108 | R5 | X10 | normal |
| N125 | N123 | R6 | X11 | normal |
| N126 | N123 | R6 | X12 | normal |
| N127 | N125 | R7 | X13 | abierta |
| N128 | N125 | R7 | X14 | abierta |
| N129 | N126 | R7 | X13 | abierta |
| N130 | N126 | R7 | X14 | abierta |
| N131 | N124 | R6 | X11 | normal |
| N132 | N124 | R6 | X12 | normal |
| N133 | N131 | R7 | X13 | abierta |
| N134 | N131 | R7 | X14 | abierta |
| N135 | N132 | R7 | X13 | abierta |
| N136 | N132 | R7 | X14 | abierta |
| N137 | N10 | R2 | X3 | normal |
| N138 | N10 | R2 | X4 | normal |
| N139 | N137 | R3 | X5 | normal |
| N140 | N137 | R3 | X6 | normal |
| N141 | N139 | R4 | X7 | normal |
| N142 | N139 | R4 | X8 | normal |
| N143 | N141 | R5 | X9 | normal |
| N144 | N141 | R5 | X10 | normal |
| N145 | N143 | R6 | X11 | normal |
| N146 | N143 | R6 | X12 | normal |
| N147 | N145 | R7 | X13 | abierta |
| N148 | N145 | R7 | X14 | abierta |
| N149 | N146 | R7 | X13 | abierta |
| N150 | N146 | R7 | X14 | abierta |
| N151 | N144 | R6 | X11 | normal |
| N152 | N144 | R6 | X12 | normal |
| N153 | N151 | R7 | X13 | abierta |
| N154 | N151 | R7 | X14 | abierta |
| N155 | N152 | R7 | X13 | abierta |
| N156 | N152 | R7 | X14 | abierta |
| N157 | N142 | R5 | X9 | normal |
| N158 | N142 | R5 | X10 | normal |
| N159 | N157 | R6 | X11 | normal |
| N160 | N157 | R6 | X12 | normal |
| N161 | N159 | R7 | X13 | abierta |
| N162 | N159 | R7 | X14 | abierta |
| N163 | N160 | R7 | X13 | abierta |
| N164 | N160 | R7 | X14 | abierta |
| N165 | N158 | R6 | X11 | normal |
| N166 | N158 | R6 | X12 | normal |
| N167 | N165 | R7 | X13 | abierta |
| N168 | N165 | R7 | X14 | abierta |
| N169 | N166 | R7 | X13 | abierta |
| N170 | N166 | R7 | X14 | abierta |
| N171 | N140 | R4 | X7 | normal |
| N172 | N140 | R4 | X8 | normal |
| N173 | N171 | R5 | X9 | normal |
| N174 | N171 | R5 | X10 | normal |
| N175 | N173 | R6 | X11 | normal |
| N176 | N173 | R6 | X12 | normal |
| N177 | N175 | R7 | X13 | abierta |
| N178 | N175 | R7 | X14 | abierta |
| N179 | N176 | R7 | X13 | abierta |
| N180 | N176 | R7 | X14 | abierta |
| N181 | N174 | R6 | X11 | normal |
| N182 | N174 | R6 | X12 | normal |
| N183 | N181 | R7 | X13 | abierta |
| N184 | N181 | R7 | X14 | abierta |
| N185 | N182 | R7 | X13 | abierta |
| N186 | N182 | R7 | X14 | abierta |
| N187 | N172 | R5 | X9 | normal |
| N188 | N172 | R5 | X10 | normal |
| N189 | N187 | R6 | X11 | normal |
| N190 | N187 | R6 | X12 | normal |
| N191 | N189 | R7 | X13 | abierta |
| N192 | N189 | R7 | X14 | abierta |
| N193 | N190 | R7 | X13 | abierta |
| N194 | N190 | R7 | X14 | abierta |
| N195 | N188 | R6 | X11 | normal |
| N196 | N188 | R6 | X12 | normal |
| N197 | N195 | R7 | X13 | abierta |
| N198 | N195 | R7 | X14 | abierta |
| N199 | N196 | R7 | X13 | abierta |
| N200 | N196 | R7 | X14 | abierta |
| N201 | N138 | R3 | X5 | normal |
| N202 | N138 | R3 | X6 | normal |
| N203 | N201 | R4 | X7 | normal |
| N204 | N201 | R4 | X8 | normal |
| N205 | N203 | R5 | X9 | normal |
| N206 | N203 | R5 | X10 | normal |
| N207 | N205 | R6 | X11 | normal |
| N208 | N205 | R6 | X12 | normal |
| N209 | N207 | R7 | X13 | abierta |
| N210 | N207 | R7 | X14 | abierta |
| N211 | N208 | R7 | X13 | abierta |
| N212 | N208 | R7 | X14 | abierta |
| N213 | N206 | R6 | X11 | normal |
| N214 | N206 | R6 | X12 | normal |
| N215 | N213 | R7 | X13 | abierta |
| N216 | N213 | R7 | X14 | abierta |
| N217 | N214 | R7 | X13 | abierta |
| N218 | N214 | R7 | X14 | abierta |
| N219 | N204 | R5 | X9 | normal |
| N220 | N204 | R5 | X10 | normal |
| N221 | N219 | R6 | X11 | normal |
| N222 | N219 | R6 | X12 | normal |
| N223 | N221 | R7 | X13 | abierta |
| N224 | N221 | R7 | X14 | abierta |
| N225 | N222 | R7 | X13 | abierta |
| N226 | N222 | R7 | X14 | abierta |
| N227 | N220 | R6 | X11 | normal |
| N228 | N220 | R6 | X12 | normal |
| N229 | N227 | R7 | X13 | abierta |
| N230 | N227 | R7 | X14 | abierta |
| N231 | N228 | R7 | X13 | abierta |
| N232 | N228 | R7 | X14 | abierta |
| N233 | N202 | R4 | X7 | normal |
| N234 | N202 | R4 | X8 | normal |
| N235 | N233 | R5 | X9 | normal |
| N236 | N233 | R5 | X10 | normal |
| N237 | N235 | R6 | X11 | normal |
| N238 | N235 | R6 | X12 | normal |
| N239 | N237 | R7 | X13 | abierta |
| N240 | N237 | R7 | X14 | abierta |
| N241 | N238 | R7 | X13 | abierta |
| N242 | N238 | R7 | X14 | abierta |
| N243 | N236 | R6 | X11 | normal |
| N244 | N236 | R6 | X12 | normal |
| N245 | N243 | R7 | X13 | abierta |
| N246 | N243 | R7 | X14 | abierta |
| N247 | N244 | R7 | X13 | abierta |
| N248 | N244 | R7 | X14 | abierta |
| N249 | N234 | R5 | X9 | normal |
| N250 | N234 | R5 | X10 | normal |
| N251 | N249 | R6 | X11 | normal |
| N252 | N249 | R6 | X12 | normal |
| N253 | N251 | R7 | X13 | abierta |
| N254 | N251 | R7 | X14 | abierta |
| N255 | N252 | R7 | X13 | abierta |
| N256 | N252 | R7 | X14 | abierta |
| N257 | N250 | R6 | X11 | normal |
| N258 | N250 | R6 | X12 | normal |
| N259 | N257 | R7 | X13 | abierta |
| N260 | N257 | R7 | X14 | abierta |
| N261 | N258 | R7 | X13 | abierta |
| N262 | N258 | R7 | X14 | abierta |

### Contradicciones

No se detectaron contradicciones en las ramas.

El TXT es la fuente editable. Este reporte se reemplaza al volver a analizar ese dominio.
