import socket
from time import sleep

# nc -u -l 127.0.0.1 9007

HOST, PORT = "127.0.0.1", 9007

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(1.0)
    retries = 3
    for i in range(1, retries + 1):
        try:
            s.sendto(b"TIME", (HOST, PORT))
            sleep(2) # espero 2 segundos antes de reintentar
            data, _ = s.recvfrom(2048) # aquí _ lo usamos para ignorar addr 
            # s.recvfrom -> data,addr (python lo desempaqueta)
            print("Respuesta:", data.decode())
            break
        except socket.timeout:
            print(f"Timeout intento {i}; reintentando...")
    else:
        print("Sin respuesta tras reintentos")
