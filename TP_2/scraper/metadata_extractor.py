from bs4 import BeautifulSoup
from typing import Dict

# Tags Open Graph y otros que buscamos
META_TAGS_TO_EXTRACT = [
    'description', 
    'keywords', 
    'og:title', 
    'og:description', 
    'og:image',
    'twitter:card',
    'twitter:title'
]

def extract_meta_tags(html_content: str) -> Dict:
    """
    Extrae meta tags relevantes (description, keywords, Open Graph tags).
    """
    soup = BeautifulSoup(html_content, 'lxml')
    meta_tags = {}
    
    # 1. Extraer tags 'name' y 'property'
    for tag in soup.find_all('meta'):
        
        # Buscar por atributo 'name' (description, keywords)
        if tag.get('name') in META_TAGS_TO_EXTRACT:
            key = tag.get('name')
            meta_tags[key] = tag.get('content')
            
        # Buscar por atributo 'property' (Open Graph tags como og:title)
        elif tag.get('property') in META_TAGS_TO_EXTRACT:
            key = tag.get('property')
            meta_tags[key] = tag.get('content')
            
    return meta_tags