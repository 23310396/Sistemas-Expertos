import unittest

from src.atomos import RegistroAtomos
from src.reglas import RegistroReglas
from src.consultas import evaluar_consulta
from src.web import consultar


def probar(premisas, pregunta):
    atomos = RegistroAtomos()
    reglas = RegistroReglas(atomos)
    for texto in premisas:
        reglas.agregar(texto)
    return evaluar_consulta(reglas.obtener_reglas(), atomos.obtener_atomos(),
                            pregunta, motor='dpll')


class TestExplicacionesNaturales(unittest.TestCase):
    def test_demostrada_identifica_premisas(self):
        r = probar(['Si Juan estudia, entonces aprueba.', 'Juan estudia.'], 'Juan aprueba')
        self.assertEqual(r['estado'], 'DEMOSTRADA')
        for t in ('R1', 'R2', 'Juan estudia', 'consulta sea falsa'):
            self.assertIn(t, r['explicacion'])

    def test_no_cita_reglas_que_no_necesita(self):
        r = probar(['Si Juan estudia, entonces aprueba.', 'Juan estudia.', 'Pedro trabaja.'], 'Juan aprueba')
        self.assertNotIn('R3 (', r['explicacion'])

    def test_refutada_justifica(self):
        r = probar(['Si Juan estudia, entonces aprueba.', 'Juan estudia.'], 'Juan no aprueba')
        self.assertEqual(r['estado'], 'REFUTADA')
        self.assertIn('consulta sea verdadera', r['explicacion'])
        self.assertIn('R1', r['explicacion'])

    def test_indeterminada_muestra_ambos_mundos(self):
        r = probar(['Juan estudia o trabaja.'], 'Juan estudia')
        self.assertEqual(r['estado'], 'INDETERMINADA')
        self.assertIn('Juan estudia: verdadero', r['explicacion'])
        self.assertIn('Juan estudia: falso', r['explicacion'])

    def test_indeterminada_atom_nuevo(self):
        r = probar(['Juan estudia.'], 'Juan tiene una beca')
        self.assertIn('no aparece en las reglas', r['explicacion'])
        self.assertIn('Juan tiene una beca', r['explicacion'])

    def test_inconsistente_menciona_conflicto(self):
        r = probar(['Juan estudia.', 'Juan no estudia.', 'Pedro trabaja.'], 'Juan aprueba')
        self.assertEqual(r['estado'], 'INCONSISTENTE')
        self.assertIn('R1', r['explicacion'])
        self.assertIn('R2', r['explicacion'])
        self.assertNotIn('R3 (', r['explicacion'])

    def test_compuesta_explicacion(self):
        r = probar(['Juan estudia.', 'Pedro trabaja.'], 'Juan estudia y Pedro trabaja')
        self.assertEqual(r['estado'], 'DEMOSTRADA')
        self.assertIn('R2', r['explicacion'])

    def test_reglas_numerosas_no_bloquean_respuesta(self):
        r = probar(['Juan estudia.'] * 25, 'Juan estudia')
        self.assertEqual(r['estado'], 'DEMOSTRADA')
        self.assertIn('no existe una asignación', r['explicacion'].lower())

    def test_api_conserva_campo_de_explicacion(self):
        r = consultar('Si Juan estudia, entonces aprueba. Juan estudia.', 'Juan aprueba')
        self.assertTrue(r['ok'])
        self.assertIn('R1', r['consulta']['explicacion'])


if __name__ == '__main__':
    unittest.main()
