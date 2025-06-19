import socket # Importa el módulo socket para la programación de red
import threading # Importa el módulo threading para manejar múltiples clientes concurrentemente

# Dirección y puerto del servidor
HOST = '0.0.0.0'  # Escucha en todas las interfaces de red disponibles
PORT = 12345      # Puerto por donde se aceptarán las conexiones

clientes = []  # Lista para almacenar los sockets de clientes conectados

# Función para manejar la comunicación con un cliente
def manejar_cliente(cliente_socket, direccion):
    print(f"[+] Nueva conexión desde {direccion}")  # Mensaje de log al recibir una conexión
    try:
        while True:
            mensaje = cliente_socket.recv(1024)  # Espera a recibir un mensaje (hasta 1024 bytes)
            if not mensaje:
                break  # Si no se recibe nada, el cliente se desconectó
                
            # Reenvia el mensaje a todos los demás clientes conectados
            for c in clientes:
                if c != cliente_socket:
                    c.sendall(mensaje)
    except Exception as e:
        # Ignora los errores comunes de desconexión en Windows (10054, 10053)
        if "10054" not in str(e) and "10053" not in str(e):
            print(f"[!] Error en cliente {direccion}: {e}")
    finally:
        # Cuando el cliente se desconecta o ocurre un error, se elimina y se cierra su socket
        print(f"[-] Conexión cerrada con {direccion}")
        clientes.remove(cliente_socket)
        cliente_socket.close()

# CONFIGURACIÓN DEL SERVIDOR 

# Crea el socket del servidor TCP (AF_INET para IPv4, SOCK_STREAM para TCP)
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Permite reutilizar la dirección en caso de reinicio rápido del servidor
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Asocia el socket a la dirección IP y puerto especificados
servidor.bind((HOST, PORT))

# Inicia el modo escucha para aceptar conexiones entrantes
servidor.listen()

# Establece un timeout para que el servidor no se bloquee al aceptar conexiones
# Esto permite que KeyboardInterrupt (Ctrl+C) sea capturado y se pueda cerrar el servidor
servidor.settimeout(1)

print(f"Servidor escuchando en {HOST}:{PORT}...")

# BUCLE PRINCIPAL DEL SERVIDOR 

try:
    while True:
        try:
            # Acepta una nueva conexión entrante de un cliente.
            cliente_socket, direccion = servidor.accept()

            # Agrega el nuevo cliente a la lista
            clientes.append(cliente_socket)

            # Crea un hilo para manejar la comunicación con ese cliente
            hilo = threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion), daemon=True)
            hilo.start() # Inicia el hilo
        except socket.timeout:
            # Si pasa 1 segundo sin conexiones nuevas, vuelve a intentar (para que Ctrl+C funcione)
            continue

except KeyboardInterrupt:
    # Captura Ctrl+C para cerrar el servidor de forma segura
    print("\n[!] Servidor detenido manualmente.")

    # Envia mensaje de cierre a todos los clientes conectados
    for c in clientes:
        try:
            c.sendall("El servidor se ha cerrado.".encode())
            c.close()
        except:
            pass  # Ignora errores al cerrar sockets

    servidor.close()  # Cierra el socket del servidor
