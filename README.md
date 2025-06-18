# TCP Chat Multicliente en Python

Este es un proyecto de ejemplo de comunicación cliente-servidor usando sockets TCP en Python. Fue desarrollado como parte de una práctica académica de la asignatura **Telecomunicaciones**.

Incluye dos formas de uso para los clientes:
- Cliente por consola.
- Cliente con interfaz gráfica usando CustomTkinter.

## Funcionalidades

### Servidor (`servidor.py`)
- Atiende múltiples clientes simultáneamente con `threading`.
- Retransmite los mensajes recibidos a todos los demás clientes conectados.
- Detecta desconexiones y permite cierre limpio con `Ctrl + C`.

### Cliente por Consola (`cliente.py`)
- Envío y recepción simultánea de mensajes mediante hilos.
- Cierre con el comando `salir`.
- Evita el envío de mensajes vacíos.
- Muestra mensajes del servidor en tiempo real.

### Cliente con Interfaz Gráfica (`_cliente_gui.py`)
- Interfaz usando `CustomTkinter`.
- Área de chat con scroll, colores y mensajes diferenciados.
- Botones de conectar, enviar y salir.
- Cierre seguro desde botón o ícono de ventana.
- Compatible con el mismo servidor TCP.

## Requisitos

- Python 3.9 o superior
- Instalar dependencias:

```bash
pip install customtkinter
```

## Cómo ejecutar

1. Ejecutar el servidor
   
```bash
python servidor.py
```

2. Ejecutar uno o varios clientes

* Opción consola:
```bash
python cliente.py
```

* Opción GUI:

```bash
python chat_client_gui.py
```
Puedes abrir múltiples instancias del cliente para simular varios usuarios.

## Notas

* El servidor usa HOST = 0.0.0.0 para escuchar en todas las interfaces.

* El cliente por defecto se conecta a 127.0.0.1. Si usas otro equipo, cambia el HOST del cliente por la IP del servidor.

* Puerto predeterminado: 12345.

## Estructura del proyecto

```bash
📁 tcp-chat-multicliente
├── chat_server.py          # Servidor TCP
├── chat_client.py          # Cliente de consola
├── chat_client_gui.py      # Cliente con interfaz gráfica (GUI)
└── README.md               # Este documento
```

## Autora

Franmari Garcia
