import aiohttpimport aiohttpimport aiohttp
import asyncio
import sys
import json
import argparse
import ipaddress 

# Configuración del Servidor A 
SERVER_A_IP = '127.0.0.1'
SERVER_A_PORT = 8080 
DEFAULT_URL = 'https://www.example.com'

# --- FUNCIÓN DE FORMATO IP (SOPORTE IPv6) ---
def format_host(ip: str) -> str:
    """
    Envuelve la IP entre corchetes si es IPv6 (ej. [::1]), 
    que es requerido por el estándar de URL HTTP.
    """
    try:
        if ipaddress.ip_address(ip).version == 6:
            return f'[{ip}]'
        return ip
    except ValueError:
        return ip
# ---------------------------------------------

async def run_client(target_url: str, ip: str, port: int):
    """
    Realiza una petición GET asíncrona al Servidor A con la URL de destino.
    """
    
    # *** CORRECCIÓN: Aplicar el formato IP antes de construir la URL ***
    host_formatted = format_host(ip) 
    server_a_url = f'http://{host_formatted}:{port}/scrape?url={target_url}'
    # ------------------------------------------------------------------
    
    print(f"--- 🚀 INICIANDO PRUEBA ---")
    print(f"Objetivo: {target_url}")
    print(f"Conectando a Servidor A en: {server_a_url}")
    
    # Timeout total alto (ej. 10 minutos)
    timeout_config = aiohttp.ClientTimeout(total=600) 
    
    async with aiohttp.ClientSession(timeout=timeout_config) as session:
        try:
            async with session.get(server_a_url) as resp:
                
                print(f"Status HTTP recibido de Servidor A: {resp.status}")
                
                data = await resp.json()
                
                if resp.status == 200 and data.get('status') in ('success', 'partial_success'):
                    print("\n✅ ÉXITO DE INTEGRACIÓN:")
                    print(f"Status Consolidado: **{data.get('status')}**")
                    print(f"Título Scrapeado: **{data['scraping_data']['title']}**")
                    
                    if 'screenshot' in data['processing_data'] and data['processing_data']['screenshot']:
                        print(f"Resultado B (Screenshot): **Recibido ({len(data['processing_data']['screenshot'])} bytes Base64)**")
                    else:
                        print("Resultado B (Screenshot): ⚠️ No recibido o fallido.")

                    print(f"Tiempo de Carga Reportado: **{data['processing_data']['performance'].get('load_time_ms', 'N/A')} ms**")
                    
                    print("\n--- Respuesta JSON Completa ---")
                    print(json.dumps(data, indent=4, ensure_ascii=False))
                    
                else:
                    print(f"\n❌ FALLO EN EL PROCESO: {data.get('message', 'Verificar logs.')}")
                    print(json.dumps(data, indent=4, ensure_ascii=False))

        except ConnectionRefusedError:
            print(f"❌ ERROR: Conexión rechazada. Asegúrate de que **Servidor A** esté corriendo en {ip}:{port}.")
        except asyncio.TimeoutError:
            print("❌ ERROR: Timeout. La petición superó los 10 minutos. Revisa el Servidor B.")
        except Exception as e:
            print(f"❌ ERROR INESPERADO del cliente: {e}")

def main():
    parser = argparse.ArgumentParser(description="Cliente de prueba para el sistema de Scraping Distribuido.")
    
    parser.add_argument('url', nargs='?', default=DEFAULT_URL, help=f'URL a scrapear (default: {DEFAULT_URL})')
    parser.add_argument('--ip', type=str, default=SERVER_A_IP, help=f'IP del Servidor A (default: {SERVER_A_IP})')
    parser.add_argument('--port', type=int, default=SERVER_A_PORT, help=f'Puerto del Servidor A (default: {SERVER_A_PORT})')

    args = parser.parse_args()
    
    try:
        asyncio.run(run_client(args.url, args.ip, args.port))
    except KeyboardInterrupt:
        print("\nCliente detenido.")

if __name__ == '__main__':
    main()
