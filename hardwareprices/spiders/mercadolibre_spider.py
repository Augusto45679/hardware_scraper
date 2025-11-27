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
        # Imagen: selectores para intentar capturar la mejor calidad
        'image_candidates': [
            'img.poly-component__picture::attr(data-src)',  # Lazy load high res
            'img.poly-component__picture::attr(src)',       # Standard src
            'div.poly-card__portada img::attr(data-src)',   # Variación de layout
            'div.poly-card__portada img::attr(src)',        # Variación de layout standard
            'img.ui-search-result-image__element::attr(data-src)', # Legacy layout
            'img.ui-search-result-image__element::attr(src)',      # Legacy layout standard
        ]
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
        - Extracción robusta de imagen
        """
        item = super().parse_product(product_selector, response)

        # Si base no encontró precio, intentamos alternativa
        if not item.get('price_current'): # Nota: base_spider usa price_current
            alt = product_selector.css(self.selectors.get('price_alt', '')).get()
            if alt:
                item['price_current'] = alt # El pipeline limpiará esto

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
        if item.get('product_url'):
            item['product_url'] = item['product_url'].split('#')[0].strip()

        # --- Extracción Robusta de Imagen ---
        # Iteramos sobre candidatos hasta encontrar uno válido
        image_url = None
        for selector in self.selectors.get('image_candidates', []):
            img_candidate = product_selector.css(selector).get()
            if img_candidate:
                # A veces vienen imágenes base64 o placeholders, filtramos si es necesario
                if 'http' in img_candidate: 
                    image_url = img_candidate
                    break
        
        if image_url:
            # Intento de mejora de calidad (hack común en ML: cambiar tamaño en URL si es posible)
            # ML suele tener urls tipo .../D_NQ_NP_XXXXXX-O.webp
            # Si encontramos una versión pequeña, a veces no hay mucho que hacer sin entrar al producto,
            # pero priorizamos data-src que suele ser la mejor.
            
            # Asegurar absoluta
            image_url = response.urljoin(image_url)
            item['image_url'] = image_url
            item['image_urls'] = [image_url] # Lista estricta para pipeline
        else:
            item['image_urls'] = []

        return item
