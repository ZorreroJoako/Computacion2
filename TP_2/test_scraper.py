import asyncio
import aiohttp
import json
import sys

# Dirección base del Servidor A (usada para IPv4)
SERVER_A_URL_V4 = 'http://127.0.0.1:8080' 
SERVER_A_URL_V6 = 'http://[::1]:8080' # Dirección IPv6 (debe usar corchetes)
URL_TEST_SUCCESS = 'https://www.example.com' 

# iniciados en modo IPv6 (python3 server_scraping.py -i ::1 -p 8080 ...)

async def test_scraper_success(url_base: str, protocol: str):
    """Prueba de integración de punta a punta con una URL válida."""
    print(f"\n--- Test 1: Éxito de Integración ({protocol}) ---")
    
    # Timeout total para el procesamiento en Servidor B
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
        try:
            full_url = f"{url_base}/scrape?url={URL_TEST_SUCCESS}"
            print(f"  > Conectando a: {full_url}")
            
            async with session.get(full_url) as resp:
                data = await resp.json()
                
                # Criterios de éxito
                assert resp.status == 200, f"Status Code inesperado: {resp.status}"
                assert data.get('status') == 'success', f"El estado no fue 'success': {data.get('status')}"
                assert 'scraping_data' in data, "Falta la clave 'scraping_data'."
                assert 'processing_data' in data, "Falta la clave 'processing_data'."
                assert data['scraping_data']['title'] == 'Example Domain', "Título scrapeado incorrecto."
                
                print(f"✅ TEST 1 PASSED ({protocol}): Datos recibidos con éxito.")
                
        except Exception as e:
            print(f"❌ TEST 1 FAILED ({protocol}): Error inesperado: {e}")

async def test_scraper_network_failure():
    """Prueba el manejo de errores de conexión/red con Servidor A (usando IPv4 base)."""
    print(f"\n--- Test 2: Manejo de Fallo de Conexión (URL Inválida) ---")
    
    # Esta URL no existe, forzará un ConnectionError en fetch_url
    url_invalid = "http://definitivamente-un-dominio-invalido-12345.com" 
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            full_url = f"{SERVER_A_URL_V4}/scrape?url={url_invalid}"
            async with session.get(full_url) as resp:
                data = await resp.json()
                
                # Esperamos un error 502 (Bad Gateway) o 500
                assert resp.status in (502, 500), f"Status Code esperado 500/502, recibido: {resp.status}"
                assert 'error' in data['message'].lower() or 'failed' in data['message'].lower(), "Mensaje de error no claro."
                
                print("✅ TEST 2 PASSED: Servidor A manejó correctamente la URL inaccesible.")
                
        except Exception as e:
            print(f"❌ TEST 2 FAILED: Error inesperado: {e}")

async def run_tests():
    # --- PRUEBA IPv4 (Asume servidores en 127.0.0.1) ---
    await test_scraper_success(SERVER_A_URL_V4, "IPv4")
    
    # --- PRUEBA IPv6 (Requiere que los servidores estén iniciados en ::1) ---
    # Nota: Es crucial que los servidores A y B estén iniciados con -i ::1 
    # antes de ejecutar esta parte.
    print("\n--- Preparando Test IPv6 ---")
    await test_scraper_success(SERVER_A_URL_V6, "IPv6")
    
    # Prueba de falla de red (usamos IPv4 base ya que la prueba de éxito cubre IPv6)
    await test_scraper_network_failure()


if __name__ == '__main__':
    print("Iniciando suite de tests. Asegúrese de que el Servidor A y B estén corriendo en las direcciones correctas.")
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\nTests detenidos.")
    except Exception as e:
        print(f"Error fatal al correr el suite de tests: {e}")
