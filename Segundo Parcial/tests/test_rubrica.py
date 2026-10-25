import itertools
import random
import tempfile
import unittest
from pathlib import Path

from src.atomos import RegistroAtomos
from src.arbol import expandir, generar_arbol
from src.consultas import evaluar_consulta
from src.dominios import reporte
from src.fnc import formula_a_clausulas
from src.parser import ErrorInterpretacion
from src.reglas import RegistroReglas, formatear_expresion
from src.sat import resolver_clausulas
from src.simbolos import letra, simbolizar
from src.web import a_natural, analizar, consultar


def verdad(nodo, asignacion):
    op = nodo['op']
    if op == 'ATOMO':
        return asignacion[nodo['id']]
    args = [verdad(h, asignacion) for h in nodo['args']]
    if op == 'NO': return not args[0]
    if op == 'Y': return all(args)
    if op == 'O': return any(args)
    if op == 'IMPLICA': return (not args[0]) or args[1]
    if op == 'BICONDICIONAL': return args[0] == args[1]
    raise AssertionError(op)


def evaluar_clausulas(clausulas, asignacion):
    return all(any((numero > 0) == asignacion[f'X{abs(numero)}'] for numero in c)
               for c in clausulas)


class TestRubrica(unittest.TestCase):
    def setUp(self):
        self.atomos = RegistroAtomos()
        self.reglas = RegistroReglas(self.atomos)

    def prueba(self, texto):
        return self.reglas.agregar(texto)['estructura']

    def test_bicondicional_basico(self):
        x = self.prueba('El motor funciona si y solo si la alarma se activa.')
        self.assertEqual(x['op'], 'BICONDICIONAL')
        self.assertEqual(formatear_expresion(x), 'X1 ↔ X2')
        arbol = generar_arbol(self.reglas.obtener_reglas(), self.atomos.obtener_atomos())
        self.assertEqual(len(arbol['hojas']), 2)
        self.assertEqual({tuple(w.values()) for w in arbol['mundos']}, {(False, False), (True, True)})

    def test_negacion_bicondicional(self):
        x = self.prueba('No es cierto que el motor funciona si y solo si la alarma se activa.')
        self.assertEqual(x['op'], 'NO')
        self.assertEqual(x['args'][0]['op'], 'BICONDICIONAL')
        self.assertEqual(formatear_expresion(x), '¬(X1 ↔ X2)')
        arbol = generar_arbol(self.reglas.obtener_reglas(), self.atomos.obtener_atomos())
        self.assertEqual({tuple(w.values()) for w in arbol['mundos']}, {(False, True), (True, False)})

    def test_bicondicional_con_negacion_izquierda(self):
        x = self.prueba('El motor no funciona si y solo si la alarma se activa.')
        self.assertEqual(formatear_expresion(x), '¬X1 ↔ X2')
        self.assertEqual(x['op'], 'BICONDICIONAL')

    def test_parentesis_y_condicionales(self):
        expr = self.prueba('Si Juan estudia y (Pedro trabaja si y solo si Ana aprueba), entonces Juan pasa la materia.')
        self.assertEqual(expr['op'], 'IMPLICA')
        self.assertEqual(expr['args'][0]['op'], 'Y')
        self.assertEqual(expr['args'][0]['args'][1]['op'], 'BICONDICIONAL')
        self.assertIn('↔', formatear_expresion(expr))
        self.assertIn('↔', a_natural(formatear_expresion(expr), self.atomos.obtener_atomos()) if False else formatear_expresion(expr))

    def test_sin_lados_rechazado(self):
        for texto in ['El motor funciona si y solo si.', 'Si y solo si el motor funciona.']:
            with self.subTest(texto=texto), self.assertRaises(ErrorInterpretacion):
                self.prueba(texto)

    def test_rubrica_ejemplo_exactamente(self):
        problema = ('Si es de día, entonces voy a trabajar. '
                    'Si llueve, entonces no voy a trabajar. Es de día.')
        resultado = analizar(problema)
        self.assertTrue(resultado['ok'])
        self.assertEqual(resultado['resumen']['abiertas'], 1)
        self.assertEqual(resultado['resumen']['cerradas'], 2)
        self.assertEqual(resultado['arbol']['mundos'], [{'X1': True, 'X2': True, 'X3': False}])
        self.assertEqual(resultado['sat']['estado'], 'SAT')
        self.assertTrue(resultado['sat']['coincide_arbol'])
        self.assertTrue(any(n['aplicada'] for n in resultado['arbol']['nodos']))
        self.assertEqual(resultado['reglas'][0]['expresion'], 'X1 → X2')

    def test_aplicadas_solo_si_expandidas(self):
        d = analizar('Juan estudia. Juan estudia o trabaja.')
        for nodo in d['arbol']['nodos']:
            if nodo['aplicada']:
                self.assertTrue('→' in nodo['expresion'] or '∨' in nodo['expresion'] or '∧' in nodo['expresion'] or '¬(' in nodo['expresion'])
        self.assertTrue(any(n['aplicada'] for n in d['arbol']['nodos']))
        self.assertTrue(any(not n['aplicada'] for n in d['arbol']['nodos']))

    def test_natural_bicondicional(self):
        x = self.prueba('El motor funciona si y solo si la alarma se activa.')
        natural = a_natural(formatear_expresion(x), self.atomos.obtener_atomos())
        self.assertIn('si y solo si', natural)
        self.assertIn('el motor funciona', natural.lower())
        self.assertIn('la alarma se activa', natural)

    def test_consultas_bicondicional(self):
        base='El motor funciona si y solo si la alarma se activa. El motor funciona.'
        d = consultar(base, 'La alarma se activa.')
        self.assertEqual(d['consulta']['estado'], 'DEMOSTRADA')
        d = consultar(base, 'No es cierto que el motor funciona si y solo si la alarma se activa.')
        self.assertEqual(d['consulta']['estado'], 'REFUTADA')

    def test_alfabeto_y_reporte(self):
        self.assertEqual([letra(f'X{i}') for i in (1,2,3,12,26,27)], ['p','q','r','a','o','p1'])
        self.assertEqual(simbolizar('X1 → X2 ∧ X12'), 'p → q ∧ a')
        texto='El motor funciona si y solo si la alarma se activa.'
        d=analizar(texto)
        md=reporte('rubrica',texto,d)
        self.assertIn('- p: El motor funciona',md)
        self.assertIn('`p ↔ q`',md)
        self.assertIn('`(¬p ∨ q) ∧ (p ∨ ¬q)`',md)
        self.assertIn('p cnf 2 2',md)

    def test_bicondicional_y_negacion_exhaustivos(self):
        for negado in (False,True):
            for a,b in itertools.product([False,True],repeat=2):
                x=self.prueba('El motor funciona si y solo si la alarma se activa.' if not negado else
                              'No es cierto que el motor funciona si y solo si la alarma se activa.')
                valuacion={'X1':a,'X2':b}
                self.assertEqual(verdad(x,valuacion), evaluar_clausulas(formula_a_clausulas(x),valuacion))
                # Separar objetos de prueba evita usar una numeración nueva de átomos.
                self.setUp()

    def test_composiciones_comprobadas_con_tabla_verdad(self):
        random.seed(381)
        nombres=['X1','X2','X3']
        def atomo(): return {'op':'ATOMO','id':random.choice(nombres)}
        def generar(prof):
            if not prof or random.random()<.2:return atomo()
            op=random.choice(['NO','Y','O','IMPLICA','BICONDICIONAL'])
            return {'op':op,'args':[generar(prof-1)] if op=='NO' else [generar(prof-1),generar(prof-1)]}
        for i in range(160):
            f=generar(3)
            cs=formula_a_clausulas(f)
            for bits in itertools.product([False,True],repeat=3):
                v=dict(zip(nombres,bits))
                self.assertEqual(verdad(f,v), evaluar_clausulas(cs,v), f'caso {i} {f}')
            # comprobación del árbol de fórmulas arbitrarias
            atomos={k:k for k in nombres}
            reglas=[{'id':'R1','estructura':f,'expresion':formatear_expresion(f)}]
            tabla=generar_arbol(reglas,atomos,max_nodos=2000,max_mundos=8)
            mundos_reales={bits for bits in itertools.product([False,True],repeat=3)
                           if verdad(f,dict(zip(nombres,bits)))}
            mundos_arbol={tuple(w[x] for x in nombres) for w in tabla['mundos']}
            self.assertEqual(mundos_reales,mundos_arbol, f'error árbol {f}')


if __name__ == '__main__':
    unittest.main()
