import itertools
import random
import unittest

from src.atomos import RegistroAtomos
from src.reglas import RegistroReglas
from src.fnc import convertir_reglas, formula_a_clausulas, mostrar_fnc, LimiteFNC


def armar(*oraciones, max_clausulas=2048):
    atomos = RegistroAtomos()
    registro = RegistroReglas(atomos)
    for oracion in oraciones:
        registro.agregar(oracion)
    return convertir_reglas(registro.obtener_reglas(), atomos.obtener_atomos(), max_clausulas)


def evaluar_ast(nodo, valores):
    operador = nodo['op']
    if operador == 'ATOMO':
        return valores[nodo['id']]
    args = [evaluar_ast(h, valores) for h in nodo['args']]
    if operador == 'NO':
        return not args[0]
    if operador == 'Y':
        return all(args)
    if operador == 'O':
        return any(args)
    if operador == 'IMPLICA':
        return not args[0] or args[1]
    raise ValueError(operador)


def evaluar_fnc(clausulas, valores):
    return all(any(valores[f'X{abs(x)}'] == (x > 0) for x in c) for c in clausulas)


class TestFormaNormalConjuntiva(unittest.TestCase):
    def test_implicacion(self):
        r = armar('Si Juan estudia, entonces aprueba.')
        self.assertEqual(r['clausulas'], [[-1, 2]])
        self.assertEqual(r['expresion'], '(¬X1 ∨ X2)')
        self.assertEqual(r['dimacs'], 'p cnf 2 1\n-1 2 0')

    def test_implicacion_compuesta(self):
        r = armar('Si Juan estudia y entrega la tarea, entonces aprueba.')
        self.assertEqual(r['clausulas'], [[-1, -2, 3]])

    def test_hechos_encadenados(self):
        r = armar('Si Juan estudia, entonces aprueba.', 'Juan estudia.')
        self.assertEqual(r['clausulas'], [[-1, 2], [1]])

    def test_negacion_de_conjuncion(self):
        r = armar('No es cierto que Juan estudia y trabaja.')
        self.assertEqual(r['clausulas'], [[-1, -2]])

    def test_negacion_de_disyuncion(self):
        r = armar('No es cierto que Juan estudia o trabaja.')
        self.assertEqual(r['clausulas'], [[-1], [-2]])

    def test_negacion_de_implicacion(self):
        r = armar('No es cierto que (si Juan estudia, entonces trabaja).')
        self.assertEqual(r['clausulas'], [[1], [-2]])

    def test_distribucion(self):
        r = armar('Juan estudia o (Pedro trabaja y Ana aprueba).')
        self.assertEqual(r['clausulas'], [[1, 2], [1, 3]])

    def test_contradiccion_no_desaparece(self):
        r = armar('Juan estudia.', 'Juan no estudia.')
        self.assertEqual(r['clausulas'], [[1], [-1]])

    def test_tautologia(self):
        r = armar('Juan estudia o no estudia.')
        self.assertEqual(r['clausulas'], [])
        self.assertEqual(r['expresion'], '⊤')
        self.assertEqual(r['dimacs'], 'p cnf 1 0')

    def test_duplicados_de_clausulas(self):
        r = armar('Juan estudia.', 'Juan estudia.')
        self.assertEqual(r['clausulas'], [[1]])
        self.assertEqual(len(r['reglas']), 2)

    def test_limite_y_entrada_vacia(self):
        with self.assertRaises(ValueError):
            convertir_reglas([])
        with self.assertRaises(ValueError):
            armar('Juan estudia.', max_clausulas=0)
        with self.assertRaises(LimiteFNC):
            armar('Juan estudia y trabaja.', max_clausulas=1)

    def test_equivalencia_de_todas_las_combinaciones(self):
        textos = [
            'Si Juan estudia, entonces aprueba.',
            'Juan estudia o (Pedro trabaja y Ana aprueba).',
            'No es cierto que (si Juan estudia, entonces Pedro trabaja).',
            'Si Juan estudia y (Pedro trabaja o Ana aprueba), entonces Ana trabaja.',
            'Si Juan estudia, entonces (si Pedro trabaja, entonces Ana aprueba).',
            'No es cierto que Juan estudia y trabaja.',
        ]
        for texto in textos:
            with self.subTest(texto=texto):
                atomos = RegistroAtomos()
                registro = RegistroReglas(atomos)
                registro.agregar(texto)
                original = registro.obtener_reglas()[0]['estructura']
                clausulas = formula_a_clausulas(original)
                claves = list(atomos.obtener_atomos())
                for bits in itertools.product((False, True), repeat=len(claves)):
                    valores = dict(zip(claves, bits))
                    self.assertEqual(evaluar_ast(original, valores), evaluar_fnc(clausulas, valores))

    def test_equivalencia_aleatoria(self):
        rng = random.Random(2026)
        for _ in range(150):
            def formula(profundidad):
                if profundidad == 0 or rng.random() < .25:
                    return {'op': 'ATOMO', 'id': f'X{rng.randrange(1, 5)}'}
                op = rng.choice(['Y', 'O', 'NO', 'IMPLICA'])
                cantidad = 1 if op == 'NO' else (2 if op == 'IMPLICA' else rng.randrange(2, 4))
                return {'op': op, 'args': [formula(profundidad - 1) for _ in range(cantidad)]}
            ast = formula(3)
            clauses = formula_a_clausulas(ast)
            for bits in itertools.product((False, True), repeat=4):
                vals = dict(zip(('X1', 'X2', 'X3', 'X4'), bits))
                self.assertEqual(evaluar_ast(ast, vals), evaluar_fnc(clauses, vals))

    def test_variable_id_invalido(self):
        with self.assertRaises(ValueError):
            formula_a_clausulas({'op': 'ATOMO', 'id': 'foo'})

    def test_expresion_verdadera_o_falsa(self):
        self.assertEqual(mostrar_fnc([]), '⊤')
        self.assertEqual(mostrar_fnc([[]]), '⊥')


if __name__ == '__main__':
    unittest.main()
