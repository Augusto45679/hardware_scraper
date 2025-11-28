import pymongo
from itemadapter import ItemAdapter
import logging
import hashlib

class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db, collection_name):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'hardware_db'),
            collection_name=crawler.settings.get('MONGO_COLLECTION', 'products')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info(f"Conectado a MongoDB: {self.mongo_uri} -> DB: {self.mongo_db}")

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Procesar ruta de la imagen descargada
        images = adapter.get('images')
        image_urls = adapter.get('image_urls')
        
        # Debug logging para ver qué está llegando
        spider.logger.info(f"DEBUG - Product: {adapter.get('product_name')}")
        spider.logger.info(f"DEBUG - Image URLs: {image_urls}")
        spider.logger.info(f"DEBUG - Images Result: {images}")

        if images and len(images) > 0:
            # ImagesPipeline guarda una lista de dicts. Tomamos el path del primero.
            # Ejemplo: [{'url': '...', 'path': 'full/product_id.jpg', 'checksum': '...'}]
            image_path = images[0].get('path')
            
            # Aseguramos que el path sea relativo como pide el usuario: "scraped_images/full/..."
            # El pipeline devuelve "full/...", así que prependeamos "scraped_images/"
            if not image_path.startswith('scraped_images/'):
                image_path = f"scraped_images/{image_path}"
                
            adapter['image_path'] = image_path # Guardamos el path local en el item
            spider.logger.info(f"DEBUG - Image Path Extracted from Pipeline: {image_path}")
            spider.logger.info(f"DEBUG - Final Image URL: {adapter.get('image_url')}")
        else:
            spider.logger.warning(f"DEBUG - No images found for product: {adapter.get('product_name')}")
            # Si no hay imagen descargada, intentamos ver si hay URL para loggear
            if image_urls:
                 spider.logger.warning(f"DEBUG - Image URLs were present but download failed or pipeline skipped: {image_urls}")


        # Convertir a dict para Mongo
        item_dict = adapter.asdict()
        
        # Usamos update_one con upsert para evitar duplicados si existe un ID único
        # Si no tienes un ID único confiable, usa insert_one
        
        # Opción A: Usar product_id (hash) como clave única
        filter_query = {'product_id': item_dict.get('product_id')}
        
        # Opción B: Usar URL como clave única
        # filter_query = {'product_url': item_dict.get('product_url')}

        try:
            self.db[self.collection_name].update_one(
                filter_query,
                {'$set': item_dict},
                upsert=True
            )
            spider.logger.debug(f"Item guardado en MongoDB: {item_dict.get('product_id')}")
        except Exception as e:
            spider.logger.error(f"Error guardando en MongoDB: {e}")

        return item
