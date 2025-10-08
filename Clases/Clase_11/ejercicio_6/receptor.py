# Cree un FIFO en /tmp/mi_fifo usando Bash (mkfifo). Luego:
# Escriba un script emisor.py que escriba mensajes en el FIFO.
# Escriba un script receptor.py que lea desde el FIFO e imprima los mensajes.
# Ejecute ambos scripts en terminales distintas.

import os, errno

if not os.path.exists('/tmp/my_fifo'):
    os.mkfifo('/tmp/my_fifo')

try:
    fd = os.open('/tmp/my_fifo', os.O_RDONLY)
    data = os.read(fd, 1024)
    print('Lectura: ', data.decode())
    os.close(fd)
    os.remove('/tmp/my_fifo')
except OSError as e:
    if e.errno == errno.ENXIO:
        print('No hay escritor disponible aún.')

# Al ejecutar el receptor luego, el emisor termina
# python3 Clases/Clase_11/ejercicio_6/receptor.py 
# Lectura:  Hola desde emisor.py
