import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from .arbol import LimiteArbol, generar_arbol
from .fnc import LimiteFNC, convertir_reglas
from .sat import resolver_clausulas
from .consultas import evaluar_consulta
from .atomos import RegistroAtomos
from .main import separar_oraciones
from .reglas import RegistroReglas
from . import dominios

BASE = Path(__file__).resolve().parent.parent
ARCHIVOS = {
    '/': ('static/index.html', 'text/html; charset=utf-8'),
    '/static/app.css': ('static/app.css', 'text/css; charset=utf-8'),
    '/static/app.js': ('static/app.js', 'application/javascript; charset=utf-8'),
}


def a_natural(expresion, atomos):
    """Traduce la estructura simbólica a una lectura en español."""
    tokens = re.findall(r'X\d+|[()¬∧∨→↔]', expresion)
    if ''.join(tokens) != re.sub(r'\s+', '', expresion):
        return expresion
    actual = 0

    def expresion_rec(minimo=0):
        nonlocal actual
        if actual >= len(tokens):
            raise ValueError('Fórmula incompleta')
        t = tokens[actual]
        actual += 1
        if t == '¬':
            hijo, op_hijo = expresion_rec(4)
            izquierda = (f'no es cierto que ({hijo})' if op_hijo else f'no es cierto que {hijo}', 'NO')
        elif t == '(':
            izquierda = expresion_rec()
            if actual >= len(tokens) or tokens[actual] != ')':
                raise ValueError('Paréntesis incompleto')
            actual += 1
        elif re.fullmatch(r'X\d+', t):
            izquierda = (atomos.get(t, t), None)
        else:
            raise ValueError('Operador sin proposición')
        prioridad = {'↔': 0, '→': 1, '∨': 2, '∧': 3}
        while actual < len(tokens) and tokens[actual] in prioridad:
            operador = tokens[actual]
            nivel = prioridad[operador]
            if nivel < minimo:
                break
            actual += 1
            derecha, op_derecha = expresion_rec(nivel if operador in {'→', '↔'} else nivel + 1)
            izq, op_izq = izquierda
            if operador == '→':
                izquierda = (f'Si {izq}, entonces {derecha}', 'IMPLICA')
            elif operador == '↔':
                izquierda = (f'{izq} si y solo si {derecha}', 'BICONDICIONAL')
            else:
                if op_izq and op_izq != ('Y' if operador == '∧' else 'O'):
                    izq = f'({izq})'
                if op_derecha and op_derecha != ('Y' if operador == '∧' else 'O'):
                    derecha = f'({derecha})'
                izquierda = (f'{izq} {"y" if operador == "∧" else "o"} {derecha}',
                             'Y' if operador == '∧' else 'O')
        return izquierda

    try:
        resultado, _ = expresion_rec()
        return resultado if actual == len(tokens) else expresion
    except (ValueError, IndexError, RecursionError):
        return expresion


def preparar(texto):
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError('Escribe al menos una regla antes de generar el árbol.')
    if len(texto) > 20000:
        raise ValueError('El texto supera los 20 000 caracteres permitidos.')
    oraciones = separar_oraciones(texto)
    if len(oraciones) > 100:
        raise ValueError('El problema supera las 100 oraciones admitidas.')

    atomos = RegistroAtomos()
    reglas = RegistroReglas(atomos)
    errores = []
    for indice, oracion in enumerate(oraciones, 1):
        try:
            reglas.agregar(oracion)
        except ValueError as error:
            errores.append({'numero': indice, 'texto': oracion, 'motivo': str(error)})
    if errores:
        return {'ok': False, 'error': 'Corrige las oraciones indicadas para generar el árbol completo.',
                'errores': errores, 'reglas': reglas.obtener_reglas(), 'atomos': atomos.obtener_atomos()}
    if not reglas.obtener_reglas():
        raise ValueError('No se encontraron reglas.')
    return atomos, reglas


def analizar(texto):
    preparado = preparar(texto)
    if isinstance(preparado, dict):
        return preparado
    atomos, reglas = preparado
    resultado = generar_arbol(reglas.obtener_reglas(), atomos.obtener_atomos(),
                              max_nodos=450, max_mundos=48)
    diccionario = atomos.obtener_atomos()
    fnc = convertir_reglas(reglas.obtener_reglas(), diccionario, max_clausulas=2048)
    sat = resolver_clausulas(fnc['clausulas'], diccionario, max_soluciones=16)
    sat['arbol'] = 'SAT' if resultado['compatible'] else 'UNSAT'
    sat['coincide_arbol'] = sat['compatible'] == resultado['compatible']
    nodos = []
    for n in resultado['nodos']:
        nodos.append({**n, 'natural': a_natural(n['expresion'], diccionario)})
    reglas_visibles = [{k: r[k] for k in ('id', 'texto', 'expresion')}
                      for r in reglas.obtener_reglas()]
    return {
        'ok': True,
        'atomos': diccionario,
        'reglas': reglas_visibles,
        'arbol': {**resultado, 'nodos': nodos},
        'fnc': fnc,
        'sat': sat,
        'resumen': {
            'abiertas': sum(h['estado'] == 'abierta' for h in resultado['hojas']),
            'cerradas': sum(h['estado'] == 'cerrada' for h in resultado['hojas']),
            'nodos': len(nodos),
        },
    }


