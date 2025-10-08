#!/bin/bash

hijo() {
    ppid=$1
    verbose=$2
    if $verbose; then
        echo -e "\t[$(echo $$)] Proceso Hijo -> Proceso padre: $ppid"
    fi
    A=1
    B=5
    sleep $((RANDOM % (B - A + 1) + A))
    if $verbose; then
        echo -e "\t[$(echo $$)] Proceso Hijo terminado"
    fi
}

while getopts "n:vh" opt; do
  case $opt in
    n)
      num_procesos=$OPTARG
      ;;
    v)
      verbose=true
      ;;
    h)
      echo -e "Uso: $0 [-n NUM_PROCESOS] [-v] [-h]\n\t-n NUM_PROCESOS: Cantidad de procesos hijos a crear\n\t-v: Activar modo verboso\n\t-h: Mostrar ayuda"; exit 0
      ;;
    \?)
      echo "Opción inválida: -$OPTARG" >&2
      ;;
  esac
done

if ! [[ "$num_procesos" =~ ^[0-9]+$ ]] || (( num_procesos <= 0 )); then
  echo "[!] Se debe especificar un número entero positivo de procesos"; exit 1
elif [ -z "$num_procesos" ]; then
  echo "[!] Se debe especificar un número de procesos"; exit 1
fi

if [ "$verbose" = true ]; then
  echo "Modo verboso activado"
else
  verbose=false
fi
echo "[+] Creando $num_procesos procesos"

ppid=$(ps | head -n 2 | tail -n 1 | awk '{print $1}')
echo "[$ppid] Proceso Principal"

for i in $(seq 1 $num_procesos); do
    if $verbose; then
        echo "[+] Creando el proceso hijo numero $i"
    fi
    hijo $ppid $verbose &
done

wait

echo "[-] Todos los procesos han terminado, finalizando..."


# Escriba un script en Python llamado `gestor.py` que reciba argumentos desde la línea de comandos utilizando `argparse`:

# - La opción `--num` indica la cantidad de procesos hijos a crear.
# - La opción `--verbose` activa mensajes detallados.

# Cada proceso hijo debe dormir entre 1 y 5 segundos y luego terminar. El proceso padre debe imprimir su PID y mostrar la jerarquía de procesos usando `pstree -p`.

# Desde otra terminal, el estudiante deberá observar el estado de los procesos con `ps` o accediendo a `/proc`.
