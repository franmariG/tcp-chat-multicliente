import socket # Importa el módulo socket para la programación de red
import threading  # Importa el módulo threading para manejar tareas concurrentes (enviar y recibir mensajes al mismo tiempo)

# Dirección IP y puerto del servidor al que se conecta el cliente
HOST = '127.0.0.1'  # Dirección local (localhost)
PORT = 12345        # Puerto del servidor

# Crea el socket TCP del cliente (AF_INET para IPv4, SOCK_STREAM para TCP)
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    cliente.connect((HOST, PORT)) # Establecer conexión con el servidor
except ConnectionRefusedError:
    print("\n[!] No se pudo conectar al servidor. Asegúrate de que el servidor esté en ejecución.")
    exit()

# Variable para controlar el estado de la conexión
conectado = True

# FUNCIONES

# Función para recibir mensajes del servidor de forma continua
def recibir():
    global conectado
    while True:
        try:
            # Espera y recibe mensajes del servidor
            mensaje = cliente.recv(1024).decode()
            if not mensaje:
                break  # Si no se recibe nada, se considera cerrada la conexión

            print("\n" + mensaje)  # Mostrar el mensaje en la consola

            # Si el servidor envía este mensaje, se cierra la conexión
            if mensaje == "El servidor se ha cerrado.":
                conectado = False
                cliente.close()
                print("\nConexión cerrada por el servidor.")
                break
        except:
            # Si ocurre un error en la recepción, se cierra la conexión
            conectado = False
            cliente.close()
            break

# Función para enviar mensajes al servidor
def enviar():
    global conectado
    try:
        nombre = input("\nEscribe tu nombre: ")  # Solicita nombre del usuario
    except EOFError:
        print("\n[!] Entrada interrumpida. Cancelando conexión...")
        cliente.close()
        return
    cliente.sendall(f"\n{nombre} ha entrado al chat.".encode())  # Notifica ingreso

    while conectado: 
        try:
            mensaje = input("\nTu: ").strip() # Leer mensaje desde consola
        except EOFError:
            print("\n[!] Entrada interrumpida. Cerrando cliente...")
            cliente.close()
            conectado = False
            break
        if not conectado:
            break  # Evita seguir si el servidor se ha cerrado
        if not mensaje:
            continue  # No enviar mensajes vacíos

        if mensaje.lower() == "salir":
            # Si el usuario escribe "salir", se desconecta
            try:
                cliente.sendall(f"\n{nombre} ha salido del chat.".encode())
            except:
                pass  # Ignorar errores si el socket ya está cerrado
            cliente.close()
            conectado = False
            break

        try:
            # Enviar mensaje formateado con el nombre del usuario
            cliente.sendall(f"\n{nombre}: {mensaje}".encode())
        except:
            break  # Si falla el envío, termina el bucle

# HILOS DE EJECUCIÓN

# Crear el hilo que recibe mensajes
hilo_recibir = threading.Thread(target=recibir)

# Crear el hilo que envía mensajes
hilo_enviar = threading.Thread(target=enviar)

# Iniciar ambos hilos
hilo_recibir.start()
hilo_enviar.start()
