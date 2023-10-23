import requests
from bs4 import BeautifulSoup
import csv
import time
import schedule
from datetime import datetime
from tabulate import tabulate
import mysql.connector
from mysql.connector import errorcode

# Define la hora en la que se desea detener la ejecución 
hora_detener = "22:00"

# Lista de URLs a scrapear
urls = ['https://www.meteored.com.ar/tiempo-en_Santa+Fe-America+Sur-Argentina-Santa+Fe-SAAV-1-16934.html',
    'https://www.meteored.com.ar/tiempo-en_Cordoba-America+Sur-Argentina-Cordoba-SACO-1-13585.html',
    'https://www.meteored.com.ar/tiempo-en_Buenos+Aires-America+Sur-Argentina-Ciudad+Autonoma+de+Buenos+Aires-SABE-1-13584.html',
    'https://www.meteored.com.ar/tiempo-en_Viedma-America+Sur-Argentina-Rio+Negro-SAVV-1-16866.html',
    'https://www.meteored.com.ar/tiempo-en_Mendoza-America+Sur-Argentina-Mendoza-SAME-1-16887.html',
    'https://www.meteored.com.ar/tiempo-en_Salta-America+Sur-Argentina-Salta-SASA-1-16932.html',
    'https://www.meteored.com.ar/tiempo-en_Ushuaia-America+Sur-Argentina-Tierra+del+Fuego-SAWH-1-16858.html',
    'https://www.meteored.com.ar/tiempo-en_Neuquen-America+Sur-Argentina-Neuquen--1-16888.html'
]
#  función para realizar el scraping
def mostrar_datos_simple():
    
    # Archivo CSV para almacenar los datos
    with open('datos8.csv', 'w', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv, delimiter=',')  
        escritor_csv.writerow(['Provincia', 'Día','Hora', 'Fecha', 'Temperatura Máxima', 'Temperatura Mínima'])  # Columnas

        # Realiza el raspado de datos
        for url in urls:
            # Realiza una solicitud HTTP para obtener la página web
            response = requests.get(url)

            # Analiza el contenido HTML de la página web con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Encuentra elementos en la página web y extrae información
            box = soup.find('div', class_='flex-w')

            provincia = soup.find('h1').get_text()
            dia = box.find('span', class_='day').get_text()
            hora = box.find('span', class_='hour').get_text()
            fecha = box.find('span', class_='subtitle-m').get_text()
            temMax = box.find('span', class_='max changeUnitT').get_text()
            temMin = box.find('span', class_='min changeUnitT').get_text()

            # Escribe los datos en el archivo CSV
            escritor_csv.writerow([provincia, dia, hora, fecha, temMax, temMin])


#------------Código para convertir CSV a BDD--------------------
# Configura la conexión a la base de datos
config = {
    'user': 'admin',
    'password': 'admin',
    'host': 'loca_host',
    'database': 'datos_temperaturas',
    'raise_on_warnings': True,
}

# Intenta conectarte a la base de datos
try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # Leer el archivo CSV e insertar los datos en la base de datos
    with open('datos8.csv', 'r', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        next(lector_csv)  # Saltar la primera fila si contiene encabezados

        for fila in lector_csv:
            # Suponiendo que tu tabla en MySQL tiene las mismas columnas en el mismo orden
            cursor.execute("INSERT INTO tu_tabla (provincia, dia, hora, fecha, temp_max, temp_min) VALUES (%s, %s, %s, %s, %s, %s)", (fila[0], fila[1], fila[2], fila[3], fila[4], fila[5]))

    # Confirmar cambios y cerrar la conexión
    cnx.commit()
    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Error: Acceso denegado, verifica tus credenciales.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Error: La base de datos no existe.")
    else:
        print(err)
#------------Código para convertir CSV a BDD--------------------



def mostrar_datos_plano():
    with open('datos8.csv', 'r', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        for fila in lector_csv:
            print(fila)

def mostrar_datos_en_tabla():
    # Lee y muestra los datos almacenados en el archivo CSV
    with open('datos8.csv', 'r', encoding='utf-8') as archivo_csv:
        lector_csv = csv.reader(archivo_csv)
        data = [fila for fila in lector_csv]

    # Divide los datos en encabezados y filas
    encabezados = data[0]
    filas = data[1:]

    # Muestra los datos utilizando tabulate
    print(tabulate(filas, headers=encabezados, tablefmt='grid'))


# Función para el submenú de visualización de datos
def submenu_visualizacion():
    print("\nVisualización de Temperaturas:")
    print("1. En formato de tabla")
    print("2. En texto plano")
    eleccion = input("Ingresa el número correspondiente a tu elección: ")
    if eleccion == '1':
        mostrar_datos_en_tabla()
    elif eleccion == '2':
        mostrar_datos_plano()

# Función para el menú principal
def menu_principal():
    print("\nTEMPERATURAS DE LAS PROVINCIAS MÁS GRANDES DE ARGENTINA")
    while True:
        print("\nMenú Principal:")
        print("1. Ver datos de las temperaturas")
        print("2. Consultar temperatura máxima")
        print("3. Consultar temperatura mínima")        

        eleccion = input("Ingresa el número correspondiente a tu elección: ")

        if eleccion == '1':
            submenu_visualizacion()
        elif eleccion == '2':
            # Agrega aquí la funcionalidad para consultar temperatura máxima
            pass
        elif eleccion == '3':
            # Agrega aquí la funcionalidad para consultar temperatura mínima
            pass
        else:
            print("Opción no válida. Por favor, ingresa un número del 1 al 3.")



# Programa la ejecución cada hora
schedule.every(1).hour.do(mostrar_datos_simple)

# Ejecuta el programa hasta que se alcance la hora de detener
while True:
    hora_actual = datetime.now().strftime("%H:%M")
    if hora_actual >= hora_detener:
        break  
    schedule.run_pending()
    time.sleep(1)  # Esperar 1 segundo entre verificaciones
    menu_principal()

    






