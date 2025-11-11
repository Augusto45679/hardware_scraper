from .base_spider import BaseHardwareSpider
from scrapy_playwright.page import PageMethod

class FalabellaSpider(BaseHardwareSpider):
    name = 'falabella'
    allowed_domains = ['falabella.com', 'media.falabella.com']
    start_url_template = 'https://www.falabella.com/falabella-cl/search?Ntt={search_term}'
    
    # Falabella requiere JS y acciones de scroll para cargar productos.
    USE_PLAYWRIGHT = True

    def __init__(self, *args, **kwargs):
        super(FalabellaSpider, self).__init__(*args, **kwargs)
        # Sobrescribimos playwright_meta para añadir acciones de scroll personalizadas.
        self.playwright_meta['playwright_page_methods'] = [
            PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
            PageMethod("wait_for_timeout", 1000),
            PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
            PageMethod("wait_for_timeout", 1000),
            PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
            PageMethod("wait_for_selector", 'a[data-pod="catalyst-pod"]')
        ]

    selectors = {
        'product_container': 'a[data-pod="catalyst-pod"]',
        # El nombre se maneja en parse_product por su complejidad.
        'name_parts': 'b.pod-title::text, b.pod-subTitle::text',
        # Falabella usa 'data-internet-price' para ofertas y 'data-event-price' para precios normales/marketplace.
        # Este selector intenta obtener el primero, y si no existe, busca el segundo.
        'price': 'li[data-internet-price]::attr(data-internet-price), li[data-event-price]::attr(data-event-price)',
        'url': '::attr(href)',
        'next_page': 'button[aria-label="Página siguiente"]:not([disabled])',
    }

    def parse_product(self, product_selector, response):
        """
        Sobrescribe el método base para manejar la extracción del nombre,
        que está compuesto por varias partes en Falabella.
        """
        # Llama al método base para obtener el item con store, currency, price y link.
        item = super().parse_product(product_selector, response)
        
        # Lógica personalizada para el nombre del producto
        title_parts = product_selector.css(self.selectors['name_parts']).getall()
        item['product_name'] = ' '.join(part.strip() for part in title_parts if part.strip())
        
        return item

    def get_next_page(self, response):
        """
        Sobrescribe el método de paginación. Falabella usa un botón y
        la paginación se gestiona añadiendo/incrementando el parámetro 'page' en la URL.
        """
        next_page_button = response.css(self.selectors['next_page'])
        if next_page_button:
            current_page_num = int(response.url.split('page=')[-1]) if 'page=' in response.url else 1
            base_url = response.url.split('?')[0]
            # Construye la URL de la siguiente página
            next_page_url = f"{base_url}?Ntt={self.search_term}&page={current_page_num + 1}"
            return next_page_url
        return None
