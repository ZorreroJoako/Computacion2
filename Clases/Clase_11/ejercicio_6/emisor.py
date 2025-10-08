# Cree un FIFO en /tmp/mi_fifo usando Bash (mkfifo). Luego:
# Escriba un script emisor.py que escriba mensajes en el FIFO.
# Escriba un script receptor.py que lea desde el FIFO e imprima los mensajes.
# Ejecute ambos scripts en terminales distintas.

import os

if not os.path.exists('/tmp/my_fifo'):
    os.mkfifo('/tmp/my_fifo')

fd = os.open('/tmp/my_fifo', os.O_WRONLY)
os.write(fd,b'Hola desde emisor.py')
os.close(fd)

# Simplemente se ejecuta y queda en ejecución hasta que receptor lee.
# python3 Clases/Clase_11/ejercicio_6/emisor.py 