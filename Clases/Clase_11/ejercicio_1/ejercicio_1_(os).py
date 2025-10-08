# Escriba un script en Python llamado `gestor.py` que reciba argumentos desde la línea de comandos utilizando `argparse`:

# - La opción `--num` indica la cantidad de procesos hijos a crear.
# - La opción `--verbose` activa mensajes detallados.

# Cada proceso hijo debe dormir entre 1 y 5 segundos y luego terminar. El proceso padre debe imprimir su PID y mostrar la jerarquía de procesos usando `pstree -p`.

# Desde otra terminal, el estudiante deberá observar el estado de los procesos con `ps` o accediendo a `/proc`.

from random import randint
import argparse, os, time

def exec_pstree():
    ppid = os.getpid()
    pid = os.fork()
    if pid == 0:
        os.execlp("pstree", "pstree", "-p", str(ppid))

def create_child(verbose=False):
    pid = os.fork()
    if pid == 0:  # Proceso hijo asigna 0 a pid - proceso padre adquiere el pdi del hijo
        if verbose:
            print(f'    [{os.getpid()}] Proceso hijo, PPID: {os.getppid()}')
        time.sleep(randint(1,5))
        if verbose:
            print(f'    [{os.getpid()}] Proceso hijo terminado.')
        os._exit(0)  
    return pid

def set_args():
    parser = argparse.ArgumentParser(
        prog='Ejercicio 1',
        description="Creación de procesos con argumentos"
    )
    
    parser.add_argument("-n", "--num", type=int, required=True, help="Indica la cantidad de procesos hijos a crear")
    parser.add_argument("-v", "--verbose", action="store_true", help="Modo verboso")

    args = parser.parse_args()
    return parser, args

def main():
    parser, args = set_args()

    print(f"[+] Modo verboso: {'Activo' if args.verbose else 'Inactivo'}")
    print(f"[+] Creando {args.num} procesos hijos...")
    children = [create_child(args.verbose) for _ in range(args.num)]
    time.sleep(1)

    print(f'[{os.getpid()}] jerarquia de procesos:')
    exec_pstree()

    if args.verbose:
        print(f'[{os.getpid()}] esperando a los procesos hijos.')
    for child in children:
        os.waitpid(child, 0)
    print('[-] Todos los procesos han terminado. Saliendo...')

if __name__ == "__main__":
    main()