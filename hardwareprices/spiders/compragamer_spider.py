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
        # Imagen: CompraGamer usa lazy loading a veces, o paths relativos
        'image_candidates': [
            'div.product-card__image-container img::attr(src)', 
            'cgw-item-image img::attr(src)',
            'img.product-card__image::attr(src)',
        ]
    }

    def get_next_page(self, response):
        """
        CompraGamer no tiene un botón "siguiente" estándar, sino que la paginación
        se basa en si se encuentran productos. Si no hay productos, se detiene.
        """
        if not response.css(self.selectors['product_container']):
            return None # No hay productos, fin de la paginación.
        return super().get_next_page(response)

    def parse_product(self, product_selector, response):
        """
        Sobreescribimos para manejar URLs relativas de imágenes y lazy loading.
        """
        item = super().parse_product(product_selector, response)
        
        # --- Extracción Robusta de Imagen ---
        image_url = None
        for selector in self.selectors.get('image_candidates', []):
            img_candidate = product_selector.css(selector).get()
            if img_candidate:
                image_url = img_candidate
                break
        
        if image_url:
            # CompraGamer suele usar URLs relativas tipo /imagenes/productos/...
            # Aseguramos que sea absoluta
            full_image_url = response.urljoin(image_url)
            
            # Validación extra: a veces ponen un placeholder si no hay imagen
            if 'sin_imagen' not in full_image_url:
                item['image_url'] = full_image_url
                item['image_urls'] = [full_image_url] # Lista requerida por ImagesPipeline

        return item