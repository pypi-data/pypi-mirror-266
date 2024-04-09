# ------------------- Importar módulos -------------------
from metodos_numericos_dcb_fi.utilidades.configuracion import text
from metodos_numericos_dcb_fi.utilidades.validacion import validarTipo
from metodos_numericos_dcb_fi.utilidades.configuracion import letras_griegas, letras_latinas

# ------------------- Importar bibliotecas -------------------
import sympy as sp
from sympy.abc import x
import numpy as np

# ------------------- Crear la clase funcion -------------------
class funcion:
    """
    Clase 'funcion'

    Esta clase representa una función matemática. Permite almacenar los valores de x e y de la función, así como también realizar operaciones y cálculos relacionados con la función.

    Atributos:
    - valores_x (list): Lista que almacena los valores de x de la función.
    - valores_y (list): Lista que almacena los valores de y de la función.
    - f_text (str): Texto de la función.
    - f (function): Función simbólica de sympy.
    - f_ (function): Función lambda de numpy.
    """
    def __init__(self) -> None:
        """
    Inicializa una instancia de la clase 'funcion'.

    Parámetros:
    - metodo (str): El método para el cual se va a utilizar la función.

    Atributos:
    - valores_x (list): Lista que almacena los valores de x de la función.
    - valores_y (list): Lista que almacena los valores de y de la función.
    - f_text (str): Texto de la función.
    - f (function): Función simbólica de sympy.
    - f_ (function): Función lambda de numpy.
    """ 
        self.valores_x = []
        self.valores_y = []
        self.limites = []
        self.f_text = None # Texto
        self.f = None # Lambdify
        self.f_ = None # Sympify
    
    def setFuncion(self, f:str, var:str='x'):
        '''
    Establece la función de la instancia actual con la función especificada.

    Parámetros:
        - f (str): La función matemática especificada como una cadena de texto.

    Excepciones:
        - Exception: Si ocurre un error al establecer la función.

    Retorno:
        - None

    Ejemplo:
        setFuncion("x**2 + 3*x - 2")
    '''
        validarTipo(f, str)
        f = f.replace('^', '**').replace('sen', 'sin').replace('tg', 'tan').replace('ctg', 'cot')
        self.f_text = f
        try:
            self.f_ = sp.sympify(self.f_text)
        except:
            raise Exception(f'{text["Utilidades"]["Errores"]["funcion"].replace("{1}", self.f_text)}')
        for _ in var:
            if _ not in letras_latinas and _ not in letras_griegas:
                raise Exception(f'{text["Utilidades"]["Errores"]["variable"].replace("{1}", _)}')
        self.f = sp.lambdify(var, self.f_, 'numpy')

    def agregarLimites(self, x_i:float, x_f:float):
        validarTipo(x_i, (int, float))
        validarTipo(x_f, (int, float))
        self.limites = [(x_i, x_f)]
# ------------------- Funciones -------------------
def convertirFuncion(f:str, var:str='x')->funcion:
    '''
    Convierte una función matemática especificada como una cadena de texto en una instancia de la clase 'funcion'.

    Parámetros:
        f (str): La función matemática especificada como una cadena de texto.
        var (str): La variable de la función. Por defecto es 'x'.

    Excepciones:
        No se generan excepciones.

    Retorno:
        Una instancia de la clase 'funcion' con la función especificada.

    Ejemplo:
        f = convertirFuncion("x**2 + 3*x - 2")
    '''
    f_ = funcion()
    f_.setFuncion(f, var)
    return f_

def leerFuncion()->funcion:
    '''
    Lee una función matemática ingresada por el usuario y la asigna a una instancia de la clase 'funcion'.

    Parámetros:
        f (str): la funcion en forma de scadena que se va a asignar a la instancia de la clase 'funcion'. Por defecto es una cadena vacía.

    Excepciones:
        No se generan excepciones.

    Retorno:
        Una instancia de la clase 'funcion' con la función asignada.

    Ejemplo:
        f = leerFuncion()
    '''
    f_ = funcion()
    print(text["Utilidades"]["Entrada"]["funcion_1"])
    f = input(f'{text["Utilidades"]["Entrada"]["funcion_2"]}')
    f_.setFuncion(f)
    return f_
    
def leerTolerancia(t:str='')->float:
    '''
    Lee la tolerancia ingresada por el usuario y la devuelve como un número de punto flotante.

    Parámetros:
        No recibe ningún parámetro.

    Excepciones:
        ValueError: Si la tolerancia ingresada es menor o igual a cero.

    Retorno:
        float: La tolerancia ingresada por el usuario.

    Ejemplo:
        leerTolerancia()
    '''
    if t != '':
        return float(t)
    print(text["Utilidades"]["Entrada"]["tolerancia_1"])
    tol = float(input(f'{text["Utilidades"]["Entrada"]["tolerancia_2"]}'))
    if tol <= 0:
        raise ValueError(f'{text["Utilidades"]["Errores"]["tolerancia"].replace("{1}", tol)}')
    return tol

