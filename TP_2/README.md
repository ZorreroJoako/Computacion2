# TP2 - Sistema de Scraping y Análisis Web Distribuido
Alumno:Zorrero Joaquín
Carrera:Ingeniería En Computación
## 📜 Descripción del Proyecto

Este proyecto implementa un sistema distribuido de dos servidores en Python para realizar **scraping web asíncrono** y **procesamiento paralelo (CPU-bound)**, cumpliendo con los requerimientos de la asignatura Computación II.

El sistema se compone de:
1.  **Servidor A (`server_scraping.py`):** Interfaz pública que gestiona peticiones I/O-bound (`asyncio` + `aiohttp`) y coordina de forma asíncrona el trabajo del Servidor B.
2.  **Servidor B (`server_processing.py`):** Motor de procesamiento que ejecuta tareas pesadas (screenshots, análisis de rendimiento) en paralelo utilizando un pool de procesos (`multiprocessing`).

### Transparencia para el Cliente (Parte C)
El cliente final solo interactúa con el Servidor A. La comunicación por sockets y el procesamiento del Servidor B son completamente transparentes para el usuario.

---

## ✅ Requisitos Técnicos Clave

| Requisito del TP | Implementación Clave |
| :--- | :--- |
| **Programación Asíncrona** | Uso de `asyncio` y `aiohttp` en Servidor A. Comunicación socket Servidor A → Servidor B es **no bloqueante**. |
| **Programación Paralela** | Uso de `multiprocessing.Pool` en Servidor B para tareas de *screenshot*, *performance* y *thumbnails*. |
| **Protocolo de Comunicación** | Comunicación TCP entre servidores con protocolo de **longitud (4 bytes)** + **datos JSON** serializados. |
| **Funciones Mínimas** | Scraping, Metadatos, Generación de Screenshot (`selenium`), Análisis de Rendimiento (`selenium`). |
| **Manejo de Errores** | Manejo de `asyncio.TimeoutError` (30s) en scraping y `ConnectionRefusedError` en sockets. |
| **Interfaz CLI** | Ambos servidores implementan `argparse` para IP, Puerto y configuración de concurrencia. |

---

## ⚙️ Instalación y Dependencias

Para ejecutar el proyecto, se requiere Python 3.8+ y las siguientes librerías:

1. Entorno Virtual e Instalación de Librerías

Accede a la carpeta raíz del proyecto (`TP2/`) e inicia el entorno virtual:

```bash
# Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Linux/macOS
# o venv\Scripts\activate.bat en Windows

# Instalar todas las dependencias
pip install -r requirements.txt

2.  **Configurar WebDriver:**
    El sistema utiliza **Selenium** para capturas y análisis. Debe tener un **WebDriver** (como **ChromeDriver** o **GeckoDriver**) instalado en el sistema y accesible desde el `PATH` del sistema operativo.

---

## ▶️ Instrucciones de Ejecución

El sistema debe iniciarse en orden (Servidor B, luego Servidor A) antes de ejecutar el cliente.

### Instrucciones de Inicio

```bash
# PASO 1: Iniciar Servidor B (Procesamiento) - 🟡 Terminal 1
# Este servidor escucha en 8001 y gestiona la carga CPU-bound.
python3 server_processing.py -i 127.0.0.1 -p 8001 -n 4

# PASO 2: Iniciar Servidor A (Scraping y Coordinación) - 🟢 Terminal 2
# Este servidor escucha en 8080 y se conecta al Servidor B en 8001.
python3 server_scraping.py -i 127.0.0.1 -p 8080 --processor-ip 127.0.0.1 --processor-port 8001

# PASO 3: Ejecutar Cliente de Prueba - 🔵 Terminal 3
# El cliente simula una petición al Servidor A.
python3 client.py https://www.google.com.ar

Para IPv6 debe usarse el formato \[<dirección IPv6>\]
# PASO 1: Iniciar Servidor B (Procesamiento) - 🟡 Terminal 1
python3 server_processing.py -i :: -p 8002 -n 4

# PASO 2: Iniciar Servidor A (Scraping y Coordinación) - 🟢 Terminal 2
python3 server_scraping.py -i :: -p 8001 --processor-ip :: --processor-port 8002
# PASO 3: Ejecutar Cliente de Prueba - 🔵 Terminal 3
python3 client.py https://google.com --ip \[::\] --port 8001
