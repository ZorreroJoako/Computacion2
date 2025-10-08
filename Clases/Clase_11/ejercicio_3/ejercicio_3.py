# Diseñe un script que cree un proceso hijo que siga ejecutándose luego de que el proceso padre haya terminado. Verifique desde Bash que el nuevo PPID del proceso hijo corresponde a init o systemd.

import os, time

def child():
    pid = os.fork()
    if pid == 0:
        time.sleep(10)
        print(f'\t [{os.getpid()}] Proceso Hijo - Proceso padre {os.getppid()}')
        os._exit(0)

if __name__ == '__main__':
    print(f'[{os.getpid()}] Proceso padre - Creando proceso hijo...')
    child()
    print(f'[{os.getpid()}] Proceso padre finalizado')
    os._exit(0)

# Salida
# [138361] Proceso padre - Creando proceso hijo...
# [138361] Proceso padre finalizado
# [138362] Proceso Hijo - Proceso padre 1204
