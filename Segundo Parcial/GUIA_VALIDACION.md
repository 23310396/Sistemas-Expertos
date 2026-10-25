# Guía de validación — Sistema Experto

Este paquete contiene **9 archivos TXT** para copiar directamente a la carpeta `dominios/`. No incluye reportes prehechos: al presionar **Analizar**, el programa debe generar un `.calculos.md` del mismo nombre.

## Instalación

Desde `Segundo Parcial`, descomprime `Pruebas_Dominios_Sistemas_Expertos.zip` con `unzip -o Pruebas_Dominios_Sistemas_Expertos.zip -d .` y recarga la lista de dominios desde la interfaz (o actualiza el navegador).

Selecciona el dominio, pulsa **Analizar**, revisa Árbol/FNC/SAT y después abre Consultas. Si el dominio requiere regeneración, el reporte guardado debe reemplazarse y marcarse actualizado.

## Resultados verificados con el código actual

| Dominio | Átomos | Reglas | Estado | Ramas abiertas/cerradas | Mundos en árbol |
|---|---:|---:|---|---:|---:|
| `prueba_01_linea_ensamble` | 6 | 6 | SAT | 1/5 | 1 |
| `prueba_02_control_calidad` | 6 | 5 | SAT | 2/5 | 3 |
| `prueba_03_control_acceso` | 6 | 5 | SAT | 5/6 | 6 |
| `prueba_04_incompatibilidad_indirecta` | 4 | 5 | UNSAT | 0/4 | 0 |
| `prueba_05_negacion_compuesta` | 6 | 5 | SAT | 2/3 | 3 |
| `prueba_06_conjunciones_anidadas` | 5 | 5 | SAT | 2/6 | 3 |
| `prueba_07_estres_ramas` | 14 | 7 | SAT | 128/0 | 48 (truncados) |
| `prueba_08_limite_proteccion` | — | 9 | **ERROR ESPERADO**: límite 450 nodos | — | — |
| `prueba_09_error_formato` | — | 1 | **ERROR ESPERADO**: falta agrupar `y/o` | — | — |

Las cuentas se comprobaron ejecutando el motor actual. Las ramas abiertas no equivalen necesariamente al número total de mundos; algunas ramas dejan variables libres.

## Preguntas que debes introducir (copiar el texto de la columna Consulta)

Las preguntas son **proposiciones lógicas**. Puedes escribirlas con o sin signos de interrogación. El programa comprueba si se deducen de las reglas.

### `prueba_01_linea_ensamble` — Línea de ensamble — cadena de inferencias

| Consulta exacta | Resultado esperado |
|---|---|
| `el actuador activa prensa` | **DEMOSTRADA** |
| `el robot no inicia ciclo` | **REFUTADA** |
| `la alarma se activa` | **INDETERMINADA** |

La última consulta menciona un átomo que no está en el dominio: debe salir **INDETERMINADA**, y el sistema lo mostrará como átomo nuevo solo para esa consulta.

### `prueba_02_control_calidad` — Inspección de calidad — múltiples causas

| Consulta exacta | Resultado esperado |
|---|---|
| `el robot se detiene` | **DEMOSTRADA** |
| `la alarma se activa` | **DEMOSTRADA** |
| `la camara detecta defecto` | **INDETERMINADA** |
| `el sensor detecta falla` | **INDETERMINADA** |
| `el motor falla` | **REFUTADA** |

### `prueba_03_control_acceso` — Control de acceso — alternativas y contraejemplos

| Consulta exacta | Resultado esperado |
|---|---|
| `el boton funciona` | **INDETERMINADA** |
| `el sensor detecta presencia` | **INDETERMINADA** |
| `la puerta se activa o el motor gira` | **DEMOSTRADA** |
| `el sistema falla` | **REFUTADA** |
| `el registro inicia ciclo` | **INDETERMINADA** |

### `prueba_04_incompatibilidad_indirecta` — Paro industrial — contradicción indirecta

| Consulta exacta | Resultado esperado |
|---|---|
| `el robot inicia ciclo` | **INCONSISTENTE** |
| `el motor se detiene` | **INCONSISTENTE** |

### `prueba_05_negacion_compuesta` — Seguridad de equipo — negación de conjunción

| Consulta exacta | Resultado esperado |
|---|---|
| `la alarma se activa` | **REFUTADA** |
| `el robot se detiene` | **DEMOSTRADA** |
| `el sensor detecta falla` | **INDETERMINADA** |
| `el motor funciona y la alarma se activa` | **REFUTADA** |

### `prueba_06_conjunciones_anidadas` — Diagnóstico combinado — lógica agrupada

