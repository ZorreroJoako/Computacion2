# Diseñe una clase `CuentaBancaria` con métodos `depositar` y `retirar`, ambos protegidos con un `RLock`. Permita que estos métodos se llamen recursivamente (desde otros métodos sincronizados).

# Simule accesos concurrentes desde varios procesos.

from multiprocessing import Process, RLock, Value
from random import randint
import os

class CuentaBancaria():
    def __init__(self, usuario):
        self.__usuario__ = usuario
        self.__dinero_disponible__ = Value('i',0)
    
    def __depositar__(self, monto, rlock):
        rlock.acquire()
        self.__dinero_disponible__.value += monto
        rlock.release()

    def __retirar__(self, monto, rlock):
        if (monto - self.__dinero_disponible__.value) < 0:
            rlock.acquire()
            self.__dinero_disponible__.value -= monto
            rlock.release()

    def get_dinero(self):
        return self.__dinero_disponible__.value

def deposit_worker(cuenta,rlock):
    monto = randint(100,1000)
    print(f'[{os.getpid()}] Proceso depositador: {monto}')
    cuenta.__depositar__(monto,rlock)

def retire_worker(cuenta,rlock):
    monto = randint(10,1000)
    print(f'[{os.getpid()}] Proceso retirador: {monto}')
    cuenta.__retirar__(monto, rlock)

if __name__ == '__main__':
    rlock = RLock()
    cuenta = CuentaBancaria('Elio')
    deposit_children = [Process(target=deposit_worker,args=(cuenta,rlock)) for _ in range(5)]
    retire_children = [Process(target=retire_worker, args=(cuenta,rlock)) for _ in range(4)]

    for depositer in deposit_children:
        depositer.start()
    for retirer in retire_children:
        retirer.start()
    
    for depositer in deposit_children:
        depositer.join()
    for retirer in retire_children:
        retirer.join()
    print(f'[+] Dinero de la cuenta: {cuenta.get_dinero()}')

# Salida
# [160280] Proceso depositador: 393
# [160281] Proceso depositador: 684
# [160282] Proceso depositador: 556
# [160283] Proceso depositador: 851
# [160284] Proceso depositador: 448
# [160285] Proceso retirador: 687
# [160286] Proceso retirador: 160
# [160287] Proceso retirador: 983
# [160288] Proceso retirador: 348
# [+] Dinero de la cuenta: 754
# El resultado final es el esperado, no han habido sobreescrituras del valor dinero