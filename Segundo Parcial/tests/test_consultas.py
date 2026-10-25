import unittest

from src.atomos import RegistroAtomos
from src.reglas import RegistroReglas
from src.consultas import evaluar_consulta
from src.web import consultar


def base(*frases):
    atomos = RegistroAtomos()
    reglas = RegistroReglas(atomos)
    for frase in frases:
        reglas.agregar(frase)
    return reglas.obtener_reglas(), atomos.obtener_atomos()


class TestConsultas(unittest.TestCase):
    def setUp(self):
        self.reglas, self.atomos = base(
            'Si Juan estudia, entonces aprueba.', 'Juan estudia.'
        )

    def consultar(self, pregunta, motor='dpll'):
        return evaluar_consulta(self.reglas, self.atomos, pregunta, motor=motor)

    def test_demostrada_con_pregunta_natural(self):
        r = self.consultar('¿Juan aprueba?')
        self.assertEqual(r['estado'], 'DEMOSTRADA')
        self.assertEqual(r['expresion'], 'X2')
        self.assertIsNone(r['contraejemplo'])
        self.assertEqual(r['ejemplo_verdadero'], {'X1': True, 'X2': True})

    def test_demostrada_por_id(self):
        self.assertEqual(self.consultar('X2')['estado'], 'DEMOSTRADA')

    def test_refutada(self):
        r = self.consultar('Juan no aprueba.')
        self.assertEqual(r['estado'], 'REFUTADA')
        self.assertIsNone(r['ejemplo_verdadero'])
        self.assertIsNotNone(r['contraejemplo'])

    def test_indeterminada_con_atomo_existente(self):
        reglas, atomos = base('Juan estudia o trabaja.')
        r = evaluar_consulta(reglas, atomos, 'Juan estudia.', motor='dpll')
        self.assertEqual(r['estado'], 'INDETERMINADA')
        self.assertTrue(r['ejemplo_verdadero']['X1'])
        self.assertFalse(r['contraejemplo']['X1'])

    def test_atomo_nuevo_no_modifica_base(self):
        previo = self.atomos.copy()
        r = self.consultar('Juan tiene una beca.')
        self.assertEqual(r['estado'], 'INDETERMINADA')
        self.assertEqual(r['nuevos_atomos'], {'X3': 'Juan tiene una beca'})
        self.assertEqual(self.atomos, previo)

    def test_consulta_compuesta(self):
        r = self.consultar('Si Juan estudia, entonces aprueba.')
        self.assertEqual(r['estado'], 'DEMOSTRADA')
        self.assertEqual(r['expresion'], 'X1 → X2')

    def test_conjunto_inconsistente(self):
        reglas, atomos = base('Juan estudia.', 'Juan no estudia.')
        r = evaluar_consulta(reglas, atomos, 'Juan aprueba.', motor='dpll')
        self.assertEqual(r['estado'], 'INCONSISTENTE')
        self.assertIsNone(r['ejemplo_verdadero'])
        self.assertIsNone(r['contraejemplo'])

    def test_rechaza_atom_id_inexistente(self):
        with self.assertRaisesRegex(ValueError, 'no existe'):
            self.consultar('X9')

    def test_rechaza_pregunta_vacia(self):
        with self.assertRaises(ValueError):
            self.consultar('¿?')

    def test_rechaza_estructura_no_soportada(self):
        with self.assertRaises(ValueError):
            self.consultar('Juan estudia porque le gusta.')

    def test_regla_nueva_cambia_la_conclusion(self):
        texto = 'Si Juan estudia, entonces aprueba. Juan estudia.'
        self.assertEqual(consultar(texto, 'Juan aprueba')['consulta']['estado'], 'DEMOSTRADA')
        nuevo = texto + ' Juan no aprueba.'
        self.assertEqual(consultar(nuevo, 'Juan aprueba')['consulta']['estado'], 'INCONSISTENTE')

    def test_rechazar_entrada_con_reglas_invalidas(self):
        r = consultar('Juan estudia. Juan trabaja porque tiene dinero.', 'Juan estudia.')
        self.assertFalse(r['ok'])
        self.assertEqual(len(r['errores']), 1)
        self.assertNotIn('consulta', r)


if __name__ == '__main__':
    unittest.main()
