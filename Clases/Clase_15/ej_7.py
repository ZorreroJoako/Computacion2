import socket
import time

# Primero ejecutamos el servidor UDP
# nc -u -l 127.0.0.1 9006
#   -u es para protocolo sin conexión 

HOST, PORT = "127.0.0.1", 9006

# Ojo: Acá se define un socket udp
start = time.time()
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b"hola mundo\n", (HOST, PORT))
    end = time.time()
    data, addr = s.recvfrom(2048) # Tamaño máximo del datagrama
    print(f"< {data!r} desde {addr}")
    print(f'Tiempo {end - start}')
    # < b'pong\n' desde ('127.0.0.1', 9006)
