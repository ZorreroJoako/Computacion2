import aiohttp
import asyncio
from aiohttp import ClientTimeout

# Timeout de 30 segundos
SCRAPING_TIMEOUT = 30 

async def fetch_url(url: str) -> str:
    """
    Realiza una petición GET asíncrona a la URL y devuelve el contenido HTML.
    Maneja el timeout y errores básicos.
    """
    # Usamos un ClientTimeout con el límite de 30s
    timeout = ClientTimeout(total=SCRAPING_TIMEOUT)
    
    # Creamos una sesión dentro de la función (o idealmente se pasa una sesión compartida)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            # Usamos `skip_auto_headers` para simplificar, se puede añadir un User-Agent
            async with session.get(url, allow_redirects=True) as response:
                
                # Manejo de códigos de estado HTTP (4xx, 5xx)
                if response.status >= 400:
                    response.raise_for_status()
                
                # Leemos el contenido como texto (HTML)
                # Limitamos el tamaño para evitar problemas de memoria en páginas gigantes
                html_content = await response.text()
                return html_content
                
        except asyncio.TimeoutError:
            # Captura específica del timeout asíncrono
            raise asyncio.TimeoutError(f"Scraping timeout ({SCRAPING_TIMEOUT}s) for {url}")
        except aiohttp.ClientError as e:
            # Captura otros errores de red o HTTP (conexión rechazada, DNS, etc.)
            raise ConnectionError(f"Network or HTTP error for {url}: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error during fetch: {e}")