def leerPolinomio(c:list=[]):
    '''
    Función: leerPolinomio

    Descripción:
    Esta función se utiliza para leer un polinomio desde la entrada estándar. Solicita al usuario el grado del polinomio y los coeficientes correspondientes, validando que los valores ingresados sean del tipo correcto.

    Parámetros:
        No recibe ningún parámetro.

    Excepciones:
        ValueError: se lanza una excepción si el grado del polinomio es menor o igual a cero.
        Exception: se lanza una excepción si ocurre un error al validar el tipo de los valores ingresados.

    Retorno:
        Una lista de coeficientes del polinomio.

    Ejemplo de uso:
        leerPolinomio()
    '''
    if len(c) > 0:
        return c
    print(text["Utilidades"]["Entrada"]["polinomio_1"])
    grado = int(input(f'{text["Utilidades"]["Entrada"]["polinomio_2"]}'))
    if grado <= 0:
        raise ValueError(f'{text["Utilidades"]["Errores"]["grado_polinomio"].replace("{1}", grado)}')
    coeficientes = []
    contador = 0
    for i in range(grado + 1):
        coeficiente = float(input(f'{text["Utilidades"]["Entrada"]["coeficiente"].replace("{1}", str(grado-i))}'))
        if i == contador and coeficiente == 0:
            contador += 1
        else:
            coeficientes.append(coeficiente)
    if len(coeficientes) < 2:
        raise ValueError(text["Utilidades"]["Errores"]["grado_final_polinomio"])
    return coeficientes

def leerMatriznxn()->np.array:
    """
    Lee una matriz cuadrada de tamaño nxn y la devuelve como un array de numpy.

    Parámetros:
        No recibe ningún parámetro.

    Excepciones:
        ValueError: Si el valor de n es menor o igual a cero.
        Exception: Si ocurre un error al validar el tipo de los valores ingresados.

    Retorno:
        np.array: La matriz cuadrada de tamaño nxn.

    Ejemplo:
        matriz = leerMatriznxn()
    """
    print(text["Utilidades"]["Entrada"]["matriz_nxn_1"])
    n = input(f'{text["Utilidades"]["Entrada"]["matriz_nxn_2"]}')
    validarTipo(n, int)
    if n <= 0:
        raise ValueError(f'{text["Utilidades"]["Errores"]["matriz_nxn"].replace("{1}", n)}')
    matriz = []
    for i in range(n):
        fila = []
        for j in range(n):
            elemento = input(f'{text["Utilidades"]["Entrada"]["matriz_nxn_3"].replace("{1}", i+1).replace("{2}", j+1)}')
            validarTipo(elemento, (int, float))
            fila.append(elemento)
        matriz.append(fila)
    return np.array(matriz)

def leerVector(n:int, reglas:str='')->np.array:
    """
    Lee un vector de números ingresados por el usuario.

    Parámetros:
    - n: int, la longitud del vector.
    - reglas: str opcional, reglas adicionales para ingresar los elementos del vector.

    Excepciones:
    - Exception: Si ocurre un error al validar el tipo de los valores ingresados.

    Retorno:
    - np.array, un arreglo numpy que contiene los elementos ingresados por el usuario.

    Ejemplo de uso:
    leerVector(5, 'Ingrese números enteros o decimales: ')
    """
    print(f'{text["Utilidades"]["Entrada"]["vector_1"]}{reglas}')
    vector = []
    for i in range(n):
        elemento = input(f'{text["Utilidades"]["Entrada"]["vector_2"].replace("{1}", i+1)}')
        validarTipo(elemento, (int, float))
        vector.append(elemento)
    return np.array(vector)

def leerVectorKrilov(n:int)->np.array:
    """
    Función: leerVectorKrilov

    Descripción:
    Esta función se utiliza para leer un vector de números ingresados por el usuario para el metodo de Krilov.

    Parámetros:
    - n: int, la longitud del vector.

    Excepciones:
    - Exception: Si ocurre un error al validar el tipo de los valores ingresados.

    Retorno:
    - np.array, un arreglo numpy que contiene los elementos ingresados por el usuario.

    Ejemplo de uso:
    leerVectorKrilov(5)
    """
    print(text["Utilidades"]["Entrada"]["vector_K_1"])
    opcion = input(f'{text["Utilidades"]["Entrada"]["opcion"]}')
    if opcion == '0':
        vector = np.zeros(n) # Vector de ceros de tamaño n
        vector[0] = 1 # Primer elemento igual a 1
    else:
        vector = leerVector(n, text["Utilidades"]["Entrada"]["vector_K_2"])
        # si todos los elementos son cero
        if np.all(vector == 0):
            print(text["Utilidades"]["Errores"]["vector_K"])
            vector = leerVectorKrilov(n)
    return vector

def leerDatosLU()->tuple[np.array, np.array]:
    '''
    Lee los datos necesarios para realizar la factorización LU de una matriz y su vector de términos independientes.

    Parámetros:
        No recibe ningún parámetro.

    Excepciones:
        ValueError: Si el valor de n es menor o igual a cero.
        Exception: Si ocurre un error al validar el tipo de los valores ingresados.

    Retorno:
        tuple: Una tupla que contiene la matriz y el vector ingresados por el usuario.

    Ejemplo:
        matriz, vector = leerDatosLU()
    '''
    print(text["Utilidades"]["Entrada"]["LU_1"])
    matriz = leerMatriznxn()
    print(text["Utilidades"]["Entrada"]["LU_2"])
    vector = leerVector(len(matriz))
    return matriz, vector
