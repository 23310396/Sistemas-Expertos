import re
import sys
from pathlib import Path

from .atomos import RegistroAtomos
from .parser import ErrorInterpretacion
from .reglas import RegistroReglas
from .simbolos import letra, simbolizar


def separar_oraciones(texto):
    return [parte.strip() for parte in re.split(r"\r?\n+|(?<=[.!?;])\s+", texto) if parte.strip()]


def mostrar(titulo, elementos):
    print(f"\n{'=' * 45}\n{titulo}\n{'=' * 45}")
    for elemento in elementos:
        print(elemento)


def main():
    archivo = Path(sys.argv[1]) if len(sys.argv) > 1 else (Path("dominios/entrada.txt") if Path("dominios/entrada.txt").exists() else Path("dominios/ejemplo.txt"))
    try:
        texto = archivo.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        print(f"No se pudo leer el archivo: {error}")
        return 1

    atomos = RegistroAtomos()
    reglas = RegistroReglas(atomos)
    errores = []
    for oracion in separar_oraciones(texto):
        try:
            reglas.agregar(oracion)
        except (ErrorInterpretacion, ValueError) as error:
            errores.append((oracion, error))

    print("\nSISTEMA DE INTERPRETACION LOGICA")
    mostrar("ATOMOS IDENTIFICADOS", (f"{letra(id)} = {texto}" for id, texto in atomos.obtener_atomos().items()))
    mostrar("REGLAS IDENTIFICADAS", (f"{r['id']} = {simbolizar(r['expresion'])}" for r in reglas.obtener_reglas()))
    if errores:
        mostrar("ORACIONES NO INTERPRETADAS", (f"- {texto}\n  Motivo: {error}" for texto, error in errores))
    print(f"\n{'=' * 45}")
    print(f"Total de atomos: {len(atomos.obtener_atomos())}")
    print(f"Total de reglas: {len(reglas.obtener_reglas())}")
    print(f"Oraciones no interpretadas: {len(errores)}")
    print("=" * 45)
    return int(bool(errores))


if __name__ == "__main__":
    sys.exit(main())
