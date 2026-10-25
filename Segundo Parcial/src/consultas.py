import re

from .atomos import RegistroAtomos
from .parser import analizar_regla
from .reglas import formatear_expresion
from .fnc import convertir_reglas, formula_a_clausulas
from .sat import resolver_clausulas



def _resumen_reglas(reglas):
    fragmentos = [f'{regla["id"]} («{regla["texto"].strip()}»)' for regla in reglas]
    return '; '.join(fragmentos)


def _fundamento(reglas, variables, extra, motor):
    """Busca un subconjunto suficiente de premisas por eliminación.

    No pretende enumerar todas las demostraciones posibles.
    """
    if len(reglas) > 24:
        return None
    conjuntos = [formula_a_clausulas(regla['estructura']) for regla in reglas]

    def insatisfacible(indices):
        clausulas = [c for i in indices for c in conjuntos[i]] + extra
        return not resolver_clausulas(clausulas, variables, max_soluciones=1, motor=motor)['compatible']

    seleccion = list(range(len(reglas)))
    if not insatisfacible(seleccion):
        return []
    for i in list(seleccion):
        candidato = [x for x in seleccion if x != i]
        if insatisfacible(candidato):
            seleccion = candidato
    return [reglas[i] for i in seleccion]


def _describir_mundo(mundo, atomos, ids, limite=5):
    items = []
    for clave in ids:
        if clave in mundo:
            items.append(f'{atomos.get(clave, clave)}: {"verdadero" if mundo[clave] else "falso"}')
        if len(items) == limite:
            break
    return '; '.join(items)


def _explicacion_natural(estado, pregunta, reglas, atomos, variables,
                         verdadero, falso, motor, estructura):
    if estado == 'INCONSISTENTE':
        base = _fundamento(reglas, variables, [], motor)
        if base is None:
            return ('Las reglas se contradicen: no hay ninguna situación donde todas sean '
                    'verdaderas simultáneamente. Hay demasiadas reglas para aislar aquí una causa breve.')
        return ('No se puede decidir la consulta porque las propias reglas son incompatibles. '
                'Estas reglas bastan para producir la contradicción: ' + _resumen_reglas(base) +
                '. No existe un mundo que satisfaga todas las premisas.')

    if estado in ('DEMOSTRADA', 'REFUTADA'):
        premisas = _fundamento(reglas, variables,
                              formula_a_clausulas({'op': 'NO', 'args': [estructura]})
                              if estado == 'DEMOSTRADA' else formula_a_clausulas(estructura), motor)
        frase = ('La conclusión «' + pregunta + '» se cumple necesariamente.'
                 if estado == 'DEMOSTRADA' else
                 'La conclusión «' + pregunta + '» es imposible bajo estas reglas.')
        if premisas is None:
            return frase + (' No existe una asignación que cumpla las reglas y niegue la conclusión.'
                            if estado == 'DEMOSTRADA' else
                            ' No existe una asignación que cumpla las reglas y la haga verdadera.')
        if not premisas:
            return frase + ' Se deduce de la propia estructura lógica de la consulta, incluso sin utilizar otras reglas.'
        hipotesis = ('la consulta sea falsa' if estado == 'DEMOSTRADA' else 'la consulta sea verdadera')
        return (frase + ' Si intentamos que ' + hipotesis + ', las siguientes reglas dejan de poder cumplirse juntas: ' + _resumen_reglas(premisas) + '.')

    # Mundo verdadero y mundo falso: ambos satisfacen las reglas.
    diferentes = [k for k in variables if verdadero[k] != falso[k]]
    detalle_v = _describir_mundo(verdadero, variables, diferentes)
    detalle_f = _describir_mundo(falso, variables, diferentes)
    introduccion = (f'Las reglas no alcanzan para decidir «{pregunta}»: '
                    'permiten al menos dos situaciones compatibles.')
    if any(k not in atomos for k in diferentes):
        introduccion += ' La consulta incluye una proposición que no aparece en las reglas iniciales.'
    return (introduccion + ' En una situación es verdadera (' + detalle_v +
            '); en otra es falsa (' + detalle_f + ').')


def evaluar_consulta(reglas, atomos, pregunta, motor='auto', clausulas_base=None):
    if not reglas:
        raise ValueError('Primero necesitas al menos una regla.')
    if not isinstance(pregunta, str):
        raise ValueError('La consulta debe ser una oración.')
    pregunta = pregunta.strip().strip('¿?').strip()
    if not pregunta or len(pregunta) > 2000:
        raise ValueError('Escribe una consulta de entre 1 y 2000 caracteres.')

    registro = RegistroAtomos()
    for identificador, proposicion in atomos.items():
        if registro.registrar(proposicion) != identificador:
            raise ValueError('Los identificadores de los átomos no son consecutivos.')

    if re.fullmatch(r'X[1-9]\d*', pregunta):
        if pregunta not in atomos:
            raise ValueError('El átomo indicado no existe en las reglas.')
        estructura = {'op': 'ATOMO', 'id': pregunta}
    else:
        estructura = analizar_regla(pregunta, registro)

    consulta_negada = {'op': 'NO', 'args': [estructura]}
    clausulas = clausulas_base if clausulas_base is not None else convertir_reglas(reglas, atomos)['clausulas']
    variables = registro.obtener_atomos()
    nuevas = {k: v for k, v in variables.items() if k not in atomos}
    base = resolver_clausulas(clausulas, variables, max_soluciones=1, motor=motor)
    if not base['compatible']:
        explicacion = _explicacion_natural('INCONSISTENTE', pregunta, reglas, atomos, variables, None, None, motor, estructura)
        return {
            'estado': 'INCONSISTENTE',
            'expresion': formatear_expresion(estructura),
            'consulta': pregunta,
            'nuevos_atomos': nuevas,
            'explicacion': explicacion,
            'ejemplo_verdadero': None,
            'contraejemplo': None,
            'motor': base['motor'],
        }

    con_pregunta = resolver_clausulas(
        clausulas + formula_a_clausulas(estructura), variables, max_soluciones=1, motor=motor
    )
    con_negacion = resolver_clausulas(
        clausulas + formula_a_clausulas(consulta_negada), variables, max_soluciones=1, motor=motor
    )

    if not con_negacion['compatible']:
        estado = 'DEMOSTRADA'
    elif not con_pregunta['compatible']:
        estado = 'REFUTADA'
    else:
        estado = 'INDETERMINADA'
    verdadero = con_pregunta['soluciones'][0] if con_pregunta['compatible'] else None
    falso = con_negacion['soluciones'][0] if con_negacion['compatible'] else None
    explicacion = _explicacion_natural(estado, pregunta, reglas, atomos, variables,
                                       verdadero, falso, motor, estructura)

    return {
        'estado': estado,
        'consulta': pregunta,
        'expresion': formatear_expresion(estructura),
        'nuevos_atomos': nuevas,
        'explicacion': explicacion,
        'ejemplo_verdadero': con_pregunta['soluciones'][0] if con_pregunta['compatible'] else None,
        'contraejemplo': con_negacion['soluciones'][0] if con_negacion['compatible'] else None,
        'motor': base['motor'],
    }
