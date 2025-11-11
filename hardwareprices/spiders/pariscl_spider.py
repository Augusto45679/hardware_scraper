from .base_spider import BaseHardwareSpider
from scrapy_playwright.page import PageMethod

class ParisclSpider(BaseHardwareSpider):
    name = 'pariscl'
    allowed_domains = ['paris.cl']
    start_url_template = 'https://www.paris.cl/search/?q={search_term}'
    
    # Paris.cl carga su contenido con JavaScript.
    USE_PLAYWRIGHT = True

    selectors = {
        'product_container': 'div[role="gridcell"]',
        # Los datos en Paris.cl están en atributos del contenedor principal.
        'name': '::attr(data-cnstrc-item-name)',
        'price': '::attr(data-cnstrc-item-price)',
        'url': 'a::attr(href)',
        'next_page': 'a[data-testid="pagination-next-button"]::attr(href)',
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizamos la espera de Playwright para Paris.cl
        self.playwright_meta['playwright_page_methods'] = [
            PageMethod("wait_for_selector", 'div[data-testid="product-list-grid"]')
        ]
