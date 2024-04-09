import numpy as np


# TODO change the reduced chi square function and translate the docstring to english.
def reduced_chi_square(f, x, y, y_err, params: list[float]) -> float:
    """Berechnet das X² pro Freiheitsgrad für eine Funktion f mit parametern <params>
    f: hat die Form f(params, __x)
    __x: ist ein Array der unabhängigen Variable
    y: ist ein Array der von __x abhängigen Variable
    y_err: Fehler von y, kann ein Array oder ein skalarer Wert sein"""

    try:
        iter(x)
        iter(y)
    except TypeError:
        print("__x and/ or y not an iterable")
        exit(-1)

    try:
        iter(y_err)
    except TypeError:
        y_err = [y_err] * len(x)

    x, y, y_err = np.array(x), np.array(y), np.array(y_err)

    chi_square = np.sum((y - f(params, x)) ** 2 / y_err ** 2)
    return chi_square / (len(x) - len(params))


