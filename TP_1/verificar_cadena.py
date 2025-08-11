import json
import hashlib
import os

BLOCKCHAIN = 'blockchain.json'
REPORTE = 'reporte.txt'


def verificar():
    if not os.path.exists(BLOCKCHAIN):
        print('No se encontró', BLOCKCHAIN)
        return 1

    with open(BLOCKCHAIN, 'r') as f:
        chain = json.load(f)

    corruptos = []
    prev = '0' * 64
    # para promedios
    cnt = 0
    sum_freq = 0.0
    sum_ox = 0.0
    sum_pres_s = 0.0
    sum_pres_d = 0.0
    alerts = 0

    for idx, block in enumerate(chain):
        datos = block['datos']
        ts = block['timestamp']
        # recalcular hash
        hash_input = block.get('prev_hash', '') + json.dumps(datos, sort_keys=True) + ts
        h = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

        if block.get('prev_hash', '') != prev:
            corruptos.append((idx, 'prev_hash mismatch'))
        if block.get('hash', '') != h:
            corruptos.append((idx, 'hash mismatch'))

        prev = block.get('hash', '')

        # acumular
        try:
            sum_freq += float(datos['frecuencia']['media'])
            sum_ox += float(datos['oxigeno']['media'])
            pres_media = datos['presion']['media']
            # pres_media puede ser lista [sist, diast]
            sum_pres_s += float(pres_media[0])
            sum_pres_d += float(pres_media[1])
            cnt += 1
        except Exception:
            pass

        if block.get('alerta'):
            alerts += 1

    # escribir reporte
    with open(REPORTE, 'w') as f:
        f.write(f"Total bloques: {len(chain)}\n")
        f.write(f"Bloques con alerta: {alerts}\n")
        if cnt:
            f.write(f"Promedio frecuencia (media de medias): {sum_freq/cnt:.2f}\n")
            f.write(f"Promedio oxígeno (media de medias): {sum_ox/cnt:.2f}\n")
            f.write(f"Promedio presión sistólica: {sum_pres_s/cnt:.2f}\n")
            f.write(f"Promedio presión diastólica: {sum_pres_d/cnt:.2f}\n")
        else:
            f.write('No hay datos para promedios\n')

        if corruptos:
            f.write('\nBloques corruptos encontrados:\n')
            for idx, reason in corruptos:
                f.write(f" - Bloque {idx}: {reason}\n")
        else:
            f.write('\nNo se encontraron bloques corruptos.\n')

    print('Verificación finalizada. Reporte escrito en', REPORTE)
    return 0


if __name__ == '__main__':
    exit(verificar())