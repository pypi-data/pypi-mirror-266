#Biblioteca: ModBububugti.py
import os

# Función para mostrar una imagen de error según el tipo de error
def shimgerr(typeerr):
    # Ruta de la imagen de error
    img = f"{typeerr}.png"

    # Verificar si el archivo de imagen existe
    if os.path.exists(img):
        # Abrir la imagen con el visor de imágenes predeterminado del sistema
        os.system(img)
    else:
        print("No se pudo encontrar la imagen de error correspondiente.")

# Función para mostrar un mensaje de error personalizado según el tipo de error
def sherr(typeerr):
    if typeerr == "TypeError": 
        print("Se ha producido un TypeError.")
    elif typeerr == "ValueError": 
        print("Se ha producido un ValueError.")
    elif typeerr == "ZeroDivisionError": 
        print("Se ha producido un ZeroDivisionError.")
    elif typeerr == "IndexError": 
        print("Se ha producido un IndexError.")
    elif typeerr == "KeyError": 
        print("Se ha producido un KeyError.")
    elif typeerr == "FileNotFoundError": 
        print("Se ha producido un FileNotFoundError.") 
    else:
        print("Se ha producido un error desconocido.")
    # Mostrar la imagen de error correspondiente
    shimgerr(typeerr)
