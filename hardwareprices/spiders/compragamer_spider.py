from .base_spider import BaseHardwareSpider

class CompragamerSpider(BaseHardwareSpider):
    name = 'compragamer'
    allowed_domains = ['compragamer.com']
    
    # Plantilla de URL. {search_term} será reemplazado por la categoría.
    # La paginación se maneja con el parámetro 'page'.
    start_url_template = 'https://compragamer.com/productos?criterio={search_term}&page=1'
    
    # Se requiere Playwright porque el contenido se carga dinámicamente.
    USE_PLAYWRIGHT = True

    # Diccionario de selectores CSS específicos para compragamer.com
    selectors = {
        'product_container': 'cgw-product-card',
        'name': 'h3.product-card__title::text',
        'price': 'span.txt_price::text',
        'url': 'a.product-card::attr(href)',
        'next_page': 'a.page-link[rel="next"]::attr(href)', # Selector para el botón "siguiente"
    }

    def get_next_page(self, response):
        """
        CompraGamer no tiene un botón "siguiente" estándar, sino que la paginación
        se basa en si se encuentran productos. Si no hay productos, se detiene.
        """
        if not response.css(self.selectors['product_container']):
            return None # No hay productos, fin de la paginación.
        return super().get_next_page(response)