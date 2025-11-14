import socketserverimport socketserver
import multiprocessing as mp
import argparse
import sys
import os
import json
import time 
import socket 

# IMPORTACIONES CLAVE
from common.protocol import decode_header, encode_message, HEADER_SIZE
from common.serialization import deserialize_data, serialize_data
from processor.screenshot import generate_screenshot
from processor.performance import analyze_performance
from processor.image_processor import process_images 

# -------------------------------------------------------------------
# Lógica del Worker (Ejecutado por cada proceso del Pool)
# -------------------------------------------------------------------
def worker_process(request_data: dict) -> dict:
    """Ejecuta todas las tareas CPU-Bound para una solicitud."""
    url = request_data.get('url')
    image_urls = request_data.get('image_urls', [])
    
    print(f"Proceso {os.getpid()}: Procesando URL: {url}")
    
    try:
        # Llamadas a las funciones pesadas de los módulos de 'processor/'
        screenshot_b64 = generate_screenshot(url)
        performance_data = analyze_performance(url)
        thumbnails = process_images(image_urls)
        
        return {
            "screenshot": screenshot_b64,
            "performance": performance_data,
            "thumbnails": thumbnails
        }
    except Exception as e:
        print(f"Error en worker_process para {url}: {e}", file=sys.stderr)
        return {
            "error": f"Error en procesamiento paralelo: {e}",
            "screenshot": "",
            "performance": {"load_time_ms": 0, "total_size_kb": 0, "num_requests": 0},
            "thumbnails": []
        }

# -------------------------------------------------------------------
# Lógica del Handler (Maneja la conexión de socket)
# -------------------------------------------------------------------
class ProcessingTCPHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        pool = self.server.process_pool 
        
        try:
            # 1. Leer encabezado (longitud)
            header_bytes = self.request.recv(HEADER_SIZE)
            if not header_bytes or len(header_bytes) < HEADER_SIZE:
                return
            
            msg_len = decode_header(header_bytes)
            
            # 2. Leer mensaje completo
            data_bytes = b''
            bytes_received = 0
            while bytes_received < msg_len:
                chunk = self.request.recv(msg_len - bytes_received)
                if not chunk: break
                data_bytes += chunk
                bytes_received += len(chunk)
            
            if bytes_received != msg_len:
                raise ConnectionError("Lectura incompleta del mensaje.")
            
            request_data = deserialize_data(data_bytes)
            
            # 3. Enviar al Pool de Procesos y esperar resultado
            result = pool.apply(worker_process, args=(request_data,))
            
            # 4. Enviar el resultado de vuelta al Servidor A
            response_bytes = encode_message(result)
            self.request.sendall(response_bytes)

        except Exception as e:
            print(f"Error en el Handler del Servidor B: {e}", file=sys.stderr)
            error_response = encode_message({"error": str(e), "status": "processor_failure"})
            try:
                self.request.sendall(error_response)
            except:
                pass 

# -------------------------------------------------------------------
# Inicialización del Servidor (Soporte IPv4 e IPv6)
# -------------------------------------------------------------------

class DualStackTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    address_family = socket.AF_INET # Por defecto

    def server_bind(self):
        # Si la IP es IPv6 (contiene ':'), ajustamos la familia del socket.
        if ':' in self.server_address[0]:
            self.address_family = socket.AF_INET6
            
            try:
                # Deshabilita el mapeo de IPv4 en IPv6 para evitar errores de enlace
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except Exception:
                pass # Ignorar si la opción no está disponible
            
        return super().server_bind()


class ThreadedTCPServer(DualStackTCPServer):
    pass
    
def run_server_b(ip, port, num_processes):
    
    with mp.Pool(processes=num_processes) as pool:
        
        ThreadedTCPServer.allow_reuse_address = True
        server = ThreadedTCPServer((ip, port), ProcessingTCPHandler) 
        server.process_pool = pool 
        
        print(f"Servidor B (Procesamiento) escuchando en {ip}:{port} con {num_processes} procesos.")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Servidor B detenido por el usuario.")
        except Exception as e:
            print(f"Error fatal en serve_forever: {e}", file=sys.stderr)


if __name__ == '__main__':
    # ... (Manejo de argparse) ...
    parser = argparse.ArgumentParser(description="Servidor de Procesamiento Distribuido")
    parser.add_argument('-i', '--ip', required=True, help="Dirección de escucha (ej: 127.0.0.1)")
    parser.add_argument('-p', '--port', required=True, type=int, help="Puerto de escucha (ej: 8001)")
    parser.add_argument('-n', '--processes', type=int, default=mp.cpu_count(),
                        help=f"Número de procesos en el pool (default: {mp.cpu_count()})")
    
    args = parser.parse_args()
    
    try:
        run_server_b(args.ip, args.port, args.processes)
    except Exception as e:
        print(f"❌ Error fatal al iniciar el Servidor B: {e}", file=sys.stderr)
