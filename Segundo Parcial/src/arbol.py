from collections import deque
from itertools import product
from .reglas import formatear_expresion


class LimiteArbol(Exception):
    pass


def negacion(formula):
    return {'op': 'NO', 'args': [formula]}


def conjuncion(*partes):
    return {'op': 'Y', 'args': list(partes)}


def expandir(formula):
    """Devuelve ('lineal'|'ramificar'|None, expresiones)."""
    op = formula['op']
    if op == 'Y':
        return 'lineal', formula['args']
    if op == 'O':
        return 'ramificar', formula['args']
    if op == 'IMPLICA':
        izquierda, derecha = formula['args']
        return 'ramificar', [negacion(izquierda), derecha]
    if op == 'BICONDICIONAL':
        a, b = formula['args']
        return 'ramificar', [conjuncion(a, b), conjuncion(negacion(a), negacion(b))]
    if op == 'NO':
        hija = formula['args'][0]
        tipo = hija['op']
        if tipo == 'NO':
            return 'lineal', [hija['args'][0]]
        if tipo == 'Y':
            return 'ramificar', [negacion(x) for x in hija['args']]
        if tipo == 'O':
            return 'lineal', [negacion(x) for x in hija['args']]
        if tipo == 'IMPLICA':
            izquierda, derecha = hija['args']
            return 'lineal', [izquierda, negacion(derecha)]
        if tipo == 'BICONDICIONAL':
            a, b = hija['args']
            return 'ramificar', [conjuncion(a, negacion(b)), conjuncion(negacion(a), b)]
    if op == 'ATOMO' or (op == 'NO' and formula['args'][0]['op'] == 'ATOMO'):
        return None, None
    raise ValueError(f'Estructura lógica desconocida: {op}')


def generar_arbol(reglas, atomos, max_nodos=1500, max_mundos=64):
    """Tabla semántica clásica. Conserva ramas cerradas y abiertas."""
    if not reglas:
        raise ValueError('Se necesita al menos una regla.')
    if max_nodos < 1 or max_mundos < 1:
        raise ValueError('Los límites deben ser positivos.')

    ids = [r['id'] for r in reglas]
    premisas = [r['estructura'] for r in reglas]
    raiz = premisas[0] if len(premisas) == 1 else {'op': 'Y', 'args': premisas}
    nodos, hojas = [], []

    def insertar(padre, formula, origen, metodo):
        if len(nodos) >= max_nodos:
            raise LimiteArbol(f'El árbol superó {max_nodos} nodos. Aumenta el límite para analizarlo por completo.')
        numero = len(nodos) + 1
        nodos.append({
            'id': numero, 'padre': padre,
            'expresion': formatear_expresion(formula),
            'origen': origen, 'metodo': metodo,
            'estado': 'normal', 'contradiccion': None,
            'aplicada': False,
        })
        return numero

    principal = insertar(None, raiz, 'Conjunto de reglas', 'raiz')
    pendiente = deque([(raiz, principal, None)])
    pila = [(principal, pendiente, {})]

    while pila:
        ultimo, pendientes, valores = pila.pop()
        while pendientes:
            pos = next((i for i, (f, _, _) in enumerate(pendientes)
                        if f['op'] == 'ATOMO' or
                        (f['op'] == 'NO' and f['args'][0]['op'] == 'ATOMO')), 0)
            formula, nodo_actual, fuente = pendientes[pos]
            del pendientes[pos]
            tipo, desarrollo = expandir(formula)

            if tipo is None:
                literal = formula if formula['op'] == 'ATOMO' else formula['args'][0]
                nombre = literal['id']
                positivo = formula['op'] == 'ATOMO'
                if nombre in valores and valores[nombre][0] != positivo:
                    previo = valores[nombre][1]
                    nodos[ultimo - 1]['estado'] = 'cerrada'
                    nodos[ultimo - 1]['contradiccion'] = {
                        'atomo': nombre, 'nodos': [previo, nodo_actual],
                    }
                    hojas.append({'nodo': ultimo, 'estado': 'cerrada',
                                  'contradiccion': {'atomo': nombre, 'nodos': [previo, nodo_actual]}})
                    break
                valores[nombre] = (positivo, nodo_actual)
                continue

            nodos[nodo_actual - 1]['aplicada'] = True
            if tipo == 'lineal':
                nuevos = []
                for i, parte in enumerate(desarrollo):
                    origen = ids[i] if nodo_actual == principal and len(ids) > 1 else (fuente or 'Desarrollo')
                    nuevo = insertar(ultimo, parte, origen, formula['op'])
                    ultimo = nuevo
                    nuevos.append((parte, nuevo, origen))
                pendientes.extendleft(reversed(nuevos))
                continue

            # Alternativas: una rama por cada opción, sin descartar las cerradas.
            alternativas = []
            for parte in desarrollo:
                nuevo = insertar(ultimo, parte, fuente or 'Desarrollo', formula['op'])
                nueva_cola = deque([(parte, nuevo, fuente)])
                nueva_cola.extend(pendientes)
                alternativas.append((nuevo, nueva_cola, valores.copy()))
            pila.extend(reversed(alternativas))
            break
        else:
            nodos[ultimo - 1]['estado'] = 'abierta'
            hojas.append({'nodo': ultimo, 'estado': 'abierta',
                          'valores': {a: v for a, (v, _) in valores.items()}})

    variables = list(atomos)
    mundos, vistos = [], set()
    truncado = False
    for hoja in hojas:
        if hoja['estado'] != 'abierta':
            continue
        fijos = hoja['valores']
        libres = [nombre for nombre in variables if nombre not in fijos]
        for bits in product((False, True), repeat=len(libres)):
            completos = dict(zip(libres, bits))
            mundo = {nombre: fijos[nombre] if nombre in fijos else completos[nombre] for nombre in variables}
            clave = tuple(mundo.items())
            if clave not in vistos:
                if len(mundos) == max_mundos:
                    truncado = True
                    break
                vistos.add(clave)
                mundos.append(mundo)
        if truncado:
            break

    return {
        'compatible': any(hoja['estado'] == 'abierta' for hoja in hojas),
        'raiz': principal, 'nodos': nodos, 'hojas': hojas,
        'mundos': mundos, 'mundos_truncados': truncado,
    }
