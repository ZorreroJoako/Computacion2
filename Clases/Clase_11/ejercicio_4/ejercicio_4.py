# Implemente un script que use fork() para crear un proceso hijo. Ese hijo deberá reemplazar su imagen de ejecución por el comando ls -l usando exec().

# Desde Bash, verifique el reemplazo observando el nombre del proceso con ps.

import os

def exec_ls():
    pid = os.fork()
    if pid == 0:
        os.execlp('ls', 'ls', '-l')
    elif pid == -1:
        os._exit(1)

if __name__ == '__main__':
    exec_ls()
    os.wait()

# El cambio de nombre con ps es casi imperseptible ya que todo sucede muy rapidamente como para ser observado