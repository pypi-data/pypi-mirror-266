# ------------------- Importar modulos -------------------
from metodos_numericos_dcb_fi.utilidades.configuracion import maxIteraciones, text
from metodos_numericos_dcb_fi.utilidades.leerEntrada import funcion
# ------------------- Importar bibliotecas -------------------
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from time import sleep
from IPython.display import clear_output
import sympy as sp
from sympy.abc import x

# ------------------- Funciones -------------------       
def graficarBiseccion(f:funcion, x_i:float, x_s:float, tolerancia:float, animacion:bool=True)->go.Figure:
    # Crear la figura
    fig = go.Figure()
    # Crear la curva de la función
    x = np.linspace(x_i-0.5, x_s+0.5, int(abs(x_s-x_i)*15))
    try:
        y = [f.f(i) for i in x]
    except:
        raise ValueError(f'{text["Errores"]["funcion_no_continua"].replace("{1}", x_i).replace("{2}", x_s)}')
    y_min = min(y)
    y_max = max(y)
    fig.add_trace(go.Scatter(x=x, y=y, name=f'f(x)={f.f_text}', mode='lines', line=dict(color='blue', width=2), showlegend=True))
    fig.update_layout(title=f'Método de bisección para f(x)={f.f_text}<br>x_i={round(x_i, 3)}, x_s={round(x_s,3)} y tolerancia={tolerancia}', xaxis_title='x', yaxis_title='f(x)', title_x=0.5)
    fig.show()
    # Aplicar el método de bisección y graficar
    i = 1
    while i <= maxIteraciones:
        x_m = (x_i + x_s)/2
        fig.add_trace(go.Scatter(x=[x_i, x_i], y=[y_min, y_max], mode='lines', line=dict(color='red', width=1, dash='dash'), showlegend=True, name=f'Limite inferior iteracion {i}: {round(x_i,2)}'))
        fig.add_trace(go.Scatter(x=[x_s, x_s], y=[y_min, y_max], mode='lines', line=dict(color='red', width=1, dash='dash'), showlegend=True, name=f'Limite superior iteracion {i}: {round(x_s,2)}'))
        if f.f(x_m) == 0: # si la raíz es exacta
            fig.add_trace(go.Scatter(x=[x_m], y=[0], mode='markers', marker=dict(color='red', size=10, symbol='diamond-open'), showlegend=True, name=f'Raíz exacta: {round(x_m,5)}'))
            break
        if abs(f.f(x_m)) < tolerancia: # si la raíz es aproximada
            fig.add_trace(go.Scatter(x=[x_m], y=[0], mode='markers', marker=dict(color='red', size=10, symbol='diamond-open'), showlegend=True, name=f'Raíz aproximada: {round(x_m,5)}'))
            break
        fig.add_trace(go.Scatter(x=[x_m], y=[0], mode='markers', marker=dict(color='red', size=5), showlegend=True, name=f'Raíz aproximada iteracion {i}: {round(x_m,2)}'))
        if animacion:
            sleep(1.5)
            clear_output(wait=True)
            fig.show()
        fig.data[-1].marker.color = 'orange'
        fig.data[-2].line.color = 'grey'
        fig.data[-3].line.color = 'grey'
        if f.f(x_i)*f.f(x_m) < 0:
            x_s = x_m
        else:
            x_i = x_m
        i += 1
    
    clear_output(wait=True)
    fig.show()
    return fig

