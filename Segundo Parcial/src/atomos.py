import re


class RegistroAtomos:
    def __init__(self):
        self.atomos = {}
        self.identificadores = {}

    def normalizar(self, texto):
        return re.sub(r"\s+", " ", texto.strip()).rstrip(".!?").strip()

    def registrar(self, proposicion):
        proposicion = self.normalizar(proposicion)
        if not proposicion:
            raise ValueError("La proposición no puede estar vacía.")

        clave = proposicion.casefold()
        if clave not in self.identificadores:
            identificador = f"X{len(self.atomos) + 1}"
            self.atomos[identificador] = proposicion
            self.identificadores[clave] = identificador
        return self.identificadores[clave]

    def obtener_atomos(self):
        return self.atomos.copy()
