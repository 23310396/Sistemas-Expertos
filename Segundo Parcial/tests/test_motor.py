import unittest
from src.atomos import RegistroAtomos
from src.parser import analizar_regla, ErrorInterpretacion
from src.reglas import RegistroReglas


class TestRegistroAtomos(unittest.TestCase):

    def setUp(self):
        self.registro = RegistroAtomos()

    def test_primer_atomo(self):
        resultado = self.registro.registrar("Juan estudia")
        self.assertEqual(resultado, "X1")

    def test_varios_atomos(self):
        self.registro.registrar("Juan estudia")
        resultado = self.registro.registrar("Pedro trabaja")
        self.assertEqual(resultado, "X2")

    def test_evitar_duplicados(self):
        self.registro.registrar("Juan estudia")
        resultado = self.registro.registrar("  juan   estudia.  ")
        self.assertEqual(resultado, "X1")
        self.assertEqual(len(self.registro.obtener_atomos()), 1)

    def test_texto_vacio(self):
        with self.assertRaises(ValueError):
            self.registro.registrar("   ")

class TestInterprete(unittest.TestCase):

    def setUp(self):
        self.registro = RegistroAtomos()

    def test_condicional(self):
        arbol = analizar_regla(
            "Si Juan estudia y entrega la tarea, "
            "entonces aprueba el examen.",
            self.registro,
        )

        self.assertEqual(arbol["op"], "IMPLICA")
        self.assertEqual(arbol["args"][0]["op"], "Y")
        self.assertEqual(len(self.registro.obtener_atomos()), 3)

    def test_sujeto_omitido(self):
        analizar_regla(
            "Si Juan estudia y entrega la tarea, "
            "entonces aprueba el examen.",
            self.registro,
        )

        atomos = self.registro.obtener_atomos()
        self.assertEqual(atomos["X2"], "Juan entrega la tarea")
        self.assertEqual(atomos["X3"], "Juan aprueba el examen")

    def test_reutilizar_atomos(self):
        analizar_regla(
            "Si Juan estudia, entonces aprueba el examen.",
            self.registro,
        )

        analizar_regla(
            "Si Juan aprueba el examen, entonces pasa la materia.",
            self.registro,
        )

        self.assertEqual(len(self.registro.obtener_atomos()), 3)

    def test_negacion(self):
        resultado = analizar_regla(
            "Juan no estudia.", self.registro
        )
        self.assertEqual(resultado["op"], "NO")

    def test_disyuncion(self):
        resultado = analizar_regla(
            "Juan estudia o trabaja.", self.registro
        )
        self.assertEqual(resultado["op"], "O")

    def test_expresion_ambigua(self):
        with self.assertRaises(ErrorInterpretacion):
            analizar_regla(
                "Juan estudia y trabaja o duerme.",
                self.registro,
            )

class TestReglas(unittest.TestCase):

    def setUp(self):
        self.atomos = RegistroAtomos()
        self.reglas = RegistroReglas(self.atomos)

    def test_numeracion(self):
        r1 = self.reglas.agregar("Juan estudia.")
        r2 = self.reglas.agregar("Pedro trabaja.")

        self.assertEqual(r1["id"], "R1")
        self.assertEqual(r2["id"], "R2")

    def test_condicional_compuesto(self):
        regla = self.reglas.agregar(
            "Si Juan estudia y entrega la tarea, "
            "entonces aprueba el examen."
        )

        self.assertEqual(
            regla["expresion"],
            "(X1 ∧ X2) → X3"
        )

    def test_reutilizacion(self):
        self.reglas.agregar(
            "Si Juan estudia, entonces aprueba el examen."
        )
        regla = self.reglas.agregar(
            "Si Juan aprueba el examen, entonces pasa la materia."
        )

        self.assertEqual(regla["expresion"], "X2 → X3")
        self.assertEqual(len(self.atomos.obtener_atomos()), 3)

    def test_regla_no_interpretable(self):
        with self.assertRaises(ErrorInterpretacion):
            self.reglas.agregar(
                "Juan estudia y trabaja o duerme."
            )

        self.assertEqual(len(self.reglas.obtener_reglas()), 0)

