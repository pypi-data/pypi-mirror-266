import os
import random
import tk
# from tkinter import messagebox
from PIL import Image, ImageTk

# Ruta a la carpeta que contiene las imágenes
ruta_carpeta = "C:\\Users\\Dani\\OneDrive - Universidad de Oviedo\\imagenes\\dani\\"

# Lista de nombres de archivos en la carpeta
archivos = os.listdir(ruta_carpeta)

# Seleccionar una imagen aleatoria
imagen_seleccionada = random.choice(archivos)
ruta_imagen = os.path.join(ruta_carpeta, imagen_seleccionada)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Reconocimiento de Imágenes")

# Función para preguntar si se reconoce la imagen al cerrar la ventana
def cerrar_ventana():
    respuesta = messagebox.askyesno("Pregunta", "¿Reconoces esta imagen?")
    if respuesta:
        messagebox.showinfo("Respuesta", "¡Genial!")
    else:
        messagebox.showinfo("Respuesta", "¡Intenta de nuevo!")

# Cargar la imagen
imagen = Image.open(ruta_imagen)
imagen = imagen.resize((300, 300), Image.ANTIALIAS)  # Ajusta el tamaño de la imagen según sea necesario
imagen_tk = ImageTk.PhotoImage(imagen)

# Mostrar la imagen en una etiqueta
etiqueta_imagen = tk.Label(ventana, image=imagen_tk)
etiqueta_imagen.pack(padx=10, pady=10)

# Configurar la función de cierre de la ventana
ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)

# Iniciar el bucle principal de la interfaz gráfica
ventana.mainloop()