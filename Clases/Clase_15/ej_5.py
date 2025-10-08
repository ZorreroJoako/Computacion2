import socket
from time import sleep

# primero ejecutamos el programa de python y luego, ejecutamos
# nc -l 127.0.0.1 9004 
# esto es para forzar a que hayan reintentos de conexión

HOST, PORT = "127.0.0.1", 9004

def try_connect(max_retries=5, base_backoff=0.5):
    for attempt in range(1, max_retries + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.5)  # segundos
                s.connect((HOST, PORT))
                s.sendall(b"ping\n")
                data = s.recv(1024)
                return data
        except (socket.timeout, ConnectionRefusedError) as e:
            sleep_s = base_backoff * attempt                # sleep es cada vez mayor 0.5 * {1,2,...,5}
            print(f"Intento {attempt} falló ({e}). Reintento en {sleep_s:.1f}s...")
            sleep(sleep_s)
    raise TimeoutError("Servidor no disponible tras varios reintentos")

if __name__ == "__main__":
    print(try_connect())

# Una forma interesante para ejecutar este ejercicio y ver los reintentos y como se puede concluir la conexión
# es ejecutando el programa de python con 
# sleep 2 && python3 ej_5.py (esto espera 2 segundos antes de ejecutar el script)

# Por otro lado lanzamos 3 veces el servidor de nc
# for n in {1,..,3}; do echo "[+] servidor $n" ; nc -l 127.0.0.1 9004 ; done
# Y cuando se establezca la conexión intentamos
# escribir algo como "hola" en nc, y vemos como python cierra exitosamente la 
# conexión