class TestSeguridadParser(unittest.TestCase):

    def setUp(self):
        self.atomos = RegistroAtomos()
        self.reglas = RegistroReglas(self.atomos)

    def test_negacion_con_sujeto_y_otro_predicado(self):
        r = self.reglas.agregar(
            "Juan no estudia y trabaja."
        )

        self.assertEqual(
            r["expresion"], "¬X1 ∧ X2"
        )

        self.assertEqual(
            self.atomos.obtener_atomos(),
            {
                "X1": "Juan estudia",
                "X2": "Juan trabaja"
            }
        )

    def test_negacion_general_alcanza_ambos_terminos(self):
        r = self.reglas.agregar(
            "No es cierto que Juan estudia y trabaja."
        )

        self.assertEqual(
            r["expresion"], "¬(X1 ∧ X2)"
        )

    def test_condicional_sin_coma(self):
        r = self.reglas.agregar(
            "Si Juan estudia entonces aprueba."
        )

        self.assertEqual(
            r["expresion"], "X1 → X2"
        )

    def test_condicional_sujeto_con_articulo(self):
        r = self.reglas.agregar(
            "Si el robot funciona, entonces la alarma se activa."
        )

        self.assertEqual(
            r["expresion"], "X1 → X2"
        )

        self.assertEqual(
            self.atomos.obtener_atomos()["X2"],
            "la alarma se activa"
        )

    def test_parentesis(self):
        r = self.reglas.agregar(
            "Si Juan estudia y (Pedro trabaja o duerme), "
            "entonces Ana aprueba."
        )

        self.assertEqual(
            r["expresion"],
            "(X1 ∧ (X2 ∨ X3)) → X4"
        )

    def test_no_inventar_atom_cuando_hay_conector_desconocido(self):
        with self.assertRaises(ErrorInterpretacion):
            self.reglas.agregar(
                "Juan estudia porque mañana tiene examen."
            )

        self.assertEqual(
            self.atomos.obtener_atomos(), {}
        )

    def test_no_confundir_lista_nominal_con_reglas(self):
        with self.assertRaises(ErrorInterpretacion):
            self.reglas.agregar(
                "Juan compra pan y leche."
            )

        self.assertEqual(
            self.atomos.obtener_atomos(), {}
        )

    def test_un_error_no_registra_atomos_ni_reglas(self):
        self.reglas.agregar("Juan estudia.")

        with self.assertRaises(ErrorInterpretacion):
            self.reglas.agregar(
                "Pedro trabaja y come pan o leche."
            )

        self.assertEqual(
            self.atomos.obtener_atomos(),
            {"X1": "Juan estudia"}
        )

        self.assertEqual(
            len(self.reglas.obtener_reglas()), 1
        )

    def test_no_admite_si_sin_entonces(self):
        with self.assertRaises(ErrorInterpretacion):
            self.reglas.agregar(
                "Juan aprueba si estudia."
            )

    def test_parentesis_desbalanceados(self):
        with self.assertRaises(ErrorInterpretacion):
            self.reglas.agregar(
                "Si (Juan estudia y trabaja, entonces aprueba."
            )

        self.assertEqual(
            self.atomos.obtener_atomos(), {}
        )


class TestRegresiones(unittest.TestCase):
    def setUp(self):
        self.atomos = RegistroAtomos()
        self.reglas = RegistroReglas(self.atomos)

    def test_parrafo_en_una_linea(self):
        from src.main import separar_oraciones
        texto = "Si Juan estudia, entonces aprueba. Juan estudia. No es cierto que Pedro trabaja."
        partes = separar_oraciones(texto)
        self.assertEqual(len(partes), 3)
        for parte in partes:
            self.reglas.agregar(parte)
        self.assertEqual(len(self.reglas.obtener_reglas()), 3)

    def test_implicaciones_anidadas_con_parentesis(self):
        regla = self.reglas.agregar("Si Juan estudia, entonces (si Pedro trabaja, entonces Ana aprueba).")
        self.assertEqual(regla["expresion"], "X1 → (X2 → X3)")

    def test_negacion_en_minuscula_reutiliza_atomo(self):
        self.reglas.agregar("Juan estudia.")
        resultado = self.reglas.agregar("juan no estudia.")
        self.assertEqual(resultado["expresion"], "¬X1")
        self.assertEqual(len(self.atomos.obtener_atomos()), 1)

    def test_no_perder_atomos_tras_error(self):
        self.reglas.agregar("Ana trabaja.")
        with self.assertRaises(ErrorInterpretacion):
            self.reglas.agregar("Si Pedro estudia y trabaja o duerme, entonces aprueba.")
        self.assertEqual(self.atomos.obtener_atomos(), {"X1": "Ana trabaja"})

    def test_variables_symbolicas(self):
        self.assertEqual(self.reglas.agregar("Si P y Q, entonces R.")["expresion"], "(X1 ∧ X2) → X3")

