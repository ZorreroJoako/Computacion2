# Cree un script en Python que genere un proceso hijo que finaliza inmediatamente. El padre no deberá recolectar su estado hasta al menos 10 segundos después.

# Desde Bash, utilice ps y /proc/[pid]/status para identificar el estado Z (zombi) del hijo.

import os, time

def child():
    pid = os.fork()
    if pid == 0:
        print(f'\t[{os.getpid()}] Proceso hijo finalizando...')
        os._exit(0)

if __name__ == '__main__':
    print(f'[{os.getpid()}] Proceso padre, creando hijo...')
    child()
    time.sleep(10)
    os.waitpid(-1, 0)

# vista del proceso zombie en la terminal
# elio      136516  0.0  0.0      0     0 pts/1    Z+   18:44   0:00 [python3] <defunct>