def graficarNR(f:funcion, x_0:float, tolerancia:float, animacion:bool=True)->go.Figure:
    # Crear la figura
    fig = go.Figure()
    # Crear la curva de la función
    x_ = np.linspace(x_0-0.5, x_0+0.5, int(abs(x_0+1)*15))
    try:
        y = [f.f(i) for i in x_]
    except:
        raise ValueError(f'{text["Errores"]["funcion_no_continua_2"].replace("{1}", f.f_text)}')
    fig.add_trace(go.Scatter(x=x_, y=y, name=f'f(x)={f.f_text}', mode='lines', line=dict(color='blue', width=2), showlegend=True))
    fig.update_layout(title=f'Método de Newton-Raphson para f(x)={f.f_text}<br>x_0={round(x_0, 3)} y tolerancia={tolerancia}', xaxis_title='x', yaxis_title='f(x)', title_x=0.5)
    # Aplicar el método de Newton-Raphson y graficar
    i = 1
    df = sp.diff(f.f_text, x) # Derivar la función
    df = sp.lambdify(x, df, 'numpy')
    x_anterior = x_0
    fig.add_trace(go.Scatter(x=[x_anterior], y=[0], mode='markers', marker=dict(color='red', size=5), showlegend=True, name=f'x_0: {round(x_anterior,2)}'))
    fig.show()
    fig.data[-1].marker.color = 'orange'
    while i <= maxIteraciones:
        x_nueva = x_anterior - (f.f(x_anterior)/df(x_anterior))
        if x_nueva < x_.min():
            x_ = np.linspace(x_nueva-0.5, x_0+0.5, int(abs(x_0+1-x_nueva)*15))
            try:
                y = [f.f(i) for i in x_]
            except:
                raise ValueError(f'{text["Errores"]["funcion_no_continua_2"].replace("{1}", f.f_text)}')
            fig.data[0].x = tuple(x_)
            fig.data[0].y = tuple(y)
        if x_nueva > x_.max():
            x_ = np.linspace(x_0-0.5, x_nueva+0.5, int(abs(x_nueva+1-x_0)*15))
            try:
                y = [f.f(i) for i in x_]
            except:
                raise ValueError(f'{text["Errores"]["funcion_no_continua_2"].replace("{1}", f.f_text)}')
            fig.data[0].x = tuple(x_)
            fig.data[0].y = tuple(y)
        fig.add_trace(go.Scatter(x=[x_nueva, x_anterior], y=[0, f.f(x_anterior)], mode='lines', line=dict(color='red', width=1, dash='dash'), showlegend=True, name=f'df({round(x_anterior, 2)})'))
        fig.add_trace(go.Scatter(x=[x_anterior, x_anterior], y=[0,f.f(x_anterior)], mode='lines', line=dict(color='red', width=1, dash='dash'), showlegend=False))
        if abs(f.f(x_nueva)) == 0:
            fig.add_trace(go.Scatter(x=[x_nueva], y=[0], mode='markers', marker=dict(color='red', size=10, symbol='diamond-open'), showlegend=True, name=f'Raíz exacta: {round(x_nueva,5)}'))
            break
        if abs(f.f(x_nueva)) < tolerancia:
            fig.add_trace(go.Scatter(x=[x_nueva], y=[0], mode='markers', marker=dict(color='red', size=10, symbol='diamond-open'), showlegend=True, name=f'Raíz aproximada: {round(x_nueva,5)}'))
            break
        fig.add_trace(go.Scatter(x=[x_nueva], y=[0], mode='markers', marker=dict(color='red', size=5), showlegend=True, name=f'Raíz aproximada iteracion {i}: {round(x_nueva,2)}'))
        if animacion:
            sleep(1.5)
            clear_output(wait=True)
            fig.show()
        fig.data[-1].marker.color = 'orange'
        fig.data[-2].line.color = 'gray'
        fig.data[-3].line.color = 'gray'
        x_anterior = x_nueva
        i += 1

    clear_output(wait=True)
    fig.show()
    return fig
    
def graficarPolinomio(c:list[float]):
    grado = len(c) - 1
    p = np.poly1d(c)
    raices = p.r
    raicesReales = [raiz for raiz in raices if not isinstance(raiz, complex)]
    if len(raicesReales) == 0:
        x_min = -10
        x_max = 10
    else:
        x_min = min(raicesReales)
        x_max = max(raicesReales)
    x_ = np.linspace(x_min-0.5, x_max+0.5, int(abs(x_max-x_min+1)*15))
    y = [p(i) for i in x_]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_, y=y, name=f'p_{grado}(x)', mode='lines', line=dict(color='blue', width=2), showlegend=True))
    if len(c) < 4:
        for raiz in raicesReales:
            fig.add_trace(go.Scatter(x=[raiz], y=[0], mode='markers', marker=dict(color='red', size=10, symbol='diamond-open'), showlegend=True, name=f'Raíz: {round(raiz,5)}'))
    fig.show()
    return fig

def graficarTrapecio(f:funcion, a:float, b:float, integral:float, mostrar=True):
    titulo = f'Metodo del Trapecio<br>Para f(x) = {f.f_text} con intervalo [{a}, {b}]' # Titulo de la grafica
    eje_x = 'x' # Nombre del eje x
    eje_y = 'f(x)' # Nombre del eje y
    rango_x = np.linspace(a, b, int(abs(a-b))*25, dtype = 'float') # Rango en x
    funcion = [f.f(x) for x in rango_x] # Rango en y

    fig = go.Figure() # Crear figura
    trapecio = go.Scatter(x = [a, b], y = [f.f(a), f.f(b)], name=f'Trapecio<br>{round(integral,4)}', line=dict(dash = "dash", color='red', width=2), fill = 'tozeroy')
    fig.add_trace(go.Scatter(x = rango_x, y = funcion, name=f'f(x)', line=dict(color='blue', width=2))) # Graficar f(x)
    fig.add_trace(go.Scatter(x = rango_x, y = funcion, name=f'Analítico<br>{round(sp.integrate(f.f_, (x, a, b)), 4)}', line=dict(color='blue', width=2), fill = 'tozeroy')) # Graficar f(x)
    fig.add_trace(trapecio) # Graficar metodo
    fig.add_trace(go.Scatter(x = [a, b], y = [f.f(a), f.f(b)], mode='markers', name='Puntos trapecio', marker=dict(color='red', size=10)))
    fig.update_layout(title=titulo, title_x=0.5, xaxis_title=eje_x, yaxis_title=eje_y) # ¡¡¡NO MODIFICAR!!!
    if mostrar:
        fig.show() # ¡¡¡NO MODIFICAR!!!
    return fig

