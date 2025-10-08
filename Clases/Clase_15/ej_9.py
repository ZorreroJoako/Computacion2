import socket
from time import sleep

# Escuchar en todas las interfaces con nc
# nc -ul 0.0.0.0 9008

PORT = 9008
BROADCAST = ("255.255.255.255", PORT)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(1.0)
    s.sendto(b"DISCOVER?", BROADCAST)
    sleep(2)
    try:
        data, addr = s.recvfrom(4096)
        print(f"{addr} -> {data!r}")
    except socket.timeout:
        print("Nadie respondió al broadcast (o la red lo filtra)")
