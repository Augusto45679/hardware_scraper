import hashlib
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes
from scrapy.http import Request

class CustomImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        # Solo tomamos la primera imagen si existe, ya que el usuario quiere 1:1 product_id -> imagen
        image_urls = item.get(self.images_urls_field, [])
        if image_urls:
            # Priorizamos la primera URL
            yield Request(image_urls[0], meta={'product_id': item.get('product_id')})

    def file_path(self, request, response=None, info=None, item=None):
        # Obtenemos product_id desde meta (inyectado en get_media_requests) o desde item (si está disponible)
        product_id = request.meta.get('product_id')
        
        # Fallback si no hay product_id (no debería pasar si el spider está bien)
        if not product_id and item:
            product_id = item.get('product_id')
            
        if not product_id:
            # Fallback final al hash de la URL si todo falla
            image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
            return f'full/{image_guid}.jpg'
            
        return f'full/{product_id}.jpg'

    def item_completed(self, results, item, info):
        # Loguear resultados
        for success, res in results:
            if success:
                info.spider.logger.info(f"Image downloaded for product {item.get('product_id')}: {res['path']}")
            else:
                info.spider.logger.error(f"Image download failed for product {item.get('product_id')}: {res}")
        
        return super().item_completed(results, item, info)
