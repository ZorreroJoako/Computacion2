import json
import time
import hashlib
import multiprocessing as mp
from multiprocessing import Pipe, Queue, Lock
from datetime import datetime
import random
import os
import numpy as np

SAMPLES = 60
WINDOW = 30

# ---------- Analizador (proc A/B/C) ----------
def analizador(name: str, conn, out_queue: Queue, stop_event: mp.Event):
    """Recibe paquetes completos por conn (Pipe), extrae su señal y mantiene ventana móvil.
    Envía a out_queue un diccionario por cada paquete con media y desviación de la señal.
    name: 'frecuencia' | 'presion' | 'oxigeno'
    """
    window = []  # guardará las muestras (para presion guardamos tuplas)
    try:
        while not stop_event.is_set():
            try:
                paquete = conn.recv()
            except EOFError:
                break
            if paquete is None:
                # señal de finalización
                break
            ts = paquete['timestamp']
            if name == 'frecuencia':
                val = int(paquete['frecuencia'])
            elif name == 'presion':
                # guardamos como tupla (sist, diast)
                val = tuple(paquete['presion'])
            elif name == 'oxigeno':
                val = int(paquete['oxigeno'])
            else:
                raise ValueError('Nombre de señal desconocido')

            window.append(val)
            # mantener sólo últimos WINDOW
            if len(window) > WINDOW:
                window.pop(0)

            # calcular media y desviación
            if name == 'presion':
                arr = np.array(window)
                # arr shape (n,2)
                media = arr.mean(axis=0).tolist()
                desv = arr.std(axis=0, ddof=0).tolist()
            else:
                arr = np.array(window, dtype=float)
                media = float(arr.mean()) if arr.size else 0.0
                desv = float(arr.std(ddof=0)) if arr.size else 0.0

            resultado = {
                'tipo': name,
                'timestamp': ts,
                'media': media,
                'desv': desv
            }
            out_queue.put(resultado)
    finally:
        # intentar cerrar conexión
        try:
            conn.close()
        except Exception:
            pass


# ---------- Verificador / Constructor de bloques ----------
def verificador(queues_dict, blockchain_path: str, file_lock: Lock, stop_event: mp.Event, total_expected: int):
    """Recibe resultados de 3 queues (frecuencia, presion, oxigeno), espera los 3 por timestamp,
    valida rangos, construye y guarda bloques en blockchain_path cada vez que completa un timestamp.
    """
    # In-memory chain
    chain = []
    prev_hash = '0' * 64

    # si existe blockchain_path y tiene contenido, lo cargamos para continuar
    if os.path.exists(blockchain_path):
        try:
            with open(blockchain_path, 'r') as f:
                existing = json.load(f)
                if isinstance(existing, list) and existing:
                    chain = existing
                    prev_hash = chain[-1]['hash']
        except Exception:
            # si archivo corrupto, ignoramos y reescribimos
            chain = []
            prev_hash = '0' * 64

    pending = {}  # pending[timestamp] = {tipo: resultado,...}
    blocks_written = 0

    # while loop hasta procesar total_expected bloques
    while not stop_event.is_set() and blocks_written < total_expected:
        # bloquear hasta que haya datos de cualquiera de las colas
        # usamos get with timeout para poder comprobar stop_event periódicamente
        for tipo, q in queues_dict.items():
            try:
                item = q.get(timeout=1.0)
            except Exception:
                item = None
            if item is None:
                continue
            ts = item['timestamp']
            pending.setdefault(ts, {})[tipo] = item

            # si ya tenemos 3 resultados para ese timestamp, procesar
            if set(pending[ts].keys()) == set(queues_dict.keys()):
                fre = pending[ts]['frecuencia']
                pres = pending[ts]['presion']
                oxy = pending[ts]['oxigeno']

                # comprobaciones simples
                alerta = False
                try:
                    if fre['media'] >= 200:
                        alerta = True
                    if not (90 <= oxy['media'] <= 100):
                        alerta = True
                    # presión sistólica media (pres['media'][0]) < 200
                    if isinstance(pres['media'], list) and pres['media'][0] >= 200:
                        alerta = True
                except Exception:
                    alerta = True

                datos = {
                    'frecuencia': {'media': fre['media'], 'desv': fre['desv']},
                    'presion': {'media': pres['media'], 'desv': pres['desv']},
                    'oxigeno': {'media': oxy['media'], 'desv': oxy['desv']}
                }

                # hash: sha256(prev_hash + str(datos) + timestamp) pero usamos json.dumps determinista
                hash_input = prev_hash + json.dumps(datos, sort_keys=True) + ts
                h = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

                bloque = {
                    'timestamp': ts,
                    'datos': datos,
                    'alerta': bool(alerta),
                    'prev_hash': prev_hash,
                    'hash': h
                }

                # encadenar
                chain.append(bloque)
                prev_hash = h
                blocks_written += 1

                # persistir en disco (reescribimos la lista completa)
                try:
                    file_lock.acquire()
                    with open(blockchain_path, 'w') as f:
                        json.dump(chain, f, indent=2)
                finally:
                    try:
                        file_lock.release()
                    except Exception:
                        pass

                print(f"Bloque {blocks_written-1} | ts={ts} | hash={h} | alerta={bloque['alerta']}")

                # borrar pending
                del pending[ts]

    # fin mientras
    # al finalizar, guardar chain una última vez (ya se guardó cada iteración, pero por seguridad)
    try:
        file_lock.acquire()
        with open(blockchain_path, 'w') as f:
            json.dump(chain, f, indent=2)
    finally:
        try:
            file_lock.release()
        except Exception:
            pass

    print('Verificador finalizado. Bloques escritos:', blocks_written)


