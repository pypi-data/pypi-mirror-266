# ------------------- Importar módulos -------------------
from metodos_numericos_dcb_fi.utilidades.configuracion import text, letras_latinas, letras_griegas
from metodos_numericos_dcb_fi.utilidades.validacion import validarTipo

# ------------------- Importar bibliotecas -------------------
from typing import List
import sympy as sp
from sympy import Symbol, Poly
from IPython.display import display, Math
import pandas as pd
import numpy as np

# ------------------- Funciones -------------------
def mostrarPolinomio(a:list[float], variable:str='x', titulo:str='')->None:
    '''
    Muestra un polinomio en formato matemático.

    Parámetros:
        a (list): Lista de coeficientes del polinomio.
        variable (str, opcional): Variable del polinomio. Por defecto es 'x'.
        titulo (str, opcional): Título que se mostrará antes del polinomio. Por defecto es ''.

    Excepciones:
        TypeError: Si 'a' no es una lista o si los coeficientes no son números.
        ValueError: Si la variable contiene caracteres que no son letras latinas o griegas.

    Retorno:
        None. Muestra el polinomio en formato matemático.

    Ejemplo:
        mostrarPolinomio([1, -2, 3], 'p', 'Polinomio de grado 2')
    '''
    # validar que a sea una lista
    validarTipo(a, list)
    # validar que los coeficientes sean números
    for coeficiente in a:
        validarTipo(coeficiente, (int, float))
    # validar que la variable sea al menos un caracter
    if len(variable) == 0:
        raise ValueError(f'{text["Utilidades"]["Errores"]["len_variable"].replace("{1}", 1).replace("{2}", len(variable))}')
    # validar si todos los caracteres de la variable son letras latinas o griegas
    for letra in variable:
        if not (letra in letras_latinas + letras_griegas):
            raise ValueError(f'{text["Utilidades"]["Errores"]["variable"].replace("{1}", variable)}')
    # Si la variable es mas de 1 caracter poerla entre parentesis en el polinomio 
    if len(variable)>1:
        variable = f'({variable})'
    polinomio = ''
    grad = len(a) - 1
    for i, coeficiente in enumerate(a[:-2]):
        if coeficiente != 0:
            sign = '-' if coeficiente < 0 else '+'
            polinomio += f'{sign} {abs(round(coeficiente, 3))}*{variable}**{grad - i} '
    if a[-2] != 0:
        sign = '-' if a[-2] < 0 else '+'
        polinomio += f'{sign} {abs(round(a[-2], 3))}*{variable} '
    if a[-1] != 0:
        sign = '-' if a[-1] < 0 else '+'
        polinomio += f'{sign} {abs(round(a[-1], 3))}'
    # Eliminar los parentesis que se agregaron para la variable
    if len(variable)>1:
        variable = variable[1:-1]
    var = Symbol(f'{variable}')
    polinomio = Poly(polinomio, var)
    if titulo != '': print(titulo)
    display(Math(f'P_{grad}({variable}) = ' + sp.latex(polinomio.as_expr())))

def crearTablaFactoresCuadraticos(a: List[float]) -> pd.DataFrame:
    '''
    Crea una tabla vacía para almacenar los coeficientes del método factores cuadráticos.

    Parámetros:
        a (List[float]): Una lista de coeficientes.

    Excepciones:
        TypeError: Si 'a' no es una lista o si alguno de los coeficientes no es un número.

    Retorno:
        pd.DataFrame: Una tabla vacía con las columnas 'Iteracion', 'p', 'q', 'b_0', 'b_1', ..., 'R', 'S', 'Δp', 'Δq'.

    Ejemplo:
        crearTablaFactoresCuadraticos([1, 2, 3])
    '''
    # validar que a sea una lista
    validarTipo(a, list)
    # validar que los coeficientes sean números
    for coeficiente in a:
        validarTipo(coeficiente, (int, float))
    
    columnas = ['Iteracion','p','q'] + [f'b_{k}' for k in range(len(a) - 2)] + ['R', 'S', '\u0394p','\u0394q']
    tabla = pd.DataFrame(columns=columnas)
    tabla.set_index('Iteracion', inplace=True)
    return tabla

def agregarRenglonFactoresCuadraticos(tabla:pd.DataFrame, p:float, q:float, b:list[float], R:float, S:float, dp:float, dq:float)->pd.DataFrame:
    '''
    Agrega un nuevo renglón a una tabla de datos que contiene factores cuadráticos.

    Parámetros:
    - tabla: DataFrame de pandas que representa la tabla de datos.
    - p: Valor numérico (int o float) que representa el factor p.
    - q: Valor numérico (int o float) que representa el factor q.
    - b: Lista de valores numéricos (int o float) que representa los coeficientes b.
    - R: Valor numérico (int o float) que representa el factor R.
    - S: Valor numérico (int o float) que representa el factor S.
    - dp: Valor numérico (int o float) que representa el factor dp.
    - dq: Valor numérico (int o float) que representa el factor dq.

    Excepciones:
    - Exception: Se lanza una excepción si alguno de los parámetros no cumple con el tipo de dato esperado.

    Retorno:
    - DataFrame de pandas: La tabla de datos actualizada con el nuevo renglón agregado.

    Ejemplo de uso:
    tabla = agregarRenglonFactoresCuadraticos(tabla, 0.5, 0.2, [1, 2, 3], 0.8, 0.6, 0.1, 0.3)
    '''
    # validar los tipos de los parámetros
    validarTipo(tabla, pd.DataFrame)
    validarTipo(p, (int, float))
    validarTipo(q, (int, float))
    validarTipo(b, list)
    for coeficiente in b:
        validarTipo(coeficiente, (int, float))
    validarTipo(R, (int, float))
    validarTipo(S, (int, float))
    validarTipo(dp, (int, float))
    validarTipo(dq, (int, float))
    # validar la longitud de b
    if len(b) != len(tabla.columns) - 6:
        raise Exception(f'{text["Utilidades"]["Errores"]["len_b_FC"].replace("{1}", len(tabla.columns) - 6).replace("{2}", len(b))}')
    # agregar un renglón a la tabla
    nuevo_renglon = [p, q]
    nuevo_renglon.extend(b)
    nuevo_renglon.extend([R, S, dp, dq])
    tabla.loc[len(tabla)+1] = nuevo_renglon
    return tabla

