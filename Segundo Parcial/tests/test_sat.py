import itertools
import random
import unittest

from src.atomos import RegistroAtomos
from src.reglas import RegistroReglas
from src.sat import resolver_clausulas, resolver_reglas


def preparar(*textos):
    atomos = RegistroAtomos()
    reglas = RegistroReglas(atomos)
    for texto in textos:
        reglas.agregar(texto)
    return reglas.obtener_reglas(), atomos.obtener_atomos()


class TestSAT(unittest.TestCase):
    def test_cadena_de_reglas(self):
        reglas, atomos = preparar(
            'Si Juan estudia y entrega la tarea, entonces aprueba el examen.',
            'Si Juan aprueba el examen, entonces pasa la materia.',
            'Juan estudia.',
            'Juan entrega la tarea.',
        )
        r = resolver_reglas(reglas, atomos, motor='dpll')
        self.assertEqual(r['estado'], 'SAT')
        self.assertTrue(r['coincide_arbol'])
        self.assertEqual(len(r['soluciones']), 1)
        self.assertEqual(r['soluciones'][0], dict.fromkeys(atomos, True))
        self.assertFalse(r['hay_mas'])

    def test_contradiccion(self):
        reglas, atomos = preparar('Juan estudia.', 'Juan no estudia.')
        r = resolver_reglas(reglas, atomos, motor='dpll')
        self.assertEqual(r['estado'], 'UNSAT')
        self.assertEqual(r['soluciones'], [])
        self.assertEqual(r['arbol'], 'UNSAT')
        self.assertTrue(r['coincide_arbol'])

    def test_contradiccion_indirecta(self):
        reglas, atomos = preparar(
            'Si Juan estudia, entonces aprueba.',
            'Juan estudia.',
            'Juan no aprueba.',
        )
        self.assertEqual(resolver_reglas(reglas, atomos, motor='dpll')['estado'], 'UNSAT')

    def test_disyuncion_tres_mundos(self):
        r = resolver_clausulas([[1, 2]], {'X1': 'P', 'X2': 'Q'}, motor='dpll')
        self.assertEqual(r['estado'], 'SAT')
        self.assertEqual(len(r['soluciones']), 3)
        self.assertFalse(r['hay_mas'])
        self.assertEqual({tuple(m.values()) for m in r['soluciones']},
                         {(False, True), (True, False), (True, True)})

    def test_tautologia_y_variables_libres(self):
        r = resolver_clausulas([], {'X1': 'P', 'X2': 'Q'}, motor='dpll')
        self.assertEqual(len(r['soluciones']), 4)
        self.assertFalse(r['hay_mas'])

    def test_tautologia_con_regla(self):
        reglas, atomos = preparar('Juan estudia o no estudia.')
        r = resolver_reglas(reglas, atomos, motor='dpll')
        self.assertEqual(len(r['soluciones']), 2)
        self.assertTrue(r['coincide_arbol'])

    def test_clausula_vacia_es_insatisfacible(self):
        r = resolver_clausulas([[]], {'X1': 'P'}, motor='dpll')
        self.assertEqual(r['estado'], 'UNSAT')

    def test_limite_soluciones_no_se_confunde_con_total(self):
        r = resolver_clausulas([], {'X1': 'P', 'X2': 'Q', 'X3': 'R'},
                              max_soluciones=3, motor='dpll')
        self.assertEqual(len(r['soluciones']), 3)
        self.assertTrue(r['hay_mas'])

    def test_maximo_exacto(self):
        r = resolver_clausulas([[1], [2]], {'X1': 'P', 'X2': 'Q'},
                              max_soluciones=1, motor='dpll')
        self.assertFalse(r['hay_mas'])
        self.assertEqual(len(r['soluciones']), 1)

    def test_validacion_de_datos(self):
        with self.assertRaises(ValueError):
            resolver_clausulas([[0]], {'X1': 'P'}, motor='dpll')
        with self.assertRaises(ValueError):
            resolver_clausulas([[2]], {'X1': 'P'}, motor='dpll')
        with self.assertRaises(ValueError):
            resolver_clausulas([], {'X1': 'P'}, max_soluciones=0, motor='dpll')
        with self.assertRaises(ValueError):
            resolver_clausulas([], {'X1': 'P'}, motor='xyz')

    def test_auto_usa_un_motor_disponible(self):
        r = resolver_clausulas([[1]], {'X1': 'P'})
        self.assertIn(r['motor'], {'DPLL (Python)', 'PySAT (Glucose3)'})
        self.assertEqual(r['soluciones'], [{'X1': True}])

    def test_sin_comparacion_de_arbol(self):
        reglas, atomos = preparar('Juan estudia.')
        r = resolver_reglas(reglas, atomos, motor='dpll', comparar_arbol=False)
        self.assertIsNone(r['coincide_arbol'])
        self.assertIsNone(r['arbol'])

    def test_aleatorio_contra_tabla_verdad(self):
        rng = random.Random(2026)
        variables = {f'X{i}': f'P{i}' for i in range(1, 5)}
        for _ in range(450):
            clausulas = [
                [rng.choice((-1, 1)) * rng.randint(1, 4)
                 for _ in range(rng.randint(0, 4))]
                for _ in range(rng.randint(0, 8))
            ]
            esperado = {
                bits for bits in itertools.product((False, True), repeat=4)
                if all(any(bits[abs(x) - 1] == (x > 0) for x in clausula)
                       for clausula in clausulas)
            }
            resultado = resolver_clausulas(clausulas, variables,
                                          max_soluciones=16, motor='dpll')
            obtenido = {tuple(m.values()) for m in resultado['soluciones']}
            self.assertEqual(obtenido, esperado, str(clausulas))
            self.assertFalse(resultado['hay_mas'])


if __name__ == '__main__':
    unittest.main()
