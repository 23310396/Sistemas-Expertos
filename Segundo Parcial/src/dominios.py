import hashlib
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from .simbolos import letra, simbolizar

CARPETA = Path(__file__).resolve().parent.parent / 'dominios'
CANDADO = threading.RLock()
NOMBRE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,49}\Z')


class ConflictoDominio(ValueError):
    pass


def rutas(nombre):
    if not isinstance(nombre, str) or not NOMBRE.fullmatch(nombre):
        raise ValueError('Nombre inválido: usa letras, números, guion o guion bajo (máximo 50).')
    return CARPETA / f'{nombre}.txt', CARPETA / f'{nombre}.calculos.md'


def revision(texto):
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()


def escribir(ruta, texto):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                            dir=ruta.parent, prefix='.temporal-', delete=False) as archivo:
        temporal = Path(archivo.name)
        try:
            archivo.write(texto)
            archivo.flush()
            os.fsync(archivo.fileno())
        except Exception:
            temporal.unlink(missing_ok=True)
            raise
    os.replace(temporal, ruta)


def leer(nombre):
    ruta, calculos = rutas(nombre)
    if not ruta.is_file() or ruta.is_symlink() or calculos.is_symlink():
        raise FileNotFoundError('El dominio no existe.')
    texto = ruta.read_text(encoding='utf-8-sig')
    sello = revision(texto)
    vigente = False
    if calculos.is_file():
        with calculos.open('r', encoding='utf-8') as archivo:
            cabecera = ''.join(archivo.readline() for _ in range(8))
        vigente = f'<!-- revision:{sello} -->' in cabecera
    return {'nombre': nombre, 'texto': texto, 'revision': sello,
            'calculado': vigente, 'tiene_calculos': calculos.is_file(),
            'archivo': f'dominios/{nombre}.txt',
            'archivo_calculos': f'dominios/{nombre}.calculos.md'}


def listar():
    CARPETA.mkdir(exist_ok=True)
    return [leer(p.stem) for p in sorted(CARPETA.glob('*.txt')) if p.is_file() and not p.is_symlink() and NOMBRE.fullmatch(p.stem)]


def crear(nombre):
    ruta, _ = rutas(nombre)
    with CANDADO:
        CARPETA.mkdir(exist_ok=True)
        if ruta.exists():
            raise ValueError('Ya existe un dominio con ese nombre.')
        with ruta.open('x', encoding='utf-8') as archivo:
            archivo.write('')
        return leer(nombre)


def comprobar(nombre, revision_esperada):
    if not isinstance(revision_esperada, str):
        raise ValueError('Falta la versión del TXT: recarga el dominio.')
    actual = leer(nombre)
    if actual['revision'] != revision_esperada:
        raise ConflictoDominio('El TXT cambió fuera de la interfaz. Recárgalo para no sobrescribir esos cambios.')
    return actual


def guardar_texto(nombre, texto, revision_esperada):
    if not isinstance(texto, str) or len(texto) > 20000:
        raise ValueError('El texto debe tener como máximo 20 000 caracteres.')
    with CANDADO:
        actual = comprobar(nombre, revision_esperada)
        if texto != actual['texto']:
            ruta, _ = rutas(nombre)
            escribir(ruta, texto)
        return leer(nombre)


def _tabla_mundos(mundos, atomos):
    if not mundos:
        return 'Ninguno.\n'
    renglones = []
    for i, mundo in enumerate(mundos, 1):
        renglones.append(f'{i}. ' + ', '.join(f'{letra(clave)}={"V" if valor else "F"}' for clave, valor in mundo.items()))
    return '\n'.join(renglones) + '\n'


def reporte(nombre, texto, resultado):
    atomos, reglas, fnc, sat, arbol = (resultado[k] for k in ('atomos', 'reglas', 'fnc', 'sat', 'arbol'))
    sello = revision(texto)
    ahora = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    bloques = [
        f'# Cálculos — {nombre}', '',
        f'<!-- revision:{sello} -->',
        f'**Fuente:** `{nombre}.txt`  ',
        f'**Calculado:** {ahora}  ',
        f'**Estado:** {sat["estado"]}  ',
        f'**Motor:** {sat["motor"]}', '',
        '## Átomos', '',
        *[f'- {letra(clave)}: {valor}' for clave, valor in atomos.items()], '',
        '## Reglas: texto, lógica y FNC', ''
    ]
    for regla, conversion in zip(reglas, fnc['reglas']):
        bloques.extend([f'### {regla["id"]}', '', f'- Texto: {regla["texto"]}',
                         f'- Lógica: `{simbolizar(regla["expresion"])}`',
                         f'- FNC: `{simbolizar(conversion["fnc"])}`', ''])
    bloques.extend(['## FNC completa', '', f'`{simbolizar(fnc["expresion"])}`', '',
                    '## Cláusulas numéricas', '', f'`{fnc["clausulas"]}`', '',
                    '## DIMACS', '', '```dimacs', fnc['dimacs'], '```', '',
                    '## Satisfacibilidad', '',
                    f'- Solver: **{sat["estado"]}**',
                    f'- Árbol: **{"SAT" if arbol["compatible"] else "UNSAT"}**',
                    f'- ¿Coinciden?: **{"Sí" if sat["coincide_arbol"] else "No"}**', '',
                    '### Mundos del solver (valores V/F)', '',
                    _tabla_mundos(sat['soluciones'], atomos).strip(),
                    ''])
    if sat.get('hay_mas'):
        bloques.extend(['Se muestran solo las primeras soluciones (límite de visualización).', ''])
    bloques.extend(['## Árbol semántico', '',
                    f'- Ramas abiertas: {resultado["resumen"]["abiertas"]}',
                    f'- Ramas cerradas: {resultado["resumen"]["cerradas"]}',
                    f'- Nodos generados: {resultado["resumen"]["nodos"]}', '',
                    '### Desarrollo de nodos', '',
                    '| Nodo | Padre | Regla/origen | Expresión | Estado |',
                    '|---|---|---|---|---|'])
    for nodo in arbol['nodos']:
        limpia = lambda x: str(x).replace('|', '\\|').replace('\n', ' ')
        bloques.append(f'| N{nodo["id"]} | ' +
                       (f'N{nodo["padre"]}' if nodo['padre'] is not None else '—') +
                       f' | {limpia(nodo["origen"])} | {limpia(simbolizar(nodo["expresion"]))} | {nodo["estado"]} |')
    bloques.extend(['', '### Contradicciones', ''])
    cerrados = [n for n in arbol['nodos'] if n.get('contradiccion')]
    if not cerrados:
        bloques.append('No se detectaron contradicciones en las ramas.')
    else:
        for n in cerrados:
            c = n['contradiccion']
            bloques.append(f'- N{n["id"]}: {letra(c["atomo"])} y su negación (N{c["nodos"][0]} / N{c["nodos"][1]}).')
    bloques.extend(['', 'El TXT es la fuente editable. Este reporte se reemplaza al volver a analizar ese dominio.', ''])
    return '\n'.join(bloques)


def guardar_analisis(nombre, texto, revision_esperada, analizar):
    if not isinstance(texto, str) or len(texto) > 20000:
        raise ValueError('El texto debe tener como máximo 20 000 caracteres.')
    with CANDADO:
        comprobar(nombre, revision_esperada)
        # El análisis se calcula antes de guardar el reporte. Un resultado inválido
        # conserva el TXT pero deja desactualizado el reporte anterior.
        try:
            resultado = analizar(texto)
        except ValueError:
            guardar_texto(nombre, texto, revision_esperada)
            raise
        comprobar(nombre, revision_esperada)
        guardar_texto(nombre, texto, revision_esperada)
        if resultado['ok']:
            _, destino = rutas(nombre)
            escribir(destino, reporte(nombre, texto, resultado))
        resultado['dominio'] = leer(nombre)
        return resultado
