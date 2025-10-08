import socket
import time

# Ejecutar desde bash
# nc -l 127.0.0.1 9001 
# Aquí ponemos netcat en escucha en el puerto 9001 de loopback
# 9001 lo usamos como socket orientado a conexión (TCP en este caso)
# Si quisieramos usar un socket con un protocolo sin conexión 
# debemos usar el parametro -u (conexión de datagramas UDP)

# En python también debemos usar el mismo protocolo y usar la misma dirección IP
# Loopback tiene un rango enorme de IPs ya que es 127.0.0.1/8
# Entonces la mascara es 255.0.0.0
# Podemos usar cualquier IP 127.xxx.xxx.xxx
def main():
    HOST, PORT = "127.0.0.1", 9001
    # AF_INET = IPv4 (socket de internet IPv4), SOCK_STREAM = TCP (protocolo orientado a conexión)
    start = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))                # 3-way handshake TCP
        s.sendall(b"hola mundo\n")             # envío atómico (o en fragmentos internos)
        end = time.time()
        data = s.recv(4096)                    # bloquea hasta recibir algo o cerrar
        print(f"< {data!r}")
        print(f'Tiempo {end - start}')
        # Si se recibe más de 4096 bytes, como el socket se cierra (en este caso)
        # la información se pierde


if __name__ == "__main__":
    main()