# ---------- Generador principal ----------
def generador(pipes, total_samples: int, stop_event: mp.Event):
    """Genera total_samples paquetes (1 por segundo) y los envía por cada pipe (full dict).
    pipes: dict name->conn
    """
    for i in range(total_samples):
        now = datetime.now().replace(microsecond=0)
        paquete = {
            'timestamp': now.isoformat(),
            'frecuencia': random.randint(60, 180),
            'presion': [random.randint(110, 180), random.randint(70, 110)],
            'oxigeno': random.randint(90, 100)
        }
        # enviar a cada analizador
        for conn in pipes.values():
            try:
                conn.send(paquete)
            except Exception:
                pass

        time.sleep(1.0)

    # enviar None como sentinel
    for conn in pipes.values():
        try:
            conn.send(None)
        except Exception:
            pass
    # señal de parada
    stop_event.set()


# ---------- Main orchestration ----------
def main():
    mp.set_start_method('spawn')
    # pipes main->analizadores
    parent_conns = {}
    child_conns = {}
    for name in ('frecuencia', 'presion', 'oxigeno'):
        pconn, cconn = Pipe()
        parent_conns[name] = pconn
        child_conns[name] = cconn

    # queues analizadores->verificador
    q_f = Queue()
    q_p = Queue()
    q_o = Queue()
    queues = {'frecuencia': q_f, 'presion': q_p, 'oxigeno': q_o}

    file_lock = Lock()
    stop_event = mp.Event()

    # lanzar procesos analizadores
    procesos = []
    for name in ('frecuencia', 'presion', 'oxigeno'):
        p = mp.Process(target=analizador, args=(name, child_conns[name], queues[name], stop_event), name=f'anal_{name}')
        p.start()
        procesos.append(p)

    # lanzar verificador
    blockchain_path = 'blockchain.json'
    verif = mp.Process(target=verificador, args=(queues, blockchain_path, file_lock, stop_event, SAMPLES), name='verificador')
    verif.start()

    # lanzar generador en proceso principal (no es necesario crear proceso separado)
    try:
        generador(parent_conns, SAMPLES, stop_event)
    except KeyboardInterrupt:
        print('Interrumpido por usuario')
        stop_event.set()

    # esperar que analizador termine
    for p in procesos:
        p.join(timeout=5)
        if p.is_alive():
            p.terminate()

    # esperar verificador
    verif.join(timeout=10)
    if verif.is_alive():
        verif.terminate()

    # cerrar pipes
    for c in parent_conns.values():
        try:
            c.close()
        except Exception:
            pass

    print('Programa principal finalizado.')


if __name__ == '__main__':
    main()