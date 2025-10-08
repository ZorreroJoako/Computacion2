from multiprocessing import Process, Event
import time

def tarea_lenta(event):
    print("Proceso lento iniciando tarea...")
    time.sleep(3)
    print("Proceso lento finalizó. Activando el evento.")
    event.set()

def tarea_dependiente(event):
    print("Proceso dependiente esperando el evento...")
    event.wait()
    print("Evento recibido. Proceso dependiente continúa.")

if __name__ == "__main__":
    evento = Event()

    p1 = Process(target=tarea_lenta, args=(evento,))
    p2 = Process(target=tarea_dependiente, args=(evento,))

    p2.start()
    p1.start()

    p1.join()
    p2.join()
