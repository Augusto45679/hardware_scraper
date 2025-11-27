# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HardwarepricesItem(scrapy.Item):
    # --- Identificadores ---
    product_id = scrapy.Field()      # Hash único del producto (generado internamente)
    store_id = scrapy.Field()        # Identificador de la tienda (e.g., 'compragamer')
    store_name = scrapy.Field()      # Nombre legible de la tienda
    external_id = scrapy.Field()     # ID del producto en la tienda (SKU/ID externo)
    
    # --- Información del Producto ---
    product_name = scrapy.Field()    # Título original
    brand = scrapy.Field()           # Marca normalizada
    model = scrapy.Field()           # Modelo específico
    category = scrapy.Field()        # Categoría normalizada
    subcategory = scrapy.Field()     # Subcategoría (opcional)
    specs_raw = scrapy.Field()       # Diccionario con specs crudas
    specs_normalized = scrapy.Field() # Diccionario con specs normalizadas
    
    # --- Precios y Disponibilidad ---
    price_original = scrapy.Field()  # Precio de lista (sin descuento)
    price_current = scrapy.Field()   # Precio actual de venta
    currency = scrapy.Field()        # Moneda (ARS, USD)
    discount_percentage = scrapy.Field() # Porcentaje de descuento calculado
    availability = scrapy.Field()    # 'in_stock', 'out_of_stock', 'preorder'
    shipping_cost = scrapy.Field()   # Costo de envío (si está disponible)
    
    # --- Metadata ---
    product_url = scrapy.Field()     # URL del producto
    image_url = scrapy.Field()       # URL de la imagen principal
    image_urls = scrapy.Field()      # Lista de URLs para el ImagesPipeline
    images = scrapy.Field()          # Resultados de la descarga (path, checksum, etc.)
    image_path = scrapy.Field()      # Ruta local de la imagen (calculada o extraída)
    rating = scrapy.Field()          # Puntuación (si existe)
    reviews_count = scrapy.Field()   # Cantidad de reviews
    
    # --- Auditoría ---
    scraped_at = scrapy.Field()      # Fecha y hora del scrape (UTC)
    last_seen_at = scrapy.Field()    # Fecha de la última vez que se vio (para histórico)
    content_hash = scrapy.Field()    # Hash del contenido para detectar cambios

