from .base_spider import BaseHardwareSpider
import scrapy

class MercadolibreSpider(BaseHardwareSpider):
    name = 'mercadolibre'
    allowed_domains = ['mercadolibre.com.ar']
    start_url_template = 'https://listado.mercadolibre.com.ar/{search_term}'
    USE_PLAYWRIGHT = False

    selectors = {
        # selector del contenedor: cada <li> dentro del ol de resultados
        'product_container': 'ol.ui-search-layout.ui-search-layout--grid li.ui-search-layout__item',
        # título / nombre (clase observada en tu captura)
        'name': 'a.poly-component__title::text',
        # url del producto (link del título)
        'url': 'a.poly-component__title::attr(href)',
        # precio preferido y alternativa (por A/B / variaciones)
        'price': 'div.poly-component__price span.andes-money-amount__fraction::text',
        'price_alt': 'div.ui-search-price__second-line span.andes-money-amount__fraction::text',
        'currency': 'span.andes-money-amount__currency-symbol::text',
        # paginación (si no funciona ajustamos según el HTML real)
        'next_page': 'li.andes-pagination__button--next a::attr(href)',
    }

    def start_requests(self):
        formatted_search_term = self.search_term.replace(' ', '-')
        start_url = self.start_url_template.format(search_term=formatted_search_term)
        self.logger.info(f"Iniciando scrapeo para la categoría '{self.categoria}' en '{self.name}' con la URL: {start_url}")
        yield scrapy.Request(start_url, callback=self.parse, meta=self.playwright_meta)

    def parse_product(self, product_selector, response):
        """
        Usamos la extracción base y añadimos robustez: 
        - fallback para price
        - fallback para nombre
        - limpieza de link y moneda
        """
        item = super().parse_product(product_selector, response)

        # Si base no encontró precio, intentamos alternativa
        if not item.get('price'):
            alt = product_selector.css(self.selectors.get('price_alt', '')).get()
            if alt:
                item['price'] = self._clean_price(alt)

        # Si base no encontró name, intentamos alternativas observadas
        if not item.get('product_name'):
            alt_name = product_selector.css('h3.poly-component__title-wrapper a::text').get() \
                    or product_selector.css('a::text').get()
            if alt_name:
                item['product_name'] = alt_name.strip()

        # Moneda (si aparece)
        cur = product_selector.css(self.selectors.get('currency', '')).get()
        if cur:
            item['currency'] = cur.strip()

        # Limpieza de link (quita tracking después de #)
        if item.get('link'):
            item['link'] = item['link'].split('#')[0].strip()

        return item
