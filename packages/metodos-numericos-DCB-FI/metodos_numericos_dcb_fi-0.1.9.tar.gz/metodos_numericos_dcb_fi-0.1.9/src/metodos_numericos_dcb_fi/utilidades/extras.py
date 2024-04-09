# ------------------- Importar módulos -------------------
from metodos_numericos_dcb_fi.utilidades.configuracion import text
from metodos_numericos_dcb_fi.utilidades.validacion import validarTipo

# ------------------- Importar bibliotecas -------------------
import numpy as np
import sympy as sp
from sympy.abc import x

# ------------------- Funciones -------------------
def calcularErrorRelativo(valorReal: float, valorAproximado: float) -> float:
    '''
    Calcula el error relativo entre un valor real y un valor aproximado.

    Parámetros:
        - valorReal (float): El valor real.
        - valorAproximado (float): El valor aproximado.

    Excepciones:
        - Exception: Se genera una excepción si alguno de los valores no es de tipo int o float.

    Retorno:
        - float: El error relativo entre los dos valores.

    Ejemplo:
        calcular_error_relativo(10.5, 10.2) -> 2.85714
    '''
    validarTipo(valorReal, (int, float))
    validarTipo(valorAproximado, (int, float))
    if valorReal == 0:
        return round(abs(valorReal - valorAproximado),5)
    return round(abs((valorReal - valorAproximado) / valorReal) * 100,5)

def calcularErrorAbsoluto(valorReal: float, valorAproximado: float) -> float:
    """
    Calcula el error absoluto entre un valor real y un valor aproximado.

    Parámetros:
        valorReal (float): El valor real.
        valorAproximado (float): El valor aproximado.

    Excepciones:
        Exception: Si alguno de los valores no es de tipo int o float.

    Retorno:
        float: El valor del error absoluto.

    Ejemplo:
        calcular_error_absoluto(10.5, 9.8) -> 0.7
    """
    validarTipo(valorReal, (int, float))
    validarTipo(valorAproximado, (int, float))
    return round(abs(valorReal - valorAproximado),5)

def quitarNan(valores_x:list, valores_y:list) -> tuple[list, list]:
    """
    Función: quitarNan

    Descripción:
    Esta función se utiliza para eliminar los valores NaN (Not a Number) de dos listas de valores, 'valores_x' y 'valores_y'. Los valores NaN son reemplazados por None en las listas actualizadas.

    Parámetros:
    - valores_x: una lista de valores.
    - valores_y: una lista de valores.

    Excepciones:
    - Exception: se lanza una excepción si las listas 'valores_x' y 'valores_y' no tienen la misma longitud o si alguno de los valores no es de tipo int o float.

    Retorno:
    - Una tupla que contiene dos listas actualizadas: 'valores_x_actualizado' y 'valores_y_actualizado'.

    Ejemplo de uso:
    quitarNan([1, 2, 3, np.nan], [4, np.nan, 6, 7])
    """
    validarTipo(valores_x, list)
    validarTipo(valores_y, list)
    if len(valores_x) != len(valores_y):
        raise Exception(f'{text["Utilidades"]["Errores"]["quitar_nan"].replace("{1}", len(valores_x)).replace("{2}", len(valores_y))}')
    valores_x_actualizado = []
    valores_y_actualizado = []
    len_y = len(valores_y)
    for i in range(len_y):
        validarTipo(valores_x[i], (int, float))
        validarTipo(valores_y[i], (int, float))
        if np.isfinite(valores_y[i]):
            valores_x_actualizado.append(valores_x[i])
            valores_y_actualizado.append(valores_y[i])
    return valores_x_actualizado, valores_y_actualizado

def obtenerRaiz(polinomio:list):
    if len(polinomio) == 2:
        return sp.solve(polinomio[0]*x + polinomio[1], x)
    if len(polinomio) == 3:
        raices = sp.solve(polinomio[0]*x**2 + polinomio[1]*x + polinomio[2], x)
        return raices[0], raices[1]