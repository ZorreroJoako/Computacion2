from bs4 import BeautifulSoup
from typing import Dict, List

def scrape_html_content(html_content: str) -> Dict:
    """
    Extrae el título, enlaces, conteo de imágenes y estructura de encabezados 
    (H1-H6) del contenido HTML.
    """
    # Usamos 'lxml' si está instalado para un parsing más rápido
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 1. Título de la página
    title = soup.title.string if soup.title else "No Title Found"
    
    # 2. Todos los enlaces (links) encontrados
    # Aseguramos que el atributo 'href' exista y sea no vacío
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].strip()]
    
    # 3. Cantidad de imágenes en la página
    images_count = len(soup.find_all('img'))
    
    # 4. Estructura básica (cantidad de headers H1-H6)
    structure = {}
    for i in range(1, 7):
        tag = f'h{i}'
        structure[tag] = len(soup.find_all(tag))
        
    return {
        "title": title,
        "links": links,
        "structure": structure,
        "images_count": images_count
    }