def graficarSimpson1_3(f:funcion, a:float, b:float, integral:float, mostrar=True):
    titulo = f'Metodo de Simpson 1/3<br>Para f(x) = {f.f_text} con intervalo [{a}, {b}]' # Titulo de la grafica
    eje_x = 'x' # Nombre del eje x
    eje_y = 'f(x)' # Nombre del eje y
    rango_x = np.linspace(a, b, int(abs(a-b))*25, dtype = 'float') # Rango en x
    funcion = [f.f(x) for x in rango_x] # Rango en y
    # obtener la funcion se la parabola que pasa por los puntos (a, f(a)), ((a+b)/2, f((a+b)/2)), (b, f(b))
    parabola = np.polyfit([a, (a+b)/2, b], [f.f(a), f.f((a+b)/2), f.f(b)], 2)
    parabola = np.poly1d(parabola)
    
    fig = go.Figure() # Crear figura
    simpson1_3 = go.Scatter(x = rango_x, y = [parabola(x) for x in rango_x], name=f'Simpson 1/3<br>{round(integral,4)}', line=dict(color='red', width=2, dash = "dash"), fill = 'tozeroy')
    fig.add_trace(go.Scatter(x = rango_x, y = funcion, name=f'f(x)', line=dict(color='blue', width=2))) # Graficar f(x)
    fig.add_trace(go.Scatter(x = rango_x, y = funcion, name=f'Analítico<br>{round(sp.integrate(f.f_, (x, a, b)), 4)}', line=dict(color='blue', width=2), fill = 'tozeroy')) # Graficar f(x)
    fig.add_trace(simpson1_3) # Graficar metodo
    # graficar solo los 3 puntos que se usaron para calcular la parabola
    fig.add_trace(go.Scatter(x = [a, (a+b)/2, b], y = [f.f(a), f.f((a+b)/2), f.f(b)], mode='markers', name='Puntos parabola', marker=dict(color='red', size=10)))
    fig.update_layout(title=titulo, title_x=0.5, xaxis_title=eje_x, yaxis_title=eje_y) # ¡¡¡NO MODIFICAR!!!
    if mostrar:
        fig.show() # ¡¡¡NO MODIFICAR!!!
    return fig

def graficarSimpson3_8(f:funcion, a:float, b:float, integral:float, mostrar=True):
    titulo = f'Metodo de Simpson 3/8<br>Para f(x) = {f.f_text} con intervalo [{a}, {b}]' # Titulo de la grafica
    eje_x = 'x' # Nombre del eje x
    eje_y = 'f(x)' # Nombre del eje y
    rango_x = np.linspace(a, b, int(abs(a-b))*25, dtype = 'float') # Rango en x
    funcion = [f.f(x) for x in rango_x] # Rango en y
    # obtener la funcion se la cubica que pasa por los puntos (a, f(a)), ((a+b)/2, f((a+b)/2)), (b, f(b))
    cubica = np.polyfit([a, (2*a+b)/3, (a+2*b)/3, b], [f.f(a), f.f((2*a+b)/3), f.f((a+2*b)/3), f.f(b)], 3)
    cubica = np.poly1d(cubica)
    
    fig = go.Figure() # Crear figura
    simpson3_8 = go.Scatter(x = rango_x, y = [cubica(x) for x in rango_x], name=f'Simpson 3/8<br>{round(integral,4)}', line=dict(color='red', width=2, dash = "dash"), fill = 'tozeroy')
    fig.add_trace(go.Scatter(x = rango_x, y = funcion, name=f'f(x)', line=dict(color='blue', width=2))) # Graficar f(x)
    fig.add_trace(go.Scatter(x = rango_x, y = funcion, name=f'Analítico<br>{round(sp.integrate(f.f_, (x, a, b)), 4)}', line=dict(color='blue', width=2), fill = 'tozeroy')) # Graficar f(x)
    fig.add_trace(simpson3_8) # Graficar metodo
    # graficar los 4 puntos que se usaron para calcular la cubica
    fig.add_trace(go.Scatter(x = [a, (2*a+b)/3, (a+2*b)/3, b], y = [f.f(a), f.f((2*a+b)/3), f.f((a+2*b)/3), f.f(b)], mode='markers', name='Puntos cúbica', marker=dict(color='red', size=10)))
    fig.update_layout(title=titulo, title_x=0.5, xaxis_title=eje_x, yaxis_title=eje_y) # ¡¡¡NO MODIFICAR!!!
    if mostrar:
        fig.show() # ¡¡¡NO MODIFICAR!!!
    return fig

