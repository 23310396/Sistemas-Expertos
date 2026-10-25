# Sistemas Expertos — Segundo Parcial

Aplicación de razonamiento lógico desarrollada en Python. Identifica átomos y reglas escritas en español controlado, construye un árbol semántico con contradicciones, transforma las reglas a FNC y las verifica mediante SAT. La interfaz permite consultar conclusiones y añadir reglas.

## Dominios y archivos

Cada problema se guarda dentro de `dominios/`:

- `nombre.txt`: **fuente editable** con las reglas del problema.
- `nombre.calculos.md`: reporte generado automáticamente al analizar. Incluye átomos, reglas simbólicas, FNC por regla y completa, cláusulas, DIMACS, SAT/UNSAT, mundos y desarrollo del árbol.

El reporte **se sobrescribe** al volver a analizar el mismo dominio; no se generan copias numeradas. Si el TXT cambia, el reporte anterior se considera desactualizado hasta calcular de nuevo.

En la interfaz puedes elegir un dominio existente o crear uno nuevo, escribir reglas y presionar **Analizar problema**. Los cambios del editor se guardan automáticamente en el TXT. Cuando editas el TXT directamente en Codespaces, la interfaz revisa los cambios periódicamente y recarga el dominio. Si ambos lados fueron editados a la vez, avisa del conflicto y **no sobrescribe** el archivo externo: utiliza ↻ para recargarlo, descartando los cambios locales si lo confirmas.

Los nombres nuevos admiten letras sin acentos, números, guiones y guiones bajos. Se conservan dominios independientes.

## Ejecutar en GitHub Codespaces

Desde la carpeta `Segundo Parcial`:

```bash
python -m src.web
```

Abre el puerto **5000** desde *Puertos* (déjalo privado para evitar que otros editen tus dominios). Para usar otro puerto: `python -m src.web 5001`.

Para utilizar PySAT/Glucose3 de forma opcional:

```bash
python -m pip install python-sat
```

Sin PySAT, el programa usa DPLL implementado en Python.

## Consola y pruebas

```bash
python -m src.main dominios/entrada.txt
python -m unittest discover -s tests -v
```

Puedes indicar cualquier otro archivo TXT al ejecutar `src.main`. El guardado automático de cálculos corresponde a **la interfaz web**, no al comando de consola.

El analizador acepta construcciones como `Si P, entonces Q`, `P y Q`, `P o Q`, negaciones, equivalencias `P si y solo si Q` y agrupaciones con paréntesis. No interpreta cualquier redacción libre; las entradas no admitidas se notifican. Los árboles, la FNC y los mundos tienen límites para controlar el tiempo y la memoria.

`src/` contiene los motores y servidor, `static/` contiene HTML/CSS/JavaScript, `tests/` las pruebas y `dominios/` los problemas con sus reportes.

## Rúbrica de árboles semánticos

Las fórmulas y los átomos se muestran como `p, q, r…` para facilitar su lectura; internamente se conservan los identificadores `X1, X2…` que permiten construir las cláusulas numéricas de DIMACS. El árbol muestra cuáles fórmulas ya fueron aplicadas (`✓ DESARROLLADA`), las ramas abiertas, las cerradas y las contradicciones. También interpreta `si y solo si` (`↔`) y su negación.

Ejemplo mínimo del profesor: `Si es de día, entonces voy a trabajar. Si llueve, entonces no voy a trabajar. Es de día.` Produce 2 ramas cerradas, 1 abierta y el modelo `p=V, q=V, r=F`.