def consultar(texto, pregunta):
    preparado = preparar(texto)
    if isinstance(preparado, dict):
        return preparado
    atomos, reglas = preparado
    atomos_dict = atomos.obtener_atomos()
    fnc = convertir_reglas(reglas.obtener_reglas(), atomos_dict, max_clausulas=2048)
    resultado = evaluar_consulta(reglas.obtener_reglas(), atomos_dict, pregunta,
                                 clausulas_base=fnc['clausulas'])
    return {'ok': True, 'consulta': resultado}


class Servidor(BaseHTTPRequestHandler):
    def _enviar(self, contenido, tipo='application/json; charset=utf-8', estado=200):
        self.send_response(estado)
        self.send_header('Content-Type', tipo)
        self.send_header('Content-Length', str(len(contenido)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(contenido)

    def _json(self, datos, estado=200):
        self._enviar(json.dumps(datos, ensure_ascii=False).encode('utf-8'), estado=estado)

    def do_GET(self):
        url = urlsplit(self.path)
        ruta = url.path
        if ruta in {'/api/dominios', '/api/dominio', '/api/dominio/calculos'}:
            try:
                if ruta == '/api/dominio/calculos':
                    nombre = parse_qs(url.query).get('nombre', [''])[0]
                    dominios.leer(nombre)
                    _, archivo = dominios.rutas(nombre)
                    if not archivo.is_file():
                        raise FileNotFoundError('Aún no existen cálculos para este dominio.')
                    self._enviar(archivo.read_bytes(), 'text/markdown; charset=utf-8')
                    return
                if ruta == '/api/dominios':
                    resultado = {'ok': True, 'dominios': [
                        {k: d[k] for k in ('nombre', 'revision', 'calculado', 'tiene_calculos')}
                        for d in dominios.listar()]}
                else:
                    nombre = parse_qs(url.query).get('nombre', [''])[0]
                    resultado = {'ok': True, 'dominio': dominios.leer(nombre)}
                self._json(resultado)
            except FileNotFoundError as error:
                self._json({'ok': False, 'error': str(error)}, 404)
            except (ValueError, OSError, UnicodeError) as error:
                self._json({'ok': False, 'error': str(error)}, 422)
            return
        if ruta not in ARCHIVOS:
            self._enviar(b'No encontrado', 'text/plain; charset=utf-8', 404)
            return
        relativo, tipo = ARCHIVOS[ruta]
        try:
            self._enviar((BASE / relativo).read_bytes(), tipo)
        except OSError:
            self._enviar(b'Archivo no disponible', 'text/plain; charset=utf-8', 500)

    def do_POST(self):
        ruta = urlsplit(self.path).path
        admitidas = {'/api/analizar', '/api/consultar', '/api/dominios',
                     '/api/dominio/guardar', '/api/dominio/analizar'}
        if ruta not in admitidas:
            self._enviar(b'No encontrado', 'text/plain; charset=utf-8', 404)
            return
        try:
            cantidad = int(self.headers.get('Content-Length', '0'))
            if cantidad <= 0 or cantidad > 100000:
                raise ValueError('La solicitud debe contener un problema de tamaño válido.')
            entrada = json.loads(self.rfile.read(cantidad))
            if not isinstance(entrada, dict):
                raise ValueError('La solicitud debe contener un objeto JSON.')
            if ruta == '/api/consultar':
                respuesta = consultar(entrada.get('texto', ''), entrada.get('pregunta', ''))
            elif ruta == '/api/analizar':
                respuesta = analizar(entrada.get('texto', ''))
            elif ruta == '/api/dominios':
                respuesta = {'ok': True, 'dominio': dominios.crear(entrada.get('nombre'))}
            elif ruta == '/api/dominio/guardar':
                respuesta = {'ok': True, 'dominio': dominios.guardar_texto(
                    entrada.get('nombre'), entrada.get('texto'), entrada.get('revision'))}
            else:
                respuesta = dominios.guardar_analisis(
                    entrada.get('nombre'), entrada.get('texto'), entrada.get('revision'), analizar)
            estado = 200 if respuesta['ok'] else 422
        except dominios.ConflictoDominio as error:
            respuesta, estado = {'ok': False, 'conflicto': True, 'error': str(error)}, 409
        except FileNotFoundError as error:
            respuesta, estado = {'ok': False, 'error': str(error)}, 404
        except (json.JSONDecodeError, UnicodeError, TypeError, AttributeError, ValueError,
                OSError, LimiteArbol, LimiteFNC, RuntimeError) as error:
            respuesta, estado = {'ok': False, 'error': str(error)}, 422
        self._json(respuesta, estado)

    def log_message(self, formato, *args):
        pass


def main():
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    servidor = ThreadingHTTPServer(('0.0.0.0', puerto), Servidor)
    print(f'Interfaz disponible en el puerto {puerto}. Ctrl+C para detener.')
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == '__main__':
    main()
