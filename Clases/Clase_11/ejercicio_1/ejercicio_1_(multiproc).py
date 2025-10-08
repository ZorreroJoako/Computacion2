# Escriba un script en Python llamado `gestor.py` que reciba argumentos desde la línea de comandos utilizando `argparse`:

# - La opción `--num` indica la cantidad de procesos hijos a crear.
# - La opción `--verbose` activa mensajes detallados.

# Cada proceso hijo debe dormir entre 1 y 5 segundos y luego terminar. El proceso padre debe imprimir su PID y mostrar la jerarquía de procesos usando `pstree -p`.

# Desde otra terminal, el estudiante deberá observar el estado de los procesos con `ps` o accediendo a `/proc`.

from random import randint
from multiprocessing import Process, current_process
import argparse, time, os

def exec_pstree():
    ppid = current_process().pid
    pid = os.fork()
    if pid == 0:
        os.execlp("pstree", "pstree", "-p", str(ppid))

def create_child(verbose=False):
    if verbose:
        print(f'    [{current_process().pid}] Proceso hijo, PPID: {current_process()._parent_pid}')
    time.sleep(randint(14,15))
    if verbose:
        print(f'    [{current_process().pid}] Proceso hijo terminado.')

def set_args():
    parser = argparse.ArgumentParser(
        prog='Ejercicio 1',
        description="Creación de procesos con argumentos"
    )
    
    parser.add_argument("-n", "--num", type=int, required=True, help="Indica la cantidad de procesos hijos a crear")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verboso")

    args = parser.parse_args()
    return parser, args

if __name__ == "__main__":
    parser, args = set_args()

    print(f"[+] Modo verboso: {'Activo' if args.verbose else 'Inactivo'}")
    print(f"[+] Creando {args.num} procesos hijos...")

    children = [Process(target=create_child, args=(args.verbose,)) for _ in range(args.num)]
    if args.verbose:
        print(f"[*] Iniciando los procesos hijos...")
    for child in children:
        child.start()
    time.sleep(0.1)
    print(f'[{current_process().pid}] jerarquia de procesos:')
    exec_pstree()
    time.sleep(0.1)
    if args.verbose:
        print(f'[{current_process().pid}] esperando a los procesos hijos.')
    for child in children:
        child.join()
    print('[-] Todos los procesos han terminado. Saliendo...')