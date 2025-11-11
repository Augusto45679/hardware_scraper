from .base_spider import BaseHardwareSpider
from scrapy_playwright.page import PageMethod

class SpdigitalSpider(BaseHardwareSpider):
    name = 'spdigital'
    allowed_domains = ['spdigital.cl']
    start_url_template = 'https://www.spdigital.cl/search/?q={search_term}&page=1'

    # SPDigital requiere JS para cargar los productos.
    USE_PLAYWRIGHT = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizamos la espera de Playwright para SPDigital.
        self.playwright_meta['playwright_page_methods'] = [
            PageMethod("wait_for_selector", 'div.Fractal-ProductCard__productcard--container')
        ]

    selectors = {
        'product_container': 'div.Fractal-ProductCard__productcard--container',
        # El nombre se construye a partir de dos partes, se maneja en parse_product.
        'brand': 'div.Fractal-ProductCard--productDetailsContainer > span a::text',
        'description': 'div.Fractal-ProductCard--productDescriptionTextContainer span a::text',
        'price': 'span[data-fractalds*="best-price,primary"]::text',
        'url': 'a.Fractal-ProductCard--image::attr(href)',
        # No hay un botón "siguiente", la paginación se maneja en get_next_page.
    }

    def parse_product(self, product_selector, response):
        """
        Sobrescribe el método base para construir el nombre del producto
        a partir de la marca y la descripción.
        """
        item = super().parse_product(product_selector, response)

        # Lógica personalizada para el nombre del producto
        brand = product_selector.css(self.selectors['brand']).get('').strip()
        description = product_selector.css(self.selectors['description']).get('').strip()
        item['product_name'] = f"{brand} {description}".strip()
        
        return item

    def get_next_page(self, response):
        """
        Sobrescribe el método de paginación. SPDigital no tiene un botón "siguiente",
        por lo que se incrementa el número de página en la URL hasta que no haya más productos.
        """
        if not response.css(self.selectors['product_container']):
            return None # No hay productos, fin de la paginación.
        
        current_page_num = int(response.url.split('page=')[-1]) if 'page=' in response.url else 1
        next_page_url = f"https://www.spdigital.cl/search/?q={self.search_term}&page={current_page_num + 1}"
        return next_page_url