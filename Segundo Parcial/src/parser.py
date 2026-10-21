import re


class ErrorInterpretacion(ValueError):
    pass


VERBOS = set("""
acredita acreditan activa activan anda andan aprueba aprueban apruebe apruebes
asiste asisten baila bailan canta cantan compra compran come comen corre corren
cumple cumplen detecta detectan detiene detienen duerme duermen enciende
encienden entrega entregan estudia estudian falla fallan funciona funcionan
gana ganan gira giran inicia inician juega juegan lee leen llueve paga pagan
pasa pasan pierde pierden puede pueden recibe reciben sale salen trabaja
trabajan tiene tienen termina terminan vive viven es son está están estaba
estaban hay toma toman revisa revisan entra entran manda mandan envía envían
""".split())
ARTICULOS = {"el", "la", "los", "las", "un", "una", "unos", "unas"}
PRONOMBRES = {"yo", "tú", "tu", "él", "ella", "nosotros", "nosotras", "ustedes", "ellos", "ellas"}
NO_ADMITIDOS = re.compile(
    r"\b(?:pero|porque|aunque|mientras|cuando|a menos que|siempre que|si y solo si|solo si|solamente si|ni)\b",
    re.I,
)


def detectar_sujeto(texto):
    palabras = texto.split()
    if not palabras:
        return None
    primero = palabras[0]
    if re.fullmatch(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+", primero) and primero.casefold() not in {"si", "no"}:
        return primero
    if len(palabras) > 1 and primero.casefold() in ARTICULOS:
        return " ".join(palabras[:2])
    return None


def completar_sujeto(texto, sujeto):
    if (sujeto and not texto.casefold().startswith(sujeto.casefold() + " ")
            and not detectar_sujeto(texto) and texto.split()[0].casefold() not in PRONOMBRES):
        return f"{sujeto} {texto}"
    return texto


def revisar_parentesis(texto):
    nivel = 0
    for caracter in texto:
        nivel += (caracter == "(") - (caracter == ")")
        if nivel < 0:
            raise ErrorInterpretacion("Hay un paréntesis de cierre sin apertura.")
    if nivel:
        raise ErrorInterpretacion("Falta cerrar un paréntesis.")


def sin_parentesis_externos(texto):
    texto = texto.strip()
    while texto.startswith("(") and texto.endswith(")"):
        nivel = 0
        for posicion, caracter in enumerate(texto):
            nivel += (caracter == "(") - (caracter == ")")
            if nivel == 0 and posicion < len(texto) - 1:
                return texto
        texto = texto[1:-1].strip()
    return texto


def operadores_externos(texto, patron):
    nivel = 0
    vista = []
    for caracter in texto:
        if caracter == "(":
            nivel += 1
        vista.append(caracter if nivel == 0 else " ")
        if caracter == ")":
            nivel -= 1
    return list(re.finditer(patron, "".join(vista), re.I))


def es_proposicion(texto):
    texto = sin_parentesis_externos(texto)
    if re.fullmatch(r"X\d+|[A-Z]", texto):
        return True
    palabras = re.findall(r"[a-záéíóúüñ]+", texto.casefold())
    if palabras and palabras[0] in {"no", "se"}:
        palabras.pop(0)
    if not palabras:
        return False
    if palabras[0] in VERBOS:
        return True
    if len(palabras) > 1 and palabras[1] in VERBOS:
        return True
    if len(palabras) > 2 and palabras[1] == "no" and palabras[2] in VERBOS:
        return True
    if len(palabras) > 2 and palabras[0] in ARTICULOS:
        return palabras[2] in VERBOS or (
            len(palabras) > 3 and palabras[2] in {"se", "no"} and palabras[3] in VERBOS
        )
    return False


def nodo(operador, *hijos):
    return {"op": operador, "args": list(hijos)}


def interpretar(texto, sujeto=None):
    texto = sin_parentesis_externos(texto)
    if not texto:
        raise ErrorInterpretacion("Hay una condición o proposición vacía.")

    if re.match(r"^si\s+", texto, re.I):
        resto = re.sub(r"^si\s+", "", texto, count=1, flags=re.I)
        partes = operadores_externos(resto, r"\bentonces\b")
        if len(partes) != 1:
            raise ErrorInterpretacion('Usa la estructura "Si ..., entonces ...".')
        posicion = partes[0]
        izquierda = resto[:posicion.start()].strip().rstrip(",").strip()
        derecha = resto[posicion.end():].strip()
        sujeto_condicion = detectar_sujeto(sin_parentesis_externos(izquierda)) or sujeto
        return nodo("IMPLICA", interpretar(izquierda, sujeto_condicion), interpretar(derecha, sujeto_condicion))

    negacion = re.fullmatch(r"no es cierto que\s+(.+)", texto, re.I)
    if negacion:
        return nodo("NO", interpretar(negacion.group(1), sujeto))

    conectores = operadores_externos(texto, r"\b(y|o)\b")
    if conectores:
        tipos = {m.group().casefold() for m in conectores}
        if len(tipos) > 1:
            raise ErrorInterpretacion('Se mezclan "y" y "o" sin agruparlos entre paréntesis.')
        puntos = [0] + [m.end() for m in conectores]
        partes = [texto[puntos[i]:m.start()].strip() for i, m in enumerate(conectores)]
        partes.append(texto[conectores[-1].end():].strip())
        if any(not parte for parte in partes):
            raise ErrorInterpretacion("Falta una proposición junto a un conector.")
        for parte in partes:
            if not parte.startswith("(") and not es_proposicion(parte):
                raise ErrorInterpretacion(
                    f'No puedo saber si "y/o" une proposiciones en: "{parte}". '
                    "Reescribe la regla con oraciones completas."
                )
        sujeto_comun = detectar_sujeto(partes[0]) or sujeto
        return nodo("Y" if "y" in tipos else "O", *(interpretar(p, sujeto_comun) for p in partes))

    if NO_ADMITIDOS.search(texto):
        raise ErrorInterpretacion("La oración contiene un conector todavía no admitido.")
    if re.search(r"\bentonces\b", texto, re.I):
        raise ErrorInterpretacion('Encontré "entonces" sin una condición válida.')
    if re.search(r"\bsi\b", texto, re.I):
        raise ErrorInterpretacion('Encontré "si" fuera de la estructura "Si ..., entonces ...".')

    negacion_sujeto = re.fullmatch(
        r"((?:el|la|los|las|un|una)\s+\w+|[a-záéíóúñ]+)\s+no\s+(.+)",
        texto, re.I,
    )
    if negacion_sujeto:
        nombre, predicado = negacion_sujeto.groups()
        return nodo("NO", interpretar(f"{nombre} {predicado}", nombre))
    if re.match(r"^no\s+", texto, re.I):
        return nodo("NO", interpretar(texto[3:], sujeto))
    if re.search(r"\bno\b", texto, re.I):
        raise ErrorInterpretacion("No pude determinar el alcance de la negación.")
    return {"op": "ATOMO", "texto": completar_sujeto(texto, sujeto)}


def asignar_atomos(arbol, registro):
    if arbol["op"] == "ATOMO":
        return {"op": "ATOMO", "id": registro.registrar(arbol["texto"])}
    return nodo(arbol["op"], *(asignar_atomos(h, registro) for h in arbol["args"]))


def analizar_regla(texto, registro):
    texto = registro.normalizar(texto)
    if not texto:
        raise ErrorInterpretacion("La regla está vacía.")
    revisar_parentesis(texto)
    return asignar_atomos(interpretar(texto), registro)
