# hardware_scraper

Este proyecto es un web scraper desarrollado con el framework [Scrapy](https://scrapy.org/) para extraer información sobre componentes de hardware.

## Requisitos

Asegúrate de tener instalado lo siguiente en tu sistema:
- Python 3.8 o superior
- pip (generalmente viene con Python)

## Instalación y Configuración

Sigue estos pasos para configurar el entorno de desarrollo y poder ejecutar el scraper.

1.  **Clona el repositorio:**

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd hardware_scraper
    ```
    *(Reemplaza `<URL_DEL_REPOSITORIO>` con la URL real de tu repositorio Git)*

2.  **Crea y activa un entorno virtual:**

    Es una buena práctica usar un entorno virtual para aislar las dependencias del proyecto y evitar conflictos con otros proyectos.

    *   **En Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

    *   **En macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    Verás `(venv)` al principio de la línea de tu terminal, indicando que el entorno está activo.

3.  **Instala las dependencias:**

    Con el entorno virtual activado, instala todas las librerías necesarias que se encuentran en el archivo `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```
4.  **Instala Playwright y sus navegadores:**

    Este proyecto utiliza `scrapy-playwright` para interactuar con páginas web dinámicas. Necesitas instalarlo y luego descargar los navegadores que utiliza.

    ```bash
    # Instala la librería de integración
    pip install scrapy-playwright
    # Descarga e instala los navegadores (Chromium, Firefox, WebKit)
    playwright install
    ```

## ¿Cómo ejecutar el Scraper?

Una vez que la configuración esté completa, puedes ejecutar el scraper desde el directorio raíz del proyecto con el siguiente comando:

```bash
scrapy crawl <nombre_del_spider> -O output.csv
```

*   Reemplaza `<nombre_del_spider>` con el nombre real de tu spider (definido dentro de la clase de tu spider, ej: `name = 'mi_spider'`).
*   La opción `-O output.csv` guardará los datos extraídos en un archivo llamado `output.csv`. Puedes cambiar el formato a `json`, `xml`, etc., y también el nombre del archivo.
