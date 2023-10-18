from bs4 import BeautifulSoup
from tabulate import tabulate
import sqlite3

# Tu HTML
html = 'https://www.tutiempo.net/clima/ws-84100.html'

# Parsear el HTML
soup = BeautifulSoup(html, 'html.parser')

# Encontrar la primera tabla
tabla_clima = soup.find('table', class_='medias')

# Inicializar un diccionario para almacenar los datos
datos_clima = {}

# Iterar sobre las filas de la tabla
for fila in tabla_clima.find_all('tr'):
    celdas = fila.find_all('td')
    if len(celdas) > 1:
        # Obtener el año
        anno = celdas[0].text.strip()

        # Inicializar un diccionario para este año si no existe
        if anno not in datos_clima:
            datos_clima[anno] = {}

        # Mapear las abreviaturas a los nombres completos de las categorías de temperatura
        categorias = {
            'T': 'Temperatura media anual',
            'TM': 'Temperatura máxima media anual',
            'Tm': 'Temperatura mínima media anual',
            'PP': 'Precipitación total anual de lluvia y/o nieve derretida (mm)',
            'V': 'Velocidad media anual del viento (Km/h)',
            'RA': 'Total días con lluvia durante el año',
            'SN': 'Total días que nevó durante el año',
            'TS': 'Total días con tormenta durante el año',
            'FG': 'Total días con niebla durante el año',
            'TN': 'Total días con tornados o nubes de embudo durante el año',
            'GR': 'Total días con granizo durante el año'
        }

        # Inicializar una lista para esta fila
        fila_datos = [anno]

        # Iterar sobre las categorías de temperatura y agregar los datos a la lista
        for abreviatura in categorias.keys():
            fila_datos.append(celdas[categorias.keys().index(abreviatura) + 1].text.strip())

        # Agregar la fila de datos al diccionario
        datos_clima[anno] = fila_datos

# Conexión a la base de datos (se crea si no existe)
conn = sqlite3.connect('clima.db')

# Crear una tabla para almacenar los datos
conn.execute('''
    CREATE TABLE IF NOT EXISTS datos_clima (
        anno TEXT PRIMARY KEY,
        T REAL,
        TM REAL,
        Tm REAL,
        PP REAL,
        V REAL,
        RA REAL,
        SN REAL,
        TS REAL,
        FG REAL,
        TN REAL,
        GR REAL
    )
''')

# Iterar sobre los datos y guardarlos en la base de datos
for anno, datos in datos_clima.items():
    conn.execute('''
        INSERT OR REPLACE INTO datos_clima (
            anno, T, TM, Tm, PP, V, RA, SN, TS, FG, TN, GR
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (anno, *map(float, datos[1:])))

# Guardar los cambios
conn.commit()

# Cerrar la conexión
conn.close()

# Funciones adicionales

def consultar_temperaturas():
    while True:
        anno = input("Ingresa el año para consultar temperaturas (o 'q' para salir): ")

        if anno == 'q':
            print("¡Hasta luego!")
            break

        if anno in datos_clima:
            print(f"\nTemperaturas para el año {anno}:\n")
            for categoria, valor in datos_clima[anno].items():
                print(f"{categoria}: {valor}")
        else:
            print("El año ingresado no se encuentra en nuestra Base de datos. Por favor intente de vuelta.")

def comparar_temperaturas():
    if 'TM' in categorias.values() and 'Tm' in categorias.values():
        maxima_anno = minima_anno = None
        maxima_valor = float('-inf')
        minima_valor = float('inf')
        for anno, datos in datos_clima.items():
            if 'Temperatura máxima media anual' in datos and 'Temperatura mínima media anual' in datos:
                tm = float(datos['Temperatura máxima media anual'].replace(' °C', ''))
                tm_anno = anno
                tm_categoria = 'Temperatura máxima media anual'

                tm = float(datos['Temperatura máxima media anual'].replace(' °C', ''))
                tm_anno = anno
                tm_categoria = 'Temperatura máxima media anual'

                if tm > maxima_valor:
                    maxima_valor = tm
                    maxima_anno = tm_anno

                if tm < minima_valor:
                    minima_valor = tm
                    minima_anno = tm_anno

        print(f'La temperatura máxima media anual más alta ({maxima_valor}°C) se registró en el año {maxima_anno}.')
        print(f'La temperatura mínima media anual más baja ({minima_valor}°C) se registró en el año {minima_anno}.')
    else:
        print('No se encontraron datos de Temperatura máxima media anual (TM) o Temperatura mínima media anual (Tm).')


def mostrar_datos_tabla():
    # Conexión a la base de datos
    conn = sqlite3.connect('clima.db')

    # Obtener todos los datos de la base de datos
    cursor = conn.execute('SELECT * FROM datos_clima')

    # Obtener los nombres de las columnas (categorías de temperatura)
    columnas = [d[0] for d in cursor.description]

    # Obtener los datos
    filas = cursor.fetchall()

    # Cerrar la conexión
    conn.close()

    # Convertir los datos en un formato adecuado para tabulate
    datos_formato_tabla = []
    for fila in filas:
        datos_formato_tabla.append(list(fila))

    # Mostrar la tabla
    print(tabulate(datos_formato_tabla, headers=columnas, tablefmt="fancy_grid"))

def menu():
    while True:
        print("\n--- Menú ---")
        print("1. Mostrar datos en forma de tabla")
        print("2. Consultar temperaturas por año")
        print("3. Comparar temperaturas")
        print("4. Salir")

        opcion = input("Ingrese el número de la opción que desea ejecutar: ")

        if opcion == '1':
            mostrar_datos_tabla()
        elif opcion == '2':
            consultar_temperaturas()
        elif opcion == '3':
            comparar_temperaturas()
        elif opcion == '4':
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Por favor intente de nuevo.")

# Llamar a la función del menú
menu()






