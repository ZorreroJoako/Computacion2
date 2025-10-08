# Implemente una versión del problema de los "puestos limitados" usando `multiprocessing.Semaphore`. Cree 10 procesos que intenten acceder a una zona crítica que solo permite 3 accesos simultáneos.

from multiprocessing import Process, Semaphore
import time, random, os

def child(sem):
    print(f'[{os.getpid()}] Proceso iniciado.')
    sem.acquire()
    print(f'[{os.getpid()}] Ha adquirido un puesto.')
    time.sleep(random.randint(1,300)/100)
    sem.release()
    print(f'[{os.getpid()}] Ha liberado un puesto.')

if __name__ == '__main__':
    sem = Semaphore(3)

    children = [Process(target=child, args=(sem,)) for _ in range(10)]
    for child in children:
        child.start()
    for child in children:
        child.join()

# [156338] Proceso iniciado.
# [156338] Ha adquirido un puesto.
# [156339] Proceso iniciado.
# [156339] Ha adquirido un puesto.
# [156340] Proceso iniciado.
# [156340] Ha adquirido un puesto.
# [156341] Proceso iniciado.
# [156342] Proceso iniciado.
# [156343] Proceso iniciado.
# [156344] Proceso iniciado.
# [156345] Proceso iniciado.
# [156346] Proceso iniciado.
# [156347] Proceso iniciado.
# [156340] Ha liberado un puesto.
# [156341] Ha adquirido un puesto.
# [156338] Ha liberado un puesto.
# [156342] Ha adquirido un puesto.
# [156339] Ha liberado un puesto.
# [156343] Ha adquirido un puesto.
# [156343] Ha liberado un puesto.
# [156344] Ha adquirido un puesto.
# [156342] Ha liberado un puesto.
# [156345] Ha adquirido un puesto.
# [156341] Ha liberado un puesto.
# [156346] Ha adquirido un puesto.
# [156345] Ha liberado un puesto.
# [156347] Ha adquirido un puesto.
# [156344] Ha liberado un puesto.
# [156346] Ha liberado un puesto.
# [156347] Ha liberado un puesto.