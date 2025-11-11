import argparse
import asyncio
import logging
import datetime
import struct
import json
import aiohttp
from aiohttp import web, ClientSession

# --- 1. Utilidades de Protocolo (Normalmente en common/protocol.py y common/serialization.py) ---

HEADER_SIZE = 4 # 4 bytes para el tamaño del mensaje

def serialize_data(data: dict) -> bytes:
    """Serializa un diccionario a bytes usando JSON."""
    return json.dumps(data).encode('utf-8')

def deserialize_data(data_bytes: bytes) -> dict:
    """Deserializa bytes a un diccionario Python."""
    return json.loads(data_bytes.decode('utf-8'))

def encode_message(data: dict) -> bytes:
    """Codifica datos en el formato: | longitud (4 bytes) | datos serializados |"""
    serialized = serialize_data(data)
    header = struct.pack('<I', len(serialized)) 
    return header + serialized

def decode_header(header_bytes: bytes) -> int:
    """Decodifica la longitud del mensaje del encabezado de 4 bytes."""
    return struct.unpack('<I', header_bytes)[0]

# --- 2. Funciones de Scraping (Normalmente en scraper/) ---

from bs4 import BeautifulSoup
from typing import Dict, List

# Requisito de Timeout de 30 segundos
SCRAPING_TIMEOUT = 30 

# Importamos aiohttp para el fetch
from aiohttp import ClientTimeout

async def fetch_url(url: str) -> str:
    """Realiza una petición GET asíncrona a la URL y devuelve el contenido HTML."""
    timeout = ClientTimeout(total=SCRAPING_TIMEOUT)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url, allow_redirects=True) as response:
                if response.status >= 400:
                    response.raise_for_status()
                html_content = await response.text()
                return html_content
                
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Scraping timeout ({SCRAPING_TIMEOUT}s) for {url}")
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Network or HTTP error for {url}: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error during fetch: {e}")


def scrape_html_content(html_content: str) -> Dict:
    """Extrae el título, enlaces, conteo y URLs de imágenes, y estructura de encabezados."""
    soup = BeautifulSoup(html_content, 'lxml')
    
    title = soup.title.string if soup.title else "No Title Found"
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].strip()]
    
    # Extracción de imágenes
    images = soup.find_all('img', src=True)
    images_count = len(images)
    image_urls = [img['src'] for img in images] 
    
    # Estructura de encabezados
    structure = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
        
    return {
        "title": title,
        "links": links,
        "structure": structure,
        "images_count": images_count,
        "image_urls": image_urls # Importante para Servidor B
    }

def extract_meta_tags(html_content: str) -> Dict:
    """Extrae meta tags relevantes."""
    soup = BeautifulSoup(html_content, 'lxml')
    meta_tags = {}
    
    tags_to_extract = ['description', 'keywords', 'og:title', 'og:description', 'og:image']

    for tag in soup.find_all('meta'):
        name = tag.get('name')
        prop = tag.get('property')
        
        if name in tags_to_extract:
            meta_tags[name] = tag.get('content')
        elif prop in tags_to_extract:
            meta_tags[prop] = tag.get('content')
            
    return meta_tags

# --- 3. Comunicación Asíncrona con Servidor B ---

async def communicate_with_processor(data_to_send: dict, processor_ip: str, processor_port: int) -> dict:
    """Envía datos al Servidor B y espera la respuesta del pool de multiprocessing."""
    reader = writer = None
    try:
        # Abre la conexión asíncrona
        reader, writer = await asyncio.open_connection(processor_ip, processor_port)
        
        # Envío del mensaje serializado con encabezado de longitud
        message = encode_message(data_to_send)
        writer.write(message)
        await writer.drain()

        # Lectura del encabezado de respuesta (Timeout largo para el procesamiento)
        header_bytes = await asyncio.wait_for(reader.readexactly(HEADER_SIZE), timeout=300)
        msg_len = decode_header(header_bytes)

        # Lectura del cuerpo de la respuesta
        data_bytes = await asyncio.wait_for(reader.readexactly(msg_len), timeout=300)
        result = deserialize_data(data_bytes)
        
        return result

    except asyncio.TimeoutError:
        error_msg = "Timeout esperando respuesta del Servidor B."
        logging.error(f"Comunication Error: {error_msg}")
        return {"status": "error", "message": error_msg}
    except ConnectionRefusedError:
        error_msg = f"Conexión rechazada al Servidor B en {processor_ip}:{processor_port}."
        logging.error(f"Comunication Error: {error_msg}")
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Fallo de comunicación/protocolo con Servidor B: {e}"
        logging.error(f"Comunication Error: {error_msg}")
        return {"status": "error", "message": error_msg}
    finally:
        if writer:
            writer.close()
            # Esperar el cierre es buena práctica en asyncio
            await writer.wait_closed() 

