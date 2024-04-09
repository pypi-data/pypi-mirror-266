# ------------------- Importar bibliotecas -------------------
from pathlib import Path
import json
import string

# -------------------  Definir constantes -------------------
colores = ['blue', 'red', 'green', 'orange', 'purple', 'magenta', 'yellow', 'black']
letras_latinas = list(string.ascii_letters)
letras_griegas = [chr(i) for i in range(0x3b1, 0x3ca)] + [chr(i) for i in range(0x3ca, 0x3d6)] + [chr(i) for i in range(0x391, 0x3a2)] + [chr(i) for i in range(0x3a3, 0x3aa)] + [chr(i) for i in range(0x3aa, 0x3b1)]
maxIteraciones = 20
idioma = 'es'
text = {}

# -------------------  Definir funciones -------------------
def leerTextos()->None:
    """
    Lee el archivo de texto correspondiente al idioma especificado y carga su contenido en la variable global 'text'.

    Parámetros:
        No recibe ningún parámetro.

    Excepciones:
        FileNotFoundError: Si no se encuentra el archivo de texto correspondiente al idioma especificado.
        json.JSONDecodeError: Si ocurre un error al decodificar el archivo de texto.

    Retorno:
        No retorna ningún valor.

    Ejemplo:
        leer_textos()
    """
    current_dir = Path(__file__).resolve().parent
    text_file = current_dir / '..' / 'data' / f'text_{idioma}.json'
    global text
    try:
        with open(text_file, 'r', encoding='utf-8') as file:
            text = json.load(file)
    except FileNotFoundError:
        raise Exception(f'No se puede leer el archivo text_{idioma}.json\nCan\'t read the file text_{idioma}.json')
    except json.JSONDecodeError:
        raise Exception(f'Error al decodificar el archivo text_{idioma}.json\nFailed to decode the file text_{idioma}.json')

def cambiarIdioma(nuevo_idioma:str)->None:
    '''
    Cambia el idioma actual del programa al idioma especificado.

    Parámetros:
        nuevo_idioma (str): El nuevo idioma al que se desea cambiar. Debe ser uno de los idiomas disponibles.

    Excepciones:
        Exception: Si el nuevo idioma no está en la lista de idiomas disponibles [es].

    Retorno:
        No retorna ningún valor.

    Ejemplo:
        cambiar_idioma('es')
    '''
    nuevo_idioma = nuevo_idioma.lower()
    idiomas_disponibles = ['es']
    if nuevo_idioma in idiomas_disponibles:
        global idioma
        idioma = nuevo_idioma
        leerTextos()
    else:
        raise Exception(f'{text["Utilidades"]["Errores"]["idioma"].replace("{1}", ", ".join(idiomas_disponibles)).replace("{2}", nuevo_idioma)}')
    
def cambiarMaxIteraciones(nuevo_max_iteraciones:int)->None:
    '''
    Cambia el número máximo de iteraciones permitidas en el programa.

    Parámetros:
        nuevo_max_iteraciones (int): El nuevo número máximo de iteraciones permitidas.

    Excepciones:
        ValueError: Si el nuevo número máximo de iteraciones no es un entero positivo.

    Retorno:
        No retorna ningún valor.

    Ejemplo:
        cambiar_max_iteraciones(30)
    '''
    if not isinstance(nuevo_max_iteraciones, int):
        raise Exception(f'{text["Utilidades"]["Errores"]["tipo_entrada"].replace("{1}", "int").replace("{2}", type(nuevo_max_iteraciones))}')
    if nuevo_max_iteraciones < 1 or nuevo_max_iteraciones > 70:
        raise Exception(f'{text["Utilidades"]["Errores"]["max_iteraciones"].replace("{1}", str(nuevo_max_iteraciones))}')
    global maxIteraciones
    maxIteraciones = nuevo_max_iteraciones
