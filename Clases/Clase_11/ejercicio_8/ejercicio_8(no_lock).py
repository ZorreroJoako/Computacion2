# Implemente un contador compartido entre dos procesos sin usar `Lock`, para evidenciar una condición de carrera. Luego modifique el programa para corregir el problema usando `multiprocessing.Lock`.

# Compare ambos resultados.

from multiprocessing import Process, Value
from random import randint
import os, time

def child(cont):
    for _ in range(10):
        if cont.value != 10:
            time.sleep(0.2)
            cont.value += 1
        time.sleep(0.2)
        

if __name__ == '__main__':
    cont = Value('i',0)
    children = [Process(target=child, args=(cont,)) for _ in range(100)]
    for child in children:
        child.start()
    for child in children:
        child.join()
    print(f'Resultado: {cont.value}')

# Salida obtenida tras la ejecución
# Resultado: 994
# Salida esperada:
# Resultado: 10