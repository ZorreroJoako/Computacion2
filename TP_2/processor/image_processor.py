from PIL import Image
import requests
import io
import base64
from typing import List, Dict

# Definición del tamaño del thumbnail requerido
THUMBNAIL_SIZE = (150, 150)
MAX_IMAGES_TO_PROCESS = 5 # Límite para evitar sobrecarga en el pool de procesos

def generate_thumbnail_b64(image_data: bytes) -> str:
    """
    Toma los bytes de una imagen, genera un thumbnail optimizado (JPEG) 
    y lo devuelve codificado en Base64.
    """
    try:
        # Abrir la imagen desde bytes en memoria
        img = Image.open(io.BytesIO(image_data))
        
        # Redimensionar la imagen para crear el thumbnail (CPU-bound)
        img.thumbnail(THUMBNAIL_SIZE)
        
        # Guardar el thumbnail en un buffer de memoria como JPEG optimizado
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=75) # Calidad 75 es un buen balance
        
        # Codificar los bytes del thumbnail a Base64
        return base64.b64encode(output.getvalue()).decode('utf-8')
        
    except Exception as e:
        # Manejo de errores de formato de imagen (no es una imagen válida, etc.)
        print(f"Error procesando imagen con Pillow: {e}")
        return ""

def process_images(image_urls: List[str]) -> List[str]:
    """
    Descarga un número limitado de imágenes y genera sus thumbnails.
    """
    thumbnail_b64_list = []
    
    # Iterar solo sobre un subconjunto limitado de URLs para ser robustos
    for url in image_urls[:MAX_IMAGES_TO_PROCESS]: 
        if not url.startswith(('http://', 'https://')):
            continue # Ignorar URLs relativas o inválidas aquí
            
        try:
            # **1. Descarga de la imagen (I/O bloqueante)**
            # Timeout de 10 segundos por imagen
            response = requests.get(url, timeout=10) 
            
            # Verificar el tipo de contenido y el código de estado
            if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                
                # **2. Procesamiento y Codificación**
                thumb = generate_thumbnail_b64(response.content)
                
                if thumb:
                    thumbnail_b64_list.append(thumb)
            
        except requests.exceptions.Timeout:
            print(f"Timeout al descargar la imagen: {url}")
        except Exception as e:
            # Incluye errores de conexión, DNS, etc.
            print(f"Fallo general al descargar/procesar {url}: {e}")
            
    return thumbnail_b64_list