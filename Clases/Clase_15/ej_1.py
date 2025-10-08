import socket
import os

# Ejecutar desde bash
# nc -lU /tmp/eco.sock (solo funciona con OpenBSD netcat)
#   -l: netcat se pone en escucha
#   -U: socket tipo unix
# /tmp/eco.sock es el fd del socket
# En /proc/pid/fd podemos ver los 4 archivos 
# 0 -> salida estándar
# 1 -> salida estándar 
# 2 -> salida estándar
# 3 -> puntero al socket
#
# Nota importante:
# Lo que se envia y se recibe es binario no string o texto

SOCKET_PATH = "/tmp/eco.sock"

def main():
    if not os.path.exists(SOCKET_PATH):
        raise SystemExit(f"No existe {SOCKET_PATH}. ¿Arrancaste `nc -lU {SOCKET_PATH}`?")

    # AF_UNIX = dominio local (archivo-socket), STREAM = estilo TCP (Orientado a conexióUDSn)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(SOCKET_PATH)
        s.sendall(b"hola desde Python\n")
        # `nc` no hace eco automático, pero podés teclear algo y ENTER en la terminal del nc
        # para que el cliente lo lea. Si no hay datos, recv puede bloquear.
        data = s.recv(4096)
        print(f"< {data!r}")

if __name__ == "__main__":
    main()