| Consulta exacta | Resultado esperado |
|---|---|
| `el robot se detiene` | **DEMOSTRADA** |
| `el operador revisa equipo` | **DEMOSTRADA** |
| `el sensor detecta falla` | **INDETERMINADA** |
| `el motor no funciona` | **REFUTADA** |

### `prueba_07_estres_ramas` — Estrés: 7 pares de alternativas

| Consulta exacta | Resultado esperado |
|---|---|
| `el sensor detecta zona1 o el motor gira zona1` | **DEMOSTRADA** |
| `el sensor detecta zona1` | **INDETERMINADA** |
| `el sensor no detecta zona1` | **INDETERMINADA** |

Aquí se generan **262 nodos**, **128 ramas abiertas**, **48 mundos visibles en el árbol** (límite de interfaz) y **16 soluciones SAT visibles**, con indicador de que hay más. Que el solver indique SAT y las listas estén truncadas es correcto. Hay **3^7 = 2187 asignaciones compatibles** en total para las 14 variables (no se enumeran todas).

## Pruebas que deben fallar de forma controlada

### `prueba_08_limite_proteccion`

Contiene **9 disyunciones independientes**. Al pulsar Analizar, la respuesta esperada es un mensaje como `El árbol superó 450 nodos`. **No debe producir una solución parcial ni un nuevo reporte `.calculos.md`**. El límite es de visualización y procesamiento del árbol; la FNC/SAT podrían resolver fórmulas más grandes, pero esta pantalla analiza el árbol primero.

### `prueba_09_error_formato`

Mezcla `y` y `o` sin paréntesis. Debe **rechazar la oración** e indicar que hay que agrupar los operadores. No debe mostrar un resultado SAT como si la fórmula se hubiera interpretado correctamente.

## Prueba de modificación de reglas y guardado

En `prueba_02_control_calidad`, añade desde la interfaz `La camara no detecta defecto.` y pulsa **Analizar**. Debe seguir SAT, pero `el sensor detecta falla` pasa a ser **DEMOSTRADA**. Luego agrega `El sensor no detecta falla.` y vuelve a analizar: debe pasar a **UNSAT** e indicar consultas **INCONSISTENTES**.

Verifica que el TXT contenga ambas reglas agregadas, que exista **un único** `.calculos.md` correspondiente y que su contenido se actualice al recalcular. Si quieres volver al ejemplo original, reemplaza el TXT por el archivo original del ZIP y analiza de nuevo.

## Cómo redactar las consultas

- ✅ Proposición: `el robot se detiene`, `el motor no funciona`, `la camara detecta defecto o el sensor detecta falla`.
- ✅ Fórmula controlada: `Si el sensor detecta presencia, entonces el robot inicia ciclo` y referencias a átomos ya identificados como `X1`.
- ✅ Se admite `¿... ?`, un punto final, conjunciones/disyunciones y negaciones con la gramática del parser.
- ⚠️ Se comparan proposiciones por **texto normalizado**, no por significado; `el robot se detiene` y `el robot se para` son átomos diferentes. Las reformulaciones pueden dar **INDETERMINADA**.
- ⚠️ No hagas preguntas de explicación general como `¿Por qué se detuvo?`, `¿Qué pasa si...?`, `¿Se puede deducir que...?`. El programa no responde preguntas abiertas: evalúa la afirmación escrita.
- ⚠️ No reconoce `R1` como consulta a una regla. `X1` sí es una referencia válida cuando ya existe. Tampoco entiende directamente `X1 → X2` ni `X1 ∧ X2` como entrada en notación simbólica: escribe la expresión en español controlado.
- ⚠️ No hay cuantificadores, comparaciones numéricas, sinónimos ni lenguaje causal libre; evita `porque`, `aunque`, `pero`, `cuando` y `si y solo si`.
- 📏 Consulta: máximo **2000 caracteres**. Problema: máximo **20 000 caracteres**, **100 oraciones** y, en esta interfaz, máximo **450 nodos de árbol**, **48 mundos visibles del árbol** y **16 soluciones visibles del solver**.
- ⚠️ Si el dominio es UNSAT, cualquier pregunta debe devolver **INCONSISTENTE**, no demostrada/refutada.

## Confirmación de pruebas

Las salidas SAT/UNSAT, el número de átomos, reglas, ramas y los estados de las consultas se verificaron ejecutando el código Python de la versión con dominios y navegación del árbol. Las pruebas `08` y `09` son errores esperados. Se probaron con el solucionador DPLL; en Codespaces puedes utilizar PySAT/Glucose3 y los resultados lógicos deben coincidir.