# --- 4. Handler Principal (Ruta /scrape) ---

async def handle_scrape(request):
    """Manejador principal: GET /scrape?url=..."""
    target_url = request.query.get('url')
    
    if not target_url:
        return web.json_response({'status': 'error', 'message': 'Missing "url" query parameter.'}, status=400)
    
    logging.info(f"Processing URL: {target_url}")

    # Obtener configuración de la aplicación
    processor_ip = request.app['processor_ip']
    processor_port = request.app['processor_port']

    scraping_data = {}
    processing_data = {}
    content_data = {}
    
    # --- A. Scraping y Extracción (Asíncrono, I/O-Bound) ---
    try:
        html_content = await fetch_url(target_url) 
        content_data = scrape_html_content(html_content)
        meta_data = extract_meta_tags(html_content)
        
        scraping_data = {
            "title": content_data["title"],
            "links": content_data["links"],
            "meta_tags": meta_data,
            "structure": content_data["structure"],
            "images_count": content_data["images_count"]
        }

    except asyncio.TimeoutError:
        return web.json_response({'status': 'error', 'message': 'Scraping request timed out (30s).'}, status=504)
    except ConnectionError as e:
        return web.json_response({'status': 'error', 'message': f'Network error during scraping: {e}'}, status=502)
    except Exception as e:
        return web.json_response({'status': 'error', 'message': f'Scraping failed: {e}'}, status=500)
    
    # --- B. Coordinación con Servidor B (CPU-Bound) ---
    
    data_to_send = {
        'url': target_url,
        'image_urls': content_data.get('image_urls', []) 
    }

    processing_result = await communicate_with_processor(data_to_send, processor_ip, processor_port)
    
    if processing_result.get('error'):
        processing_data = {"error": processing_result.get('error')}
        final_status = "partial_success"
    else:
        processing_data = processing_result
        final_status = "success"

    # --- C. Consolidación de Respuesta (Transparencia para el Cliente) ---
    response = {
        "url": target_url,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "scraping_data": scraping_data,
        "processing_data": processing_data,
        "status": final_status
    }

    logging.info(f"Finished processing for {target_url}. Status: {final_status}")
    return web.json_response(response)

# --- 5. Función de Inicio y CLI ---

def main():
    parser = argparse.ArgumentParser(description="Servidor de Scraping Web Asíncrono")
    
    # Argumentos para el Servidor A (Requerimiento)
    parser.add_argument('-i', '--ip', type=str, required=True, help="Dirección de escucha (soporta IPv4/IPv6)")
    parser.add_argument('-p', '--port', type=int, required=True, help="Puerto de escucha")
    parser.add_argument('-w', '--workers', type=int, default=1, help="Número de workers (default: 1)") # aiohttp workers

    # Argumentos para el Servidor B (Coordinación)
    parser.add_argument('--processor-ip', type=str, default='127.0.0.1', help='IP del Servidor B (default: 127.0.0.1)')
    parser.add_argument('--processor-port', type=int, default=8001, help='Puerto del Servidor B (default: 8001)')

    args = parser.parse_args()

    app = web.Application()
    
    app['processor_ip'] = args.processor_ip
    app['processor_port'] = args.processor_port
    
    app.add_routes([
        web.get('/scrape', handle_scrape),
    ])

    logging.info(f"Starting Server A on {args.ip}:{args.port}")
    logging.info(f"Configured to use Servidor B at: {args.processor_ip}:{args.processor_port}")
    
    # Iniciamos el servidor, usando el argumento workers
    web.run_app(app, host=args.ip, port=args.port, workers=args.workers) 

if __name__ == '__main__':
    # Configuración básica de logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    main()
