import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src.web import BASE, Servidor, a_natural, analizar


class TestWeb(unittest.TestCase):
    def test_una_rama_abierta_y_otra_cerrada(self):
        d = analizar('Si Juan estudia, entonces aprueba. Juan estudia.')
        self.assertTrue(d['ok'])
        self.assertEqual(d['resumen']['abiertas'], 1)
        self.assertEqual(d['resumen']['cerradas'], 1)
        self.assertEqual(len(d['atomos']), 2)
        self.assertEqual(d['arbol']['mundos'], [{'X1': True, 'X2': True}])
        self.assertIn('Si Juan estudia, entonces Juan aprueba', d['arbol']['nodos'][0]['natural'])

    def test_problema_contradiccion(self):
        d = analizar('Juan estudia. Juan no estudia.')
        self.assertFalse(d['arbol']['compatible'])
        self.assertEqual(d['resumen']['abiertas'], 0)
        self.assertGreater(d['resumen']['cerradas'], 0)
        self.assertTrue(any(n['contradiccion'] for n in d['arbol']['nodos']))

    def test_no_generar_arbol_parcial(self):
        d = analizar('Juan estudia. Juan aprueba porque estudia.')
        self.assertFalse(d['ok'])
        self.assertEqual(len(d['errores']), 1)

    def test_cadena_de_implicaciones(self):
        texto = 'Si Juan estudia, entonces (si Pedro trabaja, entonces Ana aprueba).'
        d = analizar(texto)
        self.assertTrue(d['ok'])
        self.assertIn('Si Juan estudia, entonces', d['arbol']['nodos'][0]['natural'])

    def test_rechaza_textos_vacios(self):
        with self.assertRaises(ValueError):
            analizar('  ')

    def test_lectura_natural_agrupada(self):
        frase = a_natural('¬(X1 ∧ X2)', {'X1': 'Juan estudia', 'X2': 'Ana trabaja'})
        self.assertIn('no es cierto que', frase)
        self.assertIn('Juan estudia y Ana trabaja', frase)



class TestInterfazFNCySAT(unittest.TestCase):
    def test_fnc_y_sat_con_reglas_compatibles(self):
        data = analizar(
            'Si Juan estudia y entrega la tarea, entonces aprueba el examen. '
            'Si Juan aprueba el examen, entonces pasa la materia. '
            'Juan estudia. Juan entrega la tarea.'
        )
        self.assertTrue(data['ok'])
        self.assertEqual(data['fnc']['clausulas'], [[-1, -2, 3], [-3, 4], [1], [2]])
        self.assertEqual(data['sat']['estado'], 'SAT')
        self.assertTrue(data['sat']['coincide_arbol'])
        self.assertEqual(data['sat']['soluciones'], [dict.fromkeys(('X1', 'X2', 'X3', 'X4'), True)])
        self.assertEqual(len(data['fnc']['reglas']), 4)

    def test_problema_contradictorio(self):
        data = analizar('Si Juan estudia, entonces aprueba. Juan estudia. Juan no aprueba.')
        self.assertTrue(data['ok'])
        self.assertEqual(data['sat']['estado'], 'UNSAT')
        self.assertFalse(data['arbol']['compatible'])
        self.assertTrue(data['sat']['coincide_arbol'])
        self.assertEqual(data['sat']['soluciones'], [])

    def test_varios_mundos_y_limite(self):
        data = analizar('Juan estudia o trabaja.')
        self.assertEqual(data['sat']['estado'], 'SAT')
        self.assertEqual(len(data['sat']['soluciones']), 3)
        self.assertFalse(data['sat']['hay_mas'])

    def test_fnc_de_implicacion_anidada(self):
        data = analizar('Si Juan estudia, entonces (si Pedro trabaja, entonces Ana aprueba).')
        self.assertEqual(data['fnc']['clausulas'], [[-1, -2, 3]])
        self.assertTrue(data['sat']['coincide_arbol'])

    def test_no_aceptar_salida_parcial_con_error_de_texto(self):
        data = analizar('Juan estudia. Juan trabaja porque le pagan.')
        self.assertFalse(data['ok'])
        self.assertNotIn('fnc', data)
        self.assertNotIn('sat', data)

    def test_dimacs_contiene_cabecera_y_terminadores(self):
        data = analizar('Si Juan estudia, entonces aprueba. Juan estudia.')
        self.assertEqual(data['fnc']['dimacs'].splitlines(), ['p cnf 2 2', '-1 2 0', '1 0'])

    def test_html_contiene_cuatro_pestanas(self):
        html = (BASE / 'static/index.html').read_text(encoding='utf-8')
        for fragmento in ['id="tab-arbol"', 'id="tab-fnc"', 'id="tab-sat"', 'id="tab-consultas"',
                          'id="fnc-reglas"', 'id="sat-soluciones"']:
            self.assertIn(fragmento, html)

    def test_js_usa_misma_solicitud_para_tres_resultados(self):
        javascript = (BASE / 'static/app.js').read_text(encoding='utf-8')
        self.assertIn('mostrarFnc(datos);mostrarSat(datos);dibujar();', javascript)
        self.assertIn("$('vista-' + nombre).hidden", javascript)


class TestServidorConsultas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Servidor)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/api/consultar'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def enviar(self, cuerpo):
        r = Request(self.url, data=json.dumps(cuerpo).encode(), headers={'Content-Type':'application/json'})
        try:
            with urlopen(r, timeout=5) as resp:
                return resp.status, json.load(resp)
        except HTTPError as error:
            return error.code, json.load(error)

    def test_pregunta_mediante_http(self):
        status, r = self.enviar({'texto':'Si Juan estudia, entonces aprueba. Juan estudia.', 'pregunta':'Juan aprueba'})
        self.assertEqual(status, 200)
        self.assertTrue(r['ok'])
        self.assertEqual(r['consulta']['estado'], 'DEMOSTRADA')

    def test_error_de_consulta_http(self):
        status, r = self.enviar({'texto':'Juan estudia.', 'pregunta':''})
        self.assertEqual(status, 422)
        self.assertFalse(r['ok'])

    def test_html_incluye_consultas_y_agregar(self):
        html = (BASE / 'static/index.html').read_text(encoding='utf-8')
        for fragmento in ['id="tab-consultas"', 'id="consulta-resultado"', 'id="agregar-regla"', 'id="nueva-regla"']:
            self.assertIn(fragmento, html)

    def test_js_incluye_conexion_api_y_limpieza(self):
        js = (BASE / 'static/app.js').read_text(encoding='utf-8')
        self.assertIn("fetch('/api/consultar'", js)
        self.assertIn('limpiarConsulta();', js)
        self.assertIn('await analizar();', js)


class TestLimpiezaResultados(unittest.TestCase):
    def test_editor_vacio_limpia_calculos_previos(self):
        javascript = (BASE / 'static/app.js').read_text(encoding='utf-8')
        inicio = javascript.index('async function analizar()')
        manejo_vacio = javascript[inicio:javascript.index("$('analizar').disabled=true", inicio)]
        self.assertIn('limpiarResultados()', manejo_vacio)
        self.assertIn('estado.data=null', manejo_vacio)
