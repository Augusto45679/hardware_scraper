# Hardware Scraper 🕷️

Este proyecto es un sistema de web scraping avanzado y escalable desarrollado con **Scrapy** y **Playwright**, diseñado para extraer información detallada de productos de hardware de múltiples tiendas de comercio electrónico en Latinoamérica.

El sistema no solo extrae datos, sino que también procesa, limpia, valida y almacena la información en una base de datos **MongoDB**, gestionando eficientemente las imágenes de los productos mediante **Cloudinary**.

## 🚀 Características Principales

*   **Multi-Spider**: Soporte para múltiples sitios web (`Mercado Libre`, `Compra Gamer`, `Falabella`, `Paris.cl`, `SP Digital`).
*   **Renderizado Dinámico**: Integración con **Playwright** para scrapear sitios que dependen fuertemente de JavaScript.
*   **Pipeline Inteligente de Imágenes**:
    *   Descarga local de imágenes.
    *   Subida automática a **Cloudinary**.
    *   **Deduplicación inteligente**: Evita resubir imágenes ya existentes utilizando hashes de contenido.
*   **Procesamiento de Datos**:
    *   **Limpieza**: Normalización de precios, textos y espacios.
    *   **Validación**: Asegura que los campos críticos (precio, nombre, ID) estén presentes.
    *   **Deduplicación**: Evita duplicados en la base de datos basándose en IDs únicos.
*   **Almacenamiento NoSQL**: Persistencia de datos en **MongoDB** con un esquema flexible.
*   **Configuración Centralizada**: Gestión de credenciales y configuraciones mediante variables de entorno (`.env`).

## 📋 Requisitos Previos

Asegúrate de tener instalado lo siguiente en tu sistema:

*   **Python 3.9+**
*   **MongoDB** (corriendo localmente o una instancia remota)
*   **Cuenta de Cloudinary** (para el almacenamiento de imágenes en la nube)

## 🛠️ Instalación

1.  **Clonar el repositorio:**

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd hardware_scraper
    ```

2.  **Crear y activar un entorno virtual:**

    *   Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instalar dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Instalar navegadores de Playwright:**

    ```bash
    playwright install
    ```

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto (puedes usar `.env.example` como base) y configura las siguientes variables:

```ini
# Configuración de MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=hardware_db
MONGO_COLLECTION=products

# Credenciales de Cloudinary
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

## 🕷️ Spiders Disponibles

El proyecto cuenta con los siguientes spiders en el directorio `hardwareprices/spiders`:

| Spider | Nombre (para ejecutar) | Descripción |
| :--- | :--- | :--- |
| **Mercado Libre** | `mercadolibre` | Busca productos en Mercado Libre (búsqueda general). |
| **Compra Gamer** | `compragamer` | Extrae productos de Compra Gamer (categoría específica). |
| **Falabella** | `falabella` | Scrapea productos de tecnología en Falabella. |
| **Paris.cl** | `pariscl` | Extrae datos de Paris.cl. |
| **SP Digital** | `spdigital` | Scrapea el catálogo de SP Digital. |

## ▶️ Uso

Para ejecutar un spider y guardar los resultados, utiliza el comando `scrapy crawl`.

**Ejemplo básico:**

```bash
scrapy crawl mercadolibre
```

**Guardar salida en JSON:**

```bash
scrapy crawl compragamer -O output.json
```

**Pasar argumentos (si el spider lo soporta):**

```bash
scrapy crawl mercadolibre -a search="rtx 3060"
```

## 📂 Estructura del Proyecto

```text
hardware_scraper/
├── hardwareprices/
│   ├── spiders/           # Definición de los spiders
│   ├── pipelines/         # Lógica de procesamiento (imágenes, mongo, limpieza)
│   ├── items.py           # Definición del modelo de datos
│   ├── settings.py        # Configuración de Scrapy
│   └── middlewares.py     # Middlewares personalizados
├── scraped_images/        # Directorio de descarga local de imágenes
├── scrapy.cfg             # Archivo de configuración de despliegue
├── requirements.txt       # Dependencias del proyecto
└── .env                   # Variables de entorno (no commitear)
```

## 📊 Modelo de Datos

Cada producto extraído se almacena con la siguiente estructura (definida en `items.py`):

*   `product_id`: Hash único del producto.
*   `store_id`: Identificador de la tienda.
*   `product_name`: Título del producto.
*   `price_original`: Precio de lista.
*   `price_current`: Precio actual.
*   `image_url`: URL pública de la imagen (Cloudinary).
*   `specs_normalized`: Especificaciones técnicas procesadas.
*   `scraped_at`: Fecha y hora de la extracción.

## 📝 Pipelines Activos

El orden de procesamiento en `settings.py` es:

1.  `CleaningPipeline`: Limpia espacios y normaliza textos.
2.  `ValidationPipeline`: Descarta items sin precio o nombre.
3.  `DeduplicationPipeline`: Evita procesar el mismo producto dos veces en la misma ejecución.
4.  `CustomImagesPipeline`: Descarga imágenes localmente.
5.  `SmartCloudinaryPipeline`: Sube imágenes a Cloudinary (si no existen ya).
6.  `MongoPipeline`: Guarda el item final en MongoDB.