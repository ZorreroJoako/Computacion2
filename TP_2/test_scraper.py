import asyncio
import aiohttp
import json
import sys

# Dirección donde corre el Servidor A
SERVER_A_URL = 'http://127.0.0.1:8080' 
URL_TEST_SUCCESS = 'https://www.example.com' 
URL_TEST_TIMEOUT = 'http://example.com:81' # Usar un puerto cerrado para forzar error de conexión o timeout

async def test_scraper_success():
    """Prueba de integración de punta a punta con una URL válida."""
    print(f"\n--- Test 1: Éxito de Integración con {URL_TEST_SUCCESS} ---")
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300)) as session:
        try:
            full_url = f"{SERVER_A_URL}/scrape?url={URL_TEST_SUCCESS}"
            async with session.get(full_url) as resp:
                data = await resp.json()
                
                # Criterios de éxito
                assert resp.status == 200, f"Status Code inesperado: {resp.status}"
                assert data['status'] == 'success', f"El estado no fue 'success': {data['status']}"
                assert 'scraping_data' in data, "Falta la clave 'scraping_data'."
                assert 'processing_data' in data, "Falta la clave 'processing_data'."
                assert data['scraping_data']['title'] == 'Example Domain', "Título scrapeado incorrecto."
                
                print("✅ TEST 1 PASSED: Datos de Scraping y Procesamiento recibidos con éxito.")
                
        except Exception as e:
            print(f"❌ TEST 1 FAILED: Error inesperado: {e}")

async def test_scraper_network_failure():
    """Prueba el manejo de errores de conexión/red con Servidor A."""
    print(f"\n--- Test 2: Manejo de Fallo de Conexión (URL Inválida) ---")
    
    # Esta URL no existe, forzará un ConnectionError en fetch_url
    url_invalid = "http://definitivamente-un-dominio-invalido-12345.com" 
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        try:
            full_url = f"{SERVER_A_URL}/scrape?url={url_invalid}"
            async with session.get(full_url) as resp:
                data = await resp.json()
                
                # Esperamos un error 502 (Bad Gateway) o 500
                assert resp.status in (502, 500), f"Status Code esperado 500/502, recibido: {resp.status}"
                assert 'error' in data['message'].lower() or 'failed' in data['message'].lower(), "Mensaje de error no claro."
                
                print("✅ TEST 2 PASSED: Servidor A manejó correctamente la URL inaccesible.")
                
        except Exception as e:
            print(f"❌ TEST 2 FAILED: Error inesperado: {e}")

async def run_tests():
    # Ejecutar las pruebas secuencialmente
    await test_scraper_success()
    await test_scraper_network_failure()


if __name__ == '__main__':
    # Verificar si el Servidor A está levantado antes de empezar
    print("Iniciando suite de tests. Asegúrese de que ambos servidores estén corriendo.")
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\nTests detenidos.")
    except Exception as e:
        print(f"Error fatal al correr el suite de tests: {e}")