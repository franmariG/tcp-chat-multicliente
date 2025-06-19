import customtkinter as ctk # Importa la biblioteca CustomTkinter para crear interfaces gráficas
from tkinter import scrolledtext  # Se importa el widget de texto con scroll
import socket # Importa el módulo socket para la programación de red
import threading # Importa el módulo threading para manejar tareas concurrentes (enviar y recibir mensajes al mismo tiempo)

# Parámetros de conexión del servidor
HOST = '127.0.0.1'   # Dirección local (localhost)
PORT = 12345         # Puerto del servidor

# Variables globales para el socket del cliente y estado de conexión
cliente_socket = None
conectado_global = False

# FUNCIONES PRINCIPALES

# Función que se ejecuta al presionar "Conectar", conecta al servidor e inicia el hilo receptor
def conectar_al_servidor():
    global cliente_socket, conectado_global
    nombre_usuario = entry_nombre.get().strip()  # Se obtiene el nombre del usuario
    if not nombre_usuario: # Verifica si el nombre de usuario está vacío
        actualizar_estado_conexion("Por favor, introduce tu nombre antes de conectar.", "warning")
        return

    try:
        # Crear el socket TCP del cliente (AF_INET para IPv4, SOCK_STREAM para TCP)
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((HOST, PORT)) # Establecer conexión con el servidor
        conectado_global = True
        actualizar_estado_conexion("Conectado al servidor.", "info")

        # Crea e inicia hilo para recibir mensajes
        hilo_recibir = threading.Thread(target=recibir_mensajes)
        hilo_recibir.daemon = True
        hilo_recibir.start()

        # Deshabilita campos de conexión y habilita los del chat
        btn_conectar.configure(state="disabled")
        entry_nombre.configure(state="disabled")
        entry_mensaje.configure(state="normal")
        btn_enviar.configure(state="normal")
        btn_salir.configure(state="normal")

        # Enviar mensaje de ingreso al chat
        cliente_socket.sendall(f"{nombre_usuario} ha entrado al chat.".encode())

    # Manejo de errores
    except ConnectionRefusedError:
        actualizar_estado_conexion("Error: El servidor no está disponible.", "error")
    except Exception as e:
        actualizar_estado_conexion(f"Error al conectar: {e}", "error")

# Hilo para recibir mensajes del servidor y mostrarlos en la interfaz
def recibir_mensajes():
    global conectado_global
    while conectado_global: # Mientras el cliente este conectado
        try:
            # Espera y recibe mensajes del servidor
            mensaje = cliente_socket.recv(1024).decode()
            if not mensaje:
                break  # Si no se recibe nada, se considera cerrada la conexión
            
            # Mostrar mensaje recibido en el área de chat
            chat_area.configure(state="normal")
            chat_area.insert(ctk.END, mensaje + "\n", "other_message")
            chat_area.yview(ctk.END)
            chat_area.configure(state="disabled")

            # Si el servidor envía un mensaje de cierre llama a la funcion de desconexión y informa al usuario
            if mensaje == "El servidor se ha cerrado.":
                desconectar()
                actualizar_estado_conexion("Conexión cerrada por el servidor.", "info")
                break
            
        # Manejo de errores
        except OSError as e:
            if conectado_global:
                actualizar_estado_conexion(f"Error de conexión: {e}", "error")
                desconectar()
            break
        except Exception as e:
            actualizar_estado_conexion(f"Error al recibir: {e}", "error")
            desconectar()
            break

# Envía el mensaje escrito al servidor
def enviar_mensaje():
    global conectado_global
    if not conectado_global: # Verifica si el cliente no está conectado
        actualizar_estado_conexion("No estás conectado al servidor.", "warning")
        return

    # Obtiene el nombre de usuario y el mensaje a enviar
    nombre_usuario = entry_nombre.get().strip()
    mensaje_a_enviar = entry_mensaje.get().strip()

    # Si el campo de mensaje está vacío no envía nada
    if not mensaje_a_enviar:
        return

    try:
        # Mostrar mensaje propio en el área de chat
        chat_area.configure(state="normal")
        chat_area.insert(ctk.END, f"Tú: {mensaje_a_enviar}\n", "self_message")
        chat_area.yview(ctk.END)
        chat_area.configure(state="disabled")

        # Envía el mensaje al servidor
        cliente_socket.sendall(f"{nombre_usuario}: {mensaje_a_enviar}".encode())
        entry_mensaje.delete(0, ctk.END)
    
    # Manejo de Errores
    except Exception as e:
        actualizar_estado_conexion(f"Error al enviar: {e}", "error")
        desconectar()

# Enviar mensaje de salida y cerrar la interfaz
def salir_del_chat():
    global conectado_global
    if conectado_global and cliente_socket: # Si el cliente está conectado.
        nombre_usuario = entry_nombre.get().strip()
        try:
            # Envia un mensaje al servidor informando que el usuario ha salido
            cliente_socket.sendall(f"{nombre_usuario} ha salido del chat.".encode())
        except Exception as e: # Manejo de errores
            print(f"Error al enviar mensaje de salida: {e}")
        finally:
            desconectar() # Llama a la función para cerrar la conexión del socket
            actualizar_estado_conexion("Has salido del chat.", "info") # Mensaje de salida
            # Retrasa el cierre de la ventana (0.7 s) para que el mensaje anterior sea visible
            app.after(700, lambda: app.quit())  # Cierra el bucle principal
            app.after(700, lambda: app.destroy()) # Destruye la ventana y libera recursos

