from .parser import analizar_regla


def formatear_expresion(nodo):
    operador = nodo["op"]
    if operador == "ATOMO":
        return nodo["id"]
    if operador == "NO":
        hijo = nodo["args"][0]
        expresion = formatear_expresion(hijo)
        return f"¬({expresion})" if hijo["op"] in {"Y", "O", "IMPLICA"} else f"¬{expresion}"
    if operador in {"Y", "O", "IMPLICA"}:
        partes = []
        for hijo in nodo["args"]:
            expresion = formatear_expresion(hijo)
            if hijo["op"] in {"Y", "O", "IMPLICA"} and (operador == "IMPLICA" or hijo["op"] != operador):
                expresion = f"({expresion})"
            partes.append(expresion)
        if operador == "IMPLICA":
            return " → ".join(partes)
        return (" ∧ " if operador == "Y" else " ∨ ").join(partes)
    raise ValueError(f"Operador desconocido: {operador}")


class RegistroReglas:
    def __init__(self, registro_atomos):
        self.registro_atomos = registro_atomos
        self.reglas = []

    def agregar(self, texto):
        estructura = analizar_regla(texto, self.registro_atomos)
        regla = {
            "id": f"R{len(self.reglas) + 1}",
            "texto": texto,
            "estructura": estructura,
            "expresion": formatear_expresion(estructura),
        }
        self.reglas.append(regla)
        return regla

    def obtener_reglas(self):
        return self.reglas.copy()
