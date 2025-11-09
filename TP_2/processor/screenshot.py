from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64
import time

# Configuración y generación de screenshot
def generate_screenshot(url: str) -> str:
    chrome_options = Options()
    # Ejecución sin interfaz gráfica para eficiencia
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Manejo de timeouts según el requerimiento (máximo 30 segundos de carga)
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30) 
        
        driver.get(url)
        
        # Captura la imagen como bytes PNG
        png_bytes = driver.get_screenshot_as_png()
        
        # Codifica a Base64 para el JSON de respuesta
        return base64.b64encode(png_bytes).decode('utf-8')
        
    except Exception as e:
        # Manejo de errores de Selenium/Carga de página
        print(f"Error generando screenshot para {url}: {e}")
        return "" # Devuelve cadena vacía si falla la captura
    finally:
        if driver:
            driver.quit() 