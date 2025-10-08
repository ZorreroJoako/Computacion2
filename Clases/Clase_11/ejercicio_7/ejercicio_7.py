# Utilice `multiprocessing.Process` para crear 4 procesos que escriban su identificador y una marca de tiempo en un mismo archivo de log. Utilice `multiprocessing.Lock` para evitar colisiones.

# Es importante que se ejecute en el directorio /ruta_al_repositorio/Clases/Clase_11/ejercicio_7 para que temp.log se cree donde corresponde.

from multiprocessing import Process, Lock
import datetime, os

def child(f,l):
    with l:
        with open(f, 'a') as log:
            log.write(f'[{datetime.datetime.now()}] PID: {os.getpid()}\n')
    

if __name__ == '__main__':
    l=Lock()
    f='temp.log'
    children = [Process(target=child, args=(f,l)) for _ in range(4)]
    for child in children:
        child.start()
    for child in children:
        child.join()

# Salida
# [2025-06-10 20:37:27.230798] PID: 144924
# [2025-06-10 20:37:27.231215] PID: 144925
# [2025-06-10 20:37:27.231550] PID: 144926
# [2025-06-10 20:37:27.231905] PID: 144927
