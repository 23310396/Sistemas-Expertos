import re

ALFABETO = 'pqrstuvwxyzabcdefghijklmno'


def letra(identificador):
    numero = int(identificador[1:]) - 1
    if numero < 0:
        raise ValueError('Átomo no válido')
    indice = numero % 26
    vuelta = numero // 26
    return ALFABETO[indice] + (str(vuelta) if vuelta else '')


def simbolizar(expresion):
    return re.sub(r'\bX[1-9]\d*\b', lambda m: letra(m.group()), str(expresion))
