import socket

# Ejecutar desde bash
# nc -l 127.0.0.1 9002
# Aquí ponemos netcat en escucha en el puerto 9001 de loopback
# 9001 lo usamos como socket orientado a conexión (TCP en este caso)
# Si quisieramos usar un socket con un protocolo sin conexión 
# debemos usar el parametro -u (conexión de datagramas UDP)

# En python también debemos usar el mismo protocolo y usar la misma dirección IP
# Loopback tiene un rango enorme de IPs ya que es 127.0.0.1/8
# Entonces la mascara es 255.0.0.0
# Podemos usar cualquier IP 127.xxx.xxx.xxx

def send_lines(sock, lines):
    for line in lines:
        if not line.endswith("\n"):
            line += "\n"
        sock.sendall(line.encode("utf-8"))

def recv_until_closed(sock):
    # Acumula hasta que el peer cierre; en un protocolo real pararíamos por un token/longitud
    chunks = []
    while True:
        b = sock.recv(1024)
        if not b:  # 0 bytes → peer cerró
            break
        chunks.append(b)
    return b"".join(chunks)

def main():
    HOST, PORT = "127.0.0.1", 9002
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        send_lines(s, ["uno", "dos", "tres"])  # desde la terminal del `nc` podés escribir respuestas
        # Esta línea es medio dudosa. Lo que pasa es que al decirle a nc que no transmitimos más
        # nc cierra la conexión
        s.shutdown(socket.SHUT_WR)               # anuncias que ya no enviarás más
        data = recv_until_closed(s)
        print(data.decode("utf-8", errors="replace"))

if __name__ == "__main__":
    main()