# Cierra el socket y reinicia los controles
def desconectar():
    global conectado_global
    conectado_global = False # Establece la bandera de conexión a False
    if cliente_socket: # Si existe un socket de cliente
        try:
            cliente_socket.shutdown(socket.SHUT_RDWR) # Cierra la conexión de lectura y escritura del socket
            cliente_socket.close() # Cierra el socket completamente
        
        # Manejo de Errores
        except OSError as e:
            print(f"Error al cerrar socket: {e}")
        except Exception as e:
            print(f"Error inesperado al desconectar: {e}")

    # Restaura el estado de los botones y campos de entrada a su estado inicial (desconectado)
    btn_conectar.configure(state="normal")
    entry_nombre.configure(state="normal")
    entry_mensaje.configure(state="disabled")
    btn_enviar.configure(state="disabled")
    btn_salir.configure(state="disabled")

# Muestra un mensaje de estado (info, error, advertencia) en el área de chat
def actualizar_estado_conexion(mensaje, tipo="normal"):
    tag = "status_normal"
    if tipo == "info":
        tag = "status_info"
    elif tipo == "error":
        tag = "status_error"
    elif tipo == "warning":
        tag = "status_warning"

    chat_area.configure(state="normal") # Habilita el área de chat
    chat_area.insert(ctk.END, f"[Estado] {mensaje}\n", tag) # Inserta el mensaje de estado
    chat_area.yview(ctk.END) # Auto-desplaza el área
    chat_area.configure(state="disabled") # Deshabilita nuevamente

# CONFIGURACIÓN DE LA INTERFAZ

ctk.set_appearance_mode("Dark")  # Tema oscuro
ctk.set_default_color_theme("blue")  # Tema azul

app = ctk.CTk() # Ventana principal de la aplicación
app.title("Chat") # Título
app.geometry("500x650") # Tamaño inicial
app.resizable(True, True) # Permite redimensionamiento

FONT_SIZE = 15 # Tamaño de fuente

# Colores y estilos para los mensajes del área de chat
chat_area_tags = {
    "status_normal": {"foreground": "lightgray", "font": ("Arial", FONT_SIZE)},
    "status_info": {"foreground": "#6495ED", "font": ("Arial", FONT_SIZE)},
    "status_error": {"foreground": "#FF6347", "font": ("Arial", FONT_SIZE)},
    "status_warning": {"foreground": "#FFCC00", "font": ("Arial", FONT_SIZE)},
    "self_message": {"foreground": "#90EE90", "justify": "right", "font": ("Arial", FONT_SIZE)},
    "other_message": {"foreground": "white", "justify": "left", "font": ("Arial", FONT_SIZE)}
}

# DISEÑO DE LA VENTANA 

# Frame principal, contenedor principal para todos los widgets
main_frame = ctk.CTkFrame(app, corner_radius=10)
main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

# Configurar las columnas para que se expandan dentro del main_frame
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_rowconfigure(2, weight=1)

# Campo para ingresar nombre
lbl_nombre = ctk.CTkLabel(main_frame, text="Tu Nombre:")
lbl_nombre.grid(row=0, column=0, padx=5, pady=5, sticky=ctk.W)

entry_nombre = ctk.CTkEntry(main_frame, placeholder_text="Introduce tu nombre")
entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky=(ctk.W, ctk.E))
entry_nombre.focus_set()

# Botón para establecer la conexión
btn_conectar = ctk.CTkButton(main_frame, text="Conectar", command=conectar_al_servidor)
btn_conectar.grid(row=0, column=2, padx=5, pady=5, sticky=ctk.E)

# Área de mensajes con scroll (se uso tkinter porque CustomTkinter no tiene uno propio)
chat_area = scrolledtext.ScrolledText(main_frame, wrap=ctk.WORD, state="disabled", padx=10, pady=10,
                                       bg="#333333", fg="white", relief=ctk.FLAT, borderwidth=0,
                                       insertbackground="white")
chat_area.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=(ctk.N, ctk.S, ctk.E, ctk.W))

# Aplicar los estilos definidos a los tags
for tag, config in chat_area_tags.items():
    chat_area.tag_config(tag, **config)

# Campo de entrada para escribir mensajes
entry_mensaje = ctk.CTkEntry(main_frame, placeholder_text="Escribe tu mensaje...", state="disabled")
entry_mensaje.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=(ctk.W, ctk.E))
entry_mensaje.bind("<Return>", lambda event=None: enviar_mensaje())

# Botón para enviar mensajes
btn_enviar = ctk.CTkButton(main_frame, text="Enviar", command=enviar_mensaje, state="disabled")
btn_enviar.grid(row=3, column=2, padx=5, pady=5, sticky=ctk.E)

# Botón para salir del chat
btn_salir = ctk.CTkButton(main_frame, text="Salir del Chat", command=salir_del_chat, fg_color="red", hover_color="darkred", state="disabled")
btn_salir.grid(row=4, column=0, columnspan=3, pady=10)

# Cerrar la ventana correctamente al hacer clic en la "X"
def on_closing():
    if conectado_global: # Si el cliente está conectado.
        salir_del_chat() # Llama a salir_del_chat para una salida limpia
    else:
        app.quit()  # Cierra el bucle principal
        app.destroy() # Destruye la ventana y libera recursos

# Asocia on_closing con el protocolo de cierre de ventana
app.protocol("WM_DELETE_WINDOW", on_closing)

# Inicia el bucle principal de la interfaz gráfica
app.mainloop()
