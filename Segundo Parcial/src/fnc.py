import re


class LimiteFNC(ValueError):
    pass


def _clausula(literales):
    resultado = []
    vistos = set()
    for literal in literales:
        if -literal in vistos:
            return None
        if literal not in vistos:
            vistos.add(literal)
            resultado.append(literal)
    return tuple(resultado)


def _conjuncion(grupos, limite):
    resultado = []
    vistos = set()
    for grupo in grupos:
        for clausula in grupo:
            if clausula not in vistos:
                vistos.add(clausula)
                resultado.append(clausula)
                if len(resultado) > limite:
                    raise LimiteFNC(f'La FNC supera el límite de {limite} cláusulas.')
    return resultado


def _disyuncion(izquierda, derecha, limite):
    if not izquierda or not derecha:
        return []
    if len(izquierda) * len(derecha) > max(10000, 8 * limite):
        raise LimiteFNC('La distribución generaría demasiadas combinaciones.')
    resultado = []
    vistos = set()
    for a in izquierda:
        for b in derecha:
            clausula = _clausula((*a, *b))
            if clausula is not None and clausula not in vistos:
                vistos.add(clausula)
                resultado.append(clausula)
                if len(resultado) > limite:
                    raise LimiteFNC(f'La FNC supera el límite de {limite} cláusulas.')
    return resultado


def _convertir(formula, negado, limite):
    operador = formula['op']

    if operador == 'ATOMO':
        coincidencia = re.fullmatch(r'X([1-9]\d*)', formula['id'])
        if not coincidencia:
            raise ValueError(f"Identificador de átomo inválido: {formula['id']}")
        numero = int(coincidencia.group(1))
        return [(-numero if negado else numero,)]

    hijos = formula.get('args', [])
    if operador == 'NO':
        if len(hijos) != 1:
            raise ValueError('La negación necesita una sola expresión.')
        return _convertir(hijos[0], not negado, limite)

    if operador == 'IMPLICA':
        if len(hijos) != 2:
            raise ValueError('Una implicación necesita dos expresiones.')
        a, b = hijos
        if negado:
            return _conjuncion([_convertir(a, False, limite), _convertir(b, True, limite)], limite)
        return _disyuncion(_convertir(a, True, limite), _convertir(b, False, limite), limite)

    if operador == 'BICONDICIONAL':
        if len(hijos) != 2:
            raise ValueError('Un bicondicional requiere dos expresiones.')
        a, b = hijos
        if negado:
            # XOR: (A o B) y (no A o no B)
            return _conjuncion([
                _disyuncion(_convertir(a, False, limite), _convertir(b, False, limite), limite),
                _disyuncion(_convertir(a, True, limite), _convertir(b, True, limite), limite),
            ], limite)
        # Equivalencia: (no A o B) y (A o no B)
        return _conjuncion([
            _disyuncion(_convertir(a, True, limite), _convertir(b, False, limite), limite),
            _disyuncion(_convertir(a, False, limite), _convertir(b, True, limite), limite),
        ], limite)

    if operador not in {'Y', 'O'} or len(hijos) < 2:
        raise ValueError(f'Operador o cantidad de argumentos inválida: {operador}')

    partes = [_convertir(hijo, negado, limite) for hijo in hijos]
    if (operador == 'Y') != negado:
        return _conjuncion(partes, limite)

    resultado = partes[0]
    for parte in partes[1:]:
        resultado = _disyuncion(resultado, parte, limite)
    return resultado


def formula_a_clausulas(estructura, max_clausulas=2048):
    if max_clausulas < 1:
        raise ValueError('El límite de cláusulas debe ser positivo.')
    return [list(c) for c in _convertir(estructura, False, max_clausulas)]


def mostrar_fnc(clausulas):
    if not clausulas:
        return '⊤'
    partes = []
    for clausula in clausulas:
        if not clausula:
            return '⊥'
        elementos = [('¬' if n < 0 else '') + f'X{abs(n)}' for n in clausula]
        texto = ' ∨ '.join(elementos)
        partes.append(f'({texto})' if len(elementos) > 1 else texto)
    return ' ∧ '.join(partes)


def convertir_reglas(reglas, atomos=None, max_clausulas=2048):
    if not reglas:
        raise ValueError('Se necesita al menos una regla.')
    if max_clausulas < 1:
        raise ValueError('El límite de cláusulas debe ser positivo.')

    filas = []
    grupos = []
    variables = set()

    def registrar_ids(nodo):
        if nodo['op'] == 'ATOMO':
            coincidencia = re.fullmatch(r'X([1-9]\d*)', nodo['id'])
            if not coincidencia:
                raise ValueError(f"Identificador de átomo inválido: {nodo['id']}")
            variables.add(int(coincidencia.group(1)))
        else:
            for hijo in nodo.get('args', []):
                registrar_ids(hijo)

    for regla in reglas:
        registrar_ids(regla['estructura'])
        clausulas = formula_a_clausulas(regla['estructura'], max_clausulas)
        filas.append({
            'id': regla['id'],
            'original': regla['expresion'],
            'fnc': mostrar_fnc(clausulas),
            'clausulas': clausulas,
        })
        grupos.append([tuple(c) for c in clausulas])

    if atomos is not None:
        variables.update(int(k[1:]) for k in atomos if re.fullmatch(r'X[1-9]\d*', k))

    completas = [list(c) for c in _conjuncion(grupos, max_clausulas)]
    encabezado = f'p cnf {max(variables, default=0)} {len(completas)}'
    dimacs = '\n'.join([encabezado] + [' '.join(map(str, c)) + ' 0' for c in completas])
    return {
        'reglas': filas,
        'expresion': mostrar_fnc(completas),
        'clausulas': completas,
        'dimacs': dimacs,
        'num_variables': len(variables),
    }