def compararIntegracion(f:funcion, a:float, b:float, *graficas:go.Figure):
    titulo = f'Comparación de los métodos de integración: trapecio, Simpson 1/3 y Simpson 3/8<br>Para f(x) = {f.f_text} con intervalo [{a}, {b}]' # Titulo de la grafica
    eje_x = 'x' # Nombre del eje x
    eje_y = 'f(x)' # Nombre del eje y
    rango_x = np.linspace(a, b, int(abs(a-b))*25, dtype = 'float') # Rango en x
    funcion = [f.f(x) for x in rango_x] # Rango en y

    fig = go.Figure() # Crear figura
    fig.update_layout(title=titulo, title_x=0.5, xaxis_title=eje_x, yaxis_title=eje_y) # ¡¡¡NO MODIFICAR!!!
    fig.add_trace(go.Scatter(x = rango_x, y = funcion, name=f'f(x)', line=dict(color='blue', width=2))) # Graficar f(x)
    fig.add_trace(go.Scatter(x = rango_x, y = funcion, name=f'Analítico<br>{round(sp.integrate(f.f_, (x, a, b)), 4)}', line=dict(color='blue', width=2), fill = 'tozeroy')) # Graficar f(x)

    colores = ['red', 'green', 'orange']
    for g, color in zip(graficas, colores):
        grafica = g.data[2]
        puntos = g.data[3]
        grafica.line.color = color
        puntos.marker.color = color
        fig.add_trace(grafica)
        fig.add_trace(puntos)

    fig.show() # ¡¡¡NO MODIFICAR!!!

def graficar(valores:list,**configuracion:dict):
    if configuracion['titulo'] != None:
        titulo = configuracion['titulo']
    else:
        titulo = f'Grafica de f(x) con intervalo [{a}, {b}]'
    if configuracion['labels'] != None:
        eje_x = configuracion['labels'][0]
        eje_y = configuracion['labels'][1]
    else:
        eje_x = 'x'
        eje_y = 'f(x)'
    
    # Configuraciones predeterminadAs para graficar
    if configuracion['metodo'] == 'Euler':
        mode_ = 'makers'
        name_='Euler'
        markers = dict(size=8, symbol='diamond', color='lime')
        showlegend_=True
    elif configuracion['metodo'] == 'Euler M':
        mode_ = 'makers'
        name_='Euler modificado'
        markers = dict(size=8, symbol='triangle-up', color='darkviolet')
        showlegend_=True
    elif configuracion['metodo'] == 'RK4':
        mode_ = 'makers'
        name_='Runge-Kutta 4'
        markers = dict(size=8, symbol='triangle-down', color='hotpink')
        showlegend_=True
    elif configuracion['metodo'] == 'Analitica':
        mode_ = 'lines'
        name_ = 'Solución analítica'
        lines = dict(color='blue', width=2)
        showlegend_ = True
    
    fig = go.Figure() # Crear figura
    fig.update_layout(title=titulo, title_x=0.5, xaxis_title=eje_x, yaxis_title=eje_y)
    
    if mode_ == 'makers':
        fig.add_trace(go.Scatter(x=valores[0], y=valores[1], mode='markers', marker=markers, showlegend=showlegend_, name=name_))
    elif mode_ == 'lines':
        fig.add_trace(go.Scatter(x=valores[0], y=valores[1], mode='lines', line=lines, showlegend=showlegend_, name=name_))
    fig.show() # ¡¡¡NO MODIFICAR!!!
    return fig

def compararMetodos(titulo, *graficas, **configuracion):
    if configuracion['labels'] != None:
        eje_x = configuracion['labels'][0]
        eje_y = configuracion['labels'][1]
    else:
        eje_x = 'x'
        eje_y = 'f(x)'
    
    fig = go.Figure() # Crear figura
    fig.update_layout(title=titulo, title_x=0.5, title_y=0.9, xaxis_title=eje_x, yaxis_title=eje_y, legend_title='Métodos') # ¡¡¡NO MODIFICAR!!!

    for g in graficas:
        fig.add_trace(g)
    fig.show() # ¡¡¡NO MODIFICAR!!!
    return fig
