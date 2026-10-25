import itertools
import unittest
from src.atomos import RegistroAtomos
from src.reglas import RegistroReglas
from src.arbol import generar_arbol, LimiteArbol


def analizar(*textos, limite=64):
    atomos = RegistroAtomos()
    reglas = RegistroReglas(atomos)
    for texto in textos:
        reglas.agregar(texto)
    return generar_arbol(reglas.obtener_reglas(), atomos.obtener_atomos(), max_mundos=limite)


class TestArbolSemantico(unittest.TestCase):
    def test_implicacion_y_hecho(self):
        r = analizar('Si Juan estudia, entonces aprueba.', 'Juan estudia.')
        self.assertTrue(r['compatible'])
        self.assertEqual(len([h for h in r['hojas'] if h['estado'] == 'abierta']), 1)
        self.assertEqual(len([h for h in r['hojas'] if h['estado'] == 'cerrada']), 1)
        self.assertEqual(r['mundos'], [{'X1': True, 'X2': True}])

    def test_contradiccion_simple(self):
        r = analizar('Juan estudia.', 'Juan no estudia.')
        self.assertFalse(r['compatible'])
        self.assertEqual(r['mundos'], [])
        self.assertEqual(r['hojas'][0]['contradiccion']['atomo'], 'X1')

    def test_disyuncion_dos_mundos_cerrada(self):
        r = analizar('Juan estudia o trabaja.', 'Juan no estudia.', 'Juan no trabaja.')
        self.assertFalse(r['compatible'])
        self.assertEqual(len(r['hojas']), 2)
        self.assertTrue(all(h['estado']=='cerrada' for h in r['hojas']))

    def test_mundos_libres(self):
        r = analizar('Juan estudia o trabaja.')
        self.assertTrue(r['compatible'])
        self.assertEqual(len(r['mundos']), 3)
        self.assertEqual({tuple(m.values()) for m in r['mundos']}, {(True, True), (True, False), (False, True)})

    def test_implicacion_sin_hecho(self):
        r = analizar('Si Juan estudia, entonces trabaja.')
        self.assertEqual(len(r['mundos']), 3)

    def test_negacion_conjuncion(self):
        r = analizar('No es cierto que Juan estudia y trabaja.')
        self.assertEqual(len(r['mundos']), 3)

    def test_negacion_disyuncion(self):
        r = analizar('No es cierto que Juan estudia o trabaja.')
        self.assertEqual(r['mundos'], [{'X1':False,'X2':False}])

    def test_negacion_implicacion(self):
        r = analizar('No es cierto que (si Juan estudia, entonces trabaja).')
        self.assertEqual(r['mundos'], [{'X1':True,'X2':False}])

    def test_truncamiento(self):
        r = analizar('Juan estudia o trabaja.', limite=1)
        self.assertTrue(r['mundos_truncados'])
        self.assertEqual(len(r['mundos']), 1)

    def test_mismo_parrafo_con_reglas(self):
        r = analizar('Si el sensor detecta movimiento, entonces la alarma se activa.',
                    'Si la alarma se activa, entonces el robot se detiene.',
                    'El sensor detecta movimiento.', 'No es cierto que el robot se detiene.')
        self.assertFalse(r['compatible'])
        self.assertTrue(all(h['estado'] == 'cerrada' for h in r['hojas']))

    def test_limite_nodos(self):
        with self.assertRaises(LimiteArbol):
            atomos = RegistroAtomos()
            reglas = RegistroReglas(atomos)
            reglas.agregar('Si Juan estudia, entonces trabaja.')
            generar_arbol(reglas.obtener_reglas(), atomos.obtener_atomos(), max_nodos=1)


if __name__ == '__main__':
    unittest.main()
