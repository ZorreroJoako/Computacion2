# Sistema Concurrente de Análisis Biométrico con Cadena de Bloques Local
Alumno:Zorrero Maio Joaquín Luis
Carrera:Ingeniería en Computación
Legajo:62022
## Archivos entregados
- main.py : Programa principal que genera datos, corre analizadores y verificador y crea blockchain.json.
- verificar_cadena.py : Script independiente que verifica integridad de la cadena y crea reporte.txt.
- blockchain.json : (generado tras ejecutar main.py).
- reporte.txt : (generado por verificar_cadena.py).

## Requisitos
- Python 3.9+
- Paquetes: numpy (instalar con pip install numpy)

## Ejecución
1. Ejecutar el generador y todo el sistema:
```bash
python3 main.py
Esto generará 60 muestras (1 por segundo) y producirá blockchain.json en la carpeta.

Verificar la cadena y generar reporte:
python3 verificar_cadena.py
Se generará reporte.txt con: cantidad de bloques, cantidad de alertas y promedios.

Notas de implementación
Comunicación Principal → Analizadores: multiprocessing.Pipe (un pipe por analizador).

Comunicación Analizadores → Verificador: multiprocessing.Queue (una por analizador).

El verificador persiste blockchain.json tras cada bloque para minimizar pérdida de datos.

Hash calculado con SHA-256:
sha256(prev_hash + json.dumps(datos, sort_keys=True) + timestamp)
Se usan Event y Lock para sincronización y cierre limpio.

Recomendaciones
Si el proceso se interrumpe manualmente (Ctrl+C), el sistema intenta cerrar procesos y persistir lo escrito.

Para inspeccionar la cadena: abrir blockchain.json con un visor de texto.

En este programa utilicé Pipes y Queues porque cumplen funciones distintas y complementarias en la comunicación entre procesos:

Las Pipes se usaron para enviar los paquetes completos generados en el proceso principal hacia cada uno de los procesos analizadores. Los pipes son ideales en este caso porque permiten una comunicación punto a punto, directa y ordenada, asegurando que cada analizador reciba exactamente la misma información de entrada sin necesidad de compartir una cola común.

Las Queues se usaron para que cada analizador pueda enviar sus resultados procesados al proceso verificador. Las colas permiten comunicación unidireccional y segura entre múltiples productores y un consumidor, evitando condiciones de carrera y manejando automáticamente la sincronización de mensajes. De esta forma, los analizadores pueden trabajar en paralelo y el verificador recibe sus salidas de manera ordenada y sin bloqueos.
