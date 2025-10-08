# Cree un script en Python donde el proceso padre y el hijo se comuniquen usando un os.pipe(). El hijo deberá enviar un mensaje al padre, y este deberá imprimirlo por pantalla.

# Debe usarse codificación binaria y control adecuado de cierre de descriptores.

import os

if __name__ == '__main__':
    r,w=os.pipe()

    try:
        pid=os.fork()
        if pid == 0:
            os.close(r)
            w_fd = os.fdopen(w, 'w')
            w_fd.write('Hola desde el proceso hijo\n')
            w_fd.close()
        else:
            os.close(w)
            r_fd = os.fdopen(r)
            print(f'Padre lee: {r_fd.read()}')
            r_fd.close()
    except OSError as e:
        print('No se ha podido crear el proceso')
        exit(1)

# Padre lee: Hola desde el proceso hijo