import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import threading
from inputimeout import inputimeout, TimeoutOccurred

# Función para reproducir una melodía
def reproducir_melodia(driver, melodia):
    for nota, duracion in melodia:
        tecla = driver.find_element(By.CSS_SELECTOR, f'div[data-note="{nota}"]')
        tecla.click()
        time.sleep(duracion)

# Función para cargar las canciones desde el archivo Excel
def cargar_canciones(archivo_excel):
    # Verificar el directorio actual de trabajo
    current_dir = os.getcwd()
    print(f"Directorio actual de trabajo: {current_dir}")

    # Verificar si el archivo existe en el directorio actual
    archivo_path = os.path.join(current_dir, archivo_excel)
    if not os.path.isfile(archivo_path):
        print(f"Archivo no encontrado: {archivo_path}")
        return []

    print(f"Cargando canciones desde el archivo: {archivo_path}")
    
    df = pd.read_excel(archivo_path)
    canciones = []
    for index, row in df.iterrows():
        nombre = row['Nombre']
        notas_str = row['Notas']
        notas = [(nota.split(',')[0], float(nota.split(',')[1])) for nota in notas_str.split(';')]
        canciones.append((nombre, notas))
    return canciones

# Función para mostrar el menú de selección de canciones
def seleccionar_cancion(canciones):
    print("Seleccione una canción:")
    for i, (nombre, _) in enumerate(canciones):
        print(f"{i + 1}. {nombre}")
    try:
        seleccion = inputimeout(prompt="Ingrese el número de la canción (o espere 5 segundos para comenzar automáticamente): ", timeout=5)
        return int(seleccion) - 1 if seleccion.isdigit() and 1 <= int(seleccion) <= len(canciones) else None
    except TimeoutOccurred:
        return None
    
# Función principal para ejecutar el programa
def tocar_piano():
    # Cargar canciones desde el archivo Excel
    archivo_excel = 'canciones.xlsx'
    canciones = cargar_canciones(archivo_excel)

    # Verificar si se cargaron canciones
    if not canciones:
        print("No se pudieron cargar las canciones. Verifique el archivo y su ubicación.")
        return

    # Inicializar el driver de Selenium
    driver = webdriver.Chrome()

    # Acceder a la página del piano
    driver.get('https://piano2024.vercel.app/')

    # Función para manejar la selección de canción con temporizador
    def manejar_seleccion():
        seleccion = seleccionar_cancion(canciones)
        if seleccion is None:
            seleccion = 0
        for i in range(seleccion, len(canciones)):
            nombre, melodia = canciones[i]
            print(f"Reproduciendo: {nombre}")
            reproducir_melodia(driver, melodia)
        driver.quit()

    # Crear y ejecutar el hilo con temporizador de 5 segundos
    hilo = threading.Thread(target=manejar_seleccion)
    hilo.daemon = True
    hilo.start()
    hilo.join(5)

    # Verificar si el hilo sigue activo (significa que no se seleccionó ninguna canción)
    if hilo.is_alive():
        print("No se seleccionó ninguna canción en 5 segundos. Reproduciendo la primera canción.")
        hilo.join()

    # Capturar y mostrar mensajes de la consola del navegador
    console_logs = driver.execute_script("return console.logs")
    for log in console_logs:
        print(log)

# Llamar a la función principal para tocar el piano
tocar_piano()