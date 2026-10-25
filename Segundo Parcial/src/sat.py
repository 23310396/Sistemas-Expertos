from .fnc import convertir_reglas
from .arbol import generar_arbol, LimiteArbol


def _dpll(clausulas, asignacion):
    while True:
        pendientes = []
        unitarios = []
        for clausula in clausulas:
            if any(asignacion.get(abs(x)) == (x > 0) for x in clausula):
                continue
            restantes = [x for x in clausula if abs(x) not in asignacion]
            if not restantes:
                return None
            pendientes.append(restantes)
            if len(restantes) == 1:
                unitarios.append(restantes[0])
        if not pendientes:
            return asignacion
        if not unitarios:
            break
        for literal in unitarios:
            variable, valor = abs(literal), literal > 0
            if variable in asignacion and asignacion[variable] != valor:
                return None
            asignacion[variable] = valor

    frecuencias = {}
    for clausula in pendientes:
        for literal in clausula:
            variable = abs(literal)
            frecuencias[variable] = frecuencias.get(variable, 0) + 1
    variable = max(frecuencias, key=frecuencias.get)
    for valor in (True, False):
        intento = _dpll(clausulas, {**asignacion, variable: valor})
        if intento is not None:
            return intento
    return None


def _modelos_dpll(clausulas, indices, limite):
    restricciones = [list(c) for c in clausulas]
    soluciones = []
    for _ in range(limite + 1):
        modelo = _dpll(restricciones, {})
        if modelo is None:
            break
        completo = {n: modelo.get(n, False) for n in indices}
        soluciones.append(completo)
        restricciones.append([-n if completo[n] else n for n in indices])
    return soluciones


def _modelos_pysat(clausulas, indices, limite):
    from pysat.solvers import Solver

    soluciones = []
    with Solver(name='g3', bootstrap_with=clausulas) as solver:
        for _ in range(limite + 1):
            if not solver.solve():
                break
            modelo = {abs(n): n > 0 for n in solver.get_model()}
            completo = {n: modelo.get(n, False) for n in indices}
            soluciones.append(completo)
            solver.add_clause([-n if completo[n] else n for n in indices])
    return soluciones


def resolver_clausulas(clausulas, variables, max_soluciones=16, motor='auto'):
    if not 1 <= max_soluciones <= 256:
        raise ValueError('El límite de soluciones debe estar entre 1 y 256.')
    if motor not in {'auto', 'dpll', 'pysat'}:
        raise ValueError('Motor desconocido.')

    indices = sorted({int(x[1:]) for x in variables})
    if any(not isinstance(c, (list, tuple)) for c in clausulas):
        raise ValueError('Las cláusulas deben ser listas de enteros.')
    if any(not isinstance(x, int) or isinstance(x, bool) or x == 0 for c in clausulas for x in c):
        raise ValueError('Los literales deben ser enteros distintos de cero.')
    if not {abs(x) for c in clausulas for x in c}.issubset(indices):
        raise ValueError('Una cláusula utiliza un átomo no registrado.')

    elegido = motor
    if motor == 'auto':
        try:
            from pysat.solvers import Solver  # noqa: F401
            elegido = 'pysat'
        except ImportError:
            elegido = 'dpll'
    if elegido == 'dpll' and len(indices) > 100:
        raise ValueError('Demasiadas variables para DPLL; instala python-sat.')

    try:
        soluciones = (_modelos_pysat if elegido == 'pysat' else _modelos_dpll)(
            clausulas, indices, max_soluciones
        )
    except ImportError as error:
        raise RuntimeError('PySAT no está instalado. Ejecuta: python -m pip install python-sat') from error

    hay_mas = len(soluciones) > max_soluciones
    soluciones = soluciones[:max_soluciones]
    return {
        'estado': 'SAT' if soluciones else 'UNSAT',
        'compatible': bool(soluciones),
        'motor': 'PySAT (Glucose3)' if elegido == 'pysat' else 'DPLL (Python)',
        'soluciones': [
            {clave: valores[int(clave[1:])] for clave in variables}
            for valores in soluciones
        ],
        'hay_mas': hay_mas,
    }


def resolver_reglas(reglas, atomos, max_soluciones=16, motor='auto', comparar_arbol=True):
    fnc = convertir_reglas(reglas, atomos)
    resultado = resolver_clausulas(fnc['clausulas'], atomos, max_soluciones, motor)
    resultado['fnc'] = fnc
    resultado['arbol'] = None
    resultado['coincide_arbol'] = None
    if comparar_arbol:
        try:
            arbol = generar_arbol(reglas, atomos, max_nodos=1500, max_mundos=1)
        except LimiteArbol:
            resultado['arbol'] = 'Límite de nodos alcanzado'
        else:
            resultado['arbol'] = 'SAT' if arbol['compatible'] else 'UNSAT'
            resultado['coincide_arbol'] = arbol['compatible'] == resultado['compatible']
    return resultado
