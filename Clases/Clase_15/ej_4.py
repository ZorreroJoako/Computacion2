import socket

# Desde bash
# nc -l 127.0.0.1 9003 < archivo_grande.bin -N
# El parámetro -N indica a nc que cuando termine el archivo_grande.bin
# se ha llegado al fin de la transmisión (close on EOF from stdin)

# Para en nc de GNU se puede conseguir lo mismo usando
# nc -l -p 9003 -q 0 < archivo_grande.bin
# Donde -q 0 indica que el último bit será nulo (indicando a python
# que debe terminar (brake))

# por obvias razones necesitamos un archivo binario "grande"
# Hay varias alternativas:
#   generar un archivo (de 50MiB p.e) lleno de ceros
#      dd if=/dev/zero of=archivo_grande.bin bs=1M count=50
#   generar un archivo (de 10MiB p.e) con contenido aleatorio
#      dd if=/dev/urandom of=archivo_grande.bin bs=1M count=10

def recv_all(sock):
    chunks = []
    while True:
        b = sock.recv(64 * 1024)  # 64 KiB por iteración
        if not b:
            break
        chunks.append(b)
    return b"".join(chunks)

def main():
    HOST, PORT = "127.0.0.1", 9003
    # sock_stream: TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        data = recv_all(s)
        print(f"Recibidos {len(data)} bytes")

if __name__ == "__main__":
    main()