def mostrarTablaFactoresCuadraticos(tabla:pd.DataFrame)->None:
    '''
    Muestra una tabla de datos que contiene factores cuadráticos.

    Parámetros:
    - tabla: DataFrame de pandas que representa la tabla de datos.

    Excepciones:
    - Exception: Se lanza una excepción si el parámetro 'tabla' no es un DataFrame de pandas.

    Retorno:
    - None

    Ejemplo de uso:
    mostrarTablaFactoresCuadraticos(tabla)
    '''
    # validar el tipo de tabla
    validarTipo(tabla, pd.DataFrame)
    # mostrar la tabla
    display(tabla)

def mostrarMatriz(matriz:np.ndarray[float], nombre:str='M')->None:
    """
    Función: mostrarMatriz

    Descripción:
    Esta función se utiliza para mostrar una matriz en forma de tabla en la consola. La matriz se muestra con un nombre dado y se formatea de manera que los valores estén alineados correctamente.

    Parámetros:
    - matriz: una matriz representada como un array de numpy con valores de tipo float.
    - nombre: el nombre que se desea mostrar junto a la matriz. Por defecto es 'M'.

    Retorno:
    - None

    Ejemplo de uso:
    mostrarMatriz(np.array([[1.234, 2.345], [3.456, 4.567]]), 'Matriz A')
    """
    validarTipo(matriz, np.ndarray)
    validarTipo(nombre, str)
    n = len(matriz)
    mitad = n // 2
    len_nombre = len(nombre)
    espacio = ' ' * (len_nombre + 3)
    
    for (i, j), value in np.ndenumerate(matriz):
        validarTipo(value, (int, float))
        if i == mitad:
            print(nombre + ' = ', end='')
        else:
            print(espacio, end='')
        if value >= 0:
            print(' ', end='')
        print(f'{np.around(value, decimals = 3)}   ', end='\t')
        if j == n-1:
            print('')
    print('\n')

def mostrarVector(vector:np.ndarray[float], nombre:str='v')->None:
    '''
    Función: mostrarVector

    Descripción:
    Esta función se utiliza para mostrar un vector en forma de columna, con su respectivo nombre. Cada elemento del vector se redondea a 3 decimales y se valida que sea de tipo entero o flotante antes de imprimirlo.

    Parámetros:
    - vector: un arreglo de numpy que representa el vector a mostrar.
    - nombre: una cadena de texto que representa el nombre del vector. Por defecto es 'v'.

    Retorno:
    - None

    Ejemplo de uso:
    mostrarVector(np.array([1, 2, 3]), "Vector A")
    '''
    validarTipo(vector, np.ndarray)
    validarTipo(nombre, str)
    n = len(vector)
    mitad = n // 2
    len_nombre = len(nombre)
    espacio = ' ' * (len_nombre + 3)
    columna = np.around(vector, decimals = 3)
    for i in range(n):
        validarTipo(vector[i], (int, float))
        if i == mitad:
            print(nombre + ' = ', end='')
        else:
            print(espacio, end='')
        if vector[i] >= 0:
            print(' ', end='')
        print(f'{columna[i]}   ')
    print('\n')

def mostrarValoresCaracteristicos(valores:np.ndarray)->None:
    '''
    Función: mostrarValoresCaracteristicos

    Descripción:
    Esta función se utiliza para mostrar los valores característicos de una matriz.

    Parámetros:
    - valores: un arreglo de numpy que contiene los valores característicos de la matriz.

    Excepciones:
    - Exception: se lanza una excepción si el parámetro 'valores' no es un arreglo de numpy.

    Retorno:
    - None

    Ejemplo de uso:
    mostrarValoresCaracteristicos(np.array([1, 2, 3]))
    '''
    validarTipo(valores, np.ndarray)
    for i, valor in enumerate(valores, start=1):
        if isinstance(valor, np.complex):
            display(Math(f'λ_{i} = {np.round(valor.real, 3)}'))
        else:
            display(Math(f'λ_{i} = {np.round(valor.real, 3)}'))

def mostrarRaiz(r)->None:
    if len(r) == 1:
        display(Math('r = ' + sp.latex(r[0])))
    else:
        display(Math('r_1 = ' + sp.latex(r[0])))
        display(Math('r_2 = ' + sp.latex(r[1])))