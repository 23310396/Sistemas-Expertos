import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from src import dominios
from src.web import Servidor, analizar


class TestDominios(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patcher = patch.object(dominios, 'CARPETA', Path(self.tmp.name))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()

    def test_crear_y_listar_dos_dominios(self):
        dominios.crear('estudiantes')
        dominios.crear('robots')
        self.assertEqual([x['nombre'] for x in dominios.listar()], ['estudiantes', 'robots'])
        self.assertFalse((Path(self.tmp.name) / 'robots.calculos.md').exists())

    def test_rechaza_nombres_peligrosos(self):
        for nombre in ('../fuera', 'otro/dominio', '', '.oculto', 'nombre con espacios', 'a' * 51):
            with self.subTest(nombre=nombre):
                with self.assertRaises(ValueError):
                    dominios.crear(nombre)

    def test_sobrescribe_un_mismo_reporte(self):
        dom = dominios.crear('estudiantes')
        texto = 'Si Juan estudia, entonces aprueba. Juan estudia.'
        resultado = dominios.guardar_analisis('estudiantes', texto, dom['revision'], analizar)
        self.assertTrue(resultado['ok'])
        carpeta = Path(self.tmp.name)
        self.assertEqual(len(list(carpeta.iterdir())), 2)
        md = carpeta / 'estudiantes.calculos.md'
        primero = md.read_text(encoding='utf-8')
        self.assertIn('## Reglas: texto, lógica y FNC', primero)
        self.assertIn('## FNC completa', primero)
        self.assertIn('**SAT**', primero)
        self.assertTrue(resultado['dominio']['calculado'])

        texto2 = 'Si Juan estudia, entonces aprueba. Juan estudia. Juan no aprueba.'
        resultado2 = dominios.guardar_analisis('estudiantes', texto2, resultado['dominio']['revision'], analizar)
        self.assertTrue(resultado2['ok'])
        self.assertEqual(len(list(carpeta.iterdir())), 2)
        segundo = md.read_text(encoding='utf-8')
        self.assertNotEqual(primero, segundo)
        self.assertIn('**UNSAT**', segundo)
        self.assertEqual((carpeta / 'estudiantes.txt').read_text(encoding='utf-8'), texto2)

    def test_texto_sin_analisis_vuelve_obsoletos_los_calculos(self):
        d = dominios.crear('motor')
        d = dominios.guardar_analisis('motor', 'Juan estudia.', d['revision'], analizar)['dominio']
        self.assertTrue(d['calculado'])
        guardado = dominios.guardar_texto('motor', 'Juan trabaja.', d['revision'])
        self.assertFalse(guardado['calculado'])
        self.assertTrue(guardado['tiene_calculos'])
        d = dominios.guardar_analisis('motor', 'Juan trabaja.', guardado['revision'], analizar)['dominio']
        self.assertTrue(d['calculado'])

    def test_conflicto_por_edicion_externa(self):
        d = dominios.crear('ejemplo')
        (Path(self.tmp.name) / 'ejemplo.txt').write_text('Pedro trabaja.', encoding='utf-8')
        with self.assertRaises(dominios.ConflictoDominio):
            dominios.guardar_texto('ejemplo', 'Ana trabaja.', d['revision'])
        self.assertEqual((Path(self.tmp.name) / 'ejemplo.txt').read_text(), 'Pedro trabaja.')

    def test_conflicto_no_reemplaza_reporte(self):
        d = dominios.crear('ejemplo')
        d = dominios.guardar_analisis('ejemplo', 'Pedro trabaja.', d['revision'], analizar)['dominio']
        reporte_anterior = (Path(self.tmp.name) / 'ejemplo.calculos.md').read_text()
        (Path(self.tmp.name) / 'ejemplo.txt').write_text('Cambio externo.', encoding='utf-8')
        with self.assertRaises(dominios.ConflictoDominio):
            dominios.guardar_analisis('ejemplo', 'Ana trabaja.', d['revision'], analizar)
        self.assertEqual((Path(self.tmp.name) / 'ejemplo.calculos.md').read_text(), reporte_anterior)

    def test_entrada_invalida_se_conserva_en_txt_sin_calculos_vigentes(self):
        d = dominios.crear('invalido')
        r = dominios.guardar_analisis('invalido', 'Juan trabaja.', d['revision'], analizar)
        nuevo = 'Juan trabaja porque le pagan.'
        r2 = dominios.guardar_analisis('invalido', nuevo, r['dominio']['revision'], analizar)
        self.assertFalse(r2['ok'])
        self.assertEqual(r2['dominio']['texto'], nuevo)
        self.assertFalse(r2['dominio']['calculado'])
        self.assertEqual(len(list(Path(self.tmp.name).glob('*.calculos.md'))), 1)


class TestAPIDominios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.patcher = patch.object(dominios, 'CARPETA', Path(cls.tmp.name))
        cls.patcher.start()
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Servidor)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.patcher.stop()
        cls.tmp.cleanup()

    def pedido(self, ruta, cuerpo=None):
        argumentos = {} if cuerpo is None else {
            'data': json.dumps(cuerpo).encode('utf-8'),
            'headers': {'Content-Type':'application/json'},
        }
        req = Request(self.url + ruta, **argumentos)
        try:
            with urlopen(req, timeout=8) as respuesta:
                if ruta.startswith('/api/dominio/calculos'):
                    return respuesta.status, respuesta.read().decode('utf-8')
                return respuesta.status, json.load(respuesta)
        except HTTPError as exc:
            return exc.code, json.load(exc)

    def test_ciclo_http(self):
        status, d = self.pedido('/api/dominios', {'nombre':'laboratorio'})
        self.assertEqual(status, 200)
        rev = d['dominio']['revision']
        status, d = self.pedido('/api/dominio/guardar', {'nombre':'laboratorio','texto':'Juan estudia.','revision':rev})
        self.assertEqual(status, 200)
        self.assertFalse(d['dominio']['calculado'])
        rev = d['dominio']['revision']
        status, d = self.pedido('/api/dominio/analizar', {'nombre':'laboratorio','texto':'Juan estudia.','revision':rev})
        self.assertEqual(status, 200)
        self.assertTrue(d['dominio']['calculado'])
        self.assertEqual(d['sat']['estado'], 'SAT')
        status, listado = self.pedido('/api/dominios')
        self.assertEqual(status, 200)
        self.assertTrue(any(x['nombre']=='laboratorio' for x in listado['dominios']))
        status, reporte = self.pedido('/api/dominio/calculos?nombre=laboratorio')
        self.assertEqual(status, 200)
        self.assertIn('## DIMACS', reporte)
        status, d = self.pedido('/api/dominio?nombre=laboratorio')
        self.assertEqual(status, 200)
        self.assertEqual(d['dominio']['texto'], 'Juan estudia.')

    def test_http_conflicto_devuelve_409(self):
        s, d = self.pedido('/api/dominios', {'nombre':'externo'})
        self.assertEqual(s, 200)
        viejo = d['dominio']['revision']
        (Path(self.tmp.name) / 'externo.txt').write_text('Juan estudia.', encoding='utf-8')
        estado, resultado = self.pedido('/api/dominio/guardar', {'nombre':'externo','revision':viejo,'texto':'Pedro trabaja.'})
        self.assertEqual(estado, 409)
        self.assertTrue(resultado['conflicto'])

    def test_http_path_traversal(self):
        s, d = self.pedido('/api/dominio?nombre=..%2Fafuera')
        self.assertEqual(s, 422)
        self.assertFalse(d['ok'])
