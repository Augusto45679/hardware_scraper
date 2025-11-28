import scrapy
from urllib.parse import quote_plus
from datetime import datetime
from hardwareprices.items import HardwarepricesItem
from scrapy_playwright.page import PageMethod

class BaseHardwareSpider(scrapy.Spider):
    """
    Clase base para spiders de hardware.
    Centraliza la lógica común de parsing, paginación y limpieza de datos.
    """
    # Mapeo de categorías a términos de búsqueda. Extensible para nuevos productos.
    CATEGORY_MAPPING = {
        'placas-de-video': 'tarjeta de video',
        'monitores': 'monitor',
        'procesador_intel': 'procesador intel', 'mouse_logitech':'Mouse logitech',
        'teclados':'Teclado', 'fuente_sentey':'fuente sentey', 'procesador_amd': 'procesador AMD',
        'fuente_corsair':'fuente corsair',
    }

    # Configuración personalizada común para todos los spiders que hereden de esta clase.
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'FEEDS': {
            'output.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 4,
            },
        },
    }

    def __init__(self, *args, **kwargs):
        super(BaseHardwareSpider, self).__init__(*args, **kwargs)
        # --- Configuración del Spider ---
        self.start_url_template = getattr(self, 'start_url_template', None)
        self.selectors = getattr(self, 'selectors', {})
        self.item_class = HardwarepricesItem

        # --- Manejo de categoría desde la línea de comandos ---
        self.categoria = kwargs.get('categoria', 'placas-de-video')
        self.search_term = self.CATEGORY_MAPPING.get(self.categoria, 'tarjeta de video')

        # --- Integración con Playwright ---
        self.use_playwright = getattr(self, 'USE_PLAYWRIGHT', False)
        self.playwright_meta = {
            'playwright': True,
            'playwright_page_methods': [
                PageMethod("wait_for_selector", self.selectors.get('product_container', 'body')),
            ],
        } if self.use_playwright else {}

        # --- Validación ---
        if not self.start_url_template:
            raise ValueError("El atributo 'start_url_template' debe ser definido en el spider hijo.")
        if not self.selectors:
            raise ValueError("El diccionario 'selectors' debe ser definido en el spider hijo.")

    def start_requests(self):
        """
        Genera la URL de inicio basada en la categoría y envía la primera petición.
        """
        start_url = self.start_url_template.format(search_term=quote_plus(self.search_term))
        self.logger.info(f"Iniciando scrapeo para la categoría '{self.categoria}' en '{self.name}' con la URL: {start_url}")
        yield scrapy.Request(start_url, callback=self.parse, meta=self.playwright_meta)

    def parse(self, response, **kwargs):
        """
        Método principal de parsing. Itera sobre los productos y gestiona la paginación.
        """
        products = response.css(self.selectors['product_container'])
        self.logger.info(f"Encontrados {len(products)} productos en la página: {response.url}")

        if not products and self.use_playwright:
            self.logger.warning(f"No se encontraron productos en {response.url}. El selector '{self.selectors['product_container']}' podría ser incorrecto o la página no cargó a tiempo.")

        for product_selector in products:
            item = self.parse_product(product_selector, response)
            # Verificamos campos clave antes de hacer yield
            if item.get('product_name') and item.get('price_current'):
                yield item

        # --- Manejo de Paginación ---
        next_page_url = self.get_next_page(response)
        if next_page_url:
            self.logger.info(f"Página siguiente encontrada: {next_page_url}")
            yield scrapy.Request(next_page_url, callback=self.parse, meta=self.playwright_meta)
        else:
            self.logger.info(f"No se encontró página siguiente. Finalizando el spider '{self.name}'.")

    def parse_product(self, product_selector, response):
        """
        Extrae los datos de un único producto usando los selectores definidos.
        """
        item = self.item_class()
        
        # --- Campos Base ---
        item['store_id'] = self.name
        item['store_name'] = self.name.capitalize() # Simple default, puede mejorarse
        item['currency'] = 'ARS' # Default para tiendas argentinas
        item['scraped_at'] = datetime.utcnow().isoformat()
        
        # --- Extracción con Selectores ---
        if 'name' in self.selectors:
            item['product_name'] = product_selector.css(self.selectors['name']).get('').strip()
        
        # Precio: extraemos el string crudo, el pipeline se encarga de limpiar
        price_str = product_selector.css(self.selectors['price']).get()
        item['price_current'] = price_str # Pasamos el string crudo
        # URL
        url_path = product_selector.css(self.selectors['url']).get()
        if url_path:
            item['product_url'] = response.urljoin(url_path)
            
        # --- Campos Opcionales (si los selectores existen) ---
        if 'image' in self.selectors:
            image_url_raw = product_selector.css(self.selectors['image']).get()
            if image_url_raw:
                # Asegurar URL absoluta
                full_image_url = response.urljoin(image_url_raw)
                item['image_url'] = full_image_url
                item['image_urls'] = [full_image_url] # Lista requerida por ImagesPipeline
        
        return item

    def get_next_page(self, response):
        """
        Obtiene la URL de la siguiente página.
        Este método puede ser sobreescrito por los spiders hijos si la lógica es más compleja.
        """
        next_page_selector = self.selectors.get('next_page')
        if not next_page_selector:
            return None
        
        next_page_url = response.css(next_page_selector).get()
        return response.urljoin(next_page_url) if next_page_url else None