import cloudinary
import cloudinary.uploader
import requests
from io import BytesIO
import pymongo
from itemadapter import ItemAdapter
import os

class SmartCloudinaryPipeline:
    def __init__(self, mongo_uri, mongo_db, collection_name, cloud_name, api_key, api_secret, images_store):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.collection_name = collection_name
        self.images_store = images_store
        self.client = None
        self.db = None
        
        # Cloudinary config
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'hardware_db'),
            collection_name=crawler.settings.get('MONGO_COLLECTION', 'products'),
            cloud_name=crawler.settings.get('CLOUDINARY_CLOUD_NAME'),
            api_key=crawler.settings.get('CLOUDINARY_API_KEY'),
            api_secret=crawler.settings.get('CLOUDINARY_API_SECRET'),
            images_store=crawler.settings.get('IMAGES_STORE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.logger.info(f"SmartCloudinaryPipeline: Conectado a MongoDB: {self.mongo_uri}")

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        product_id = adapter.get('product_id')
        images = adapter.get('images')
        
        spider.logger.warning(f"DEBUG PIPELINE - Recibido: {adapter.get('image_urls')}")
        
        if not product_id:
            spider.logger.warning("SmartCloudinaryPipeline: Item sin product_id, saltando.")
            return item

        # 1. Verificación en MongoDB
        existing_doc = self.db[self.collection_name].find_one(
            {'product_id': product_id},
            {'image_url': 1}
        )

        # CASO A: Ya existe y tiene imagen
        if existing_doc and existing_doc.get('image_url'):
            stored_url = existing_doc.get('image_url')
            spider.logger.info(f"SmartCloudinaryPipeline: Imagen encontrada en caché DB para {product_id}, saltando upload.")
            adapter['image_url'] = stored_url
            return item

        # CASO B: Es nuevo o no tiene imagen
        if not images:
            spider.logger.warning(f"SmartCloudinaryPipeline: No hay imágenes descargadas para {product_id}, no se puede subir nada.")
            return item

        # Intentamos subir la imagen local
        # images es una lista de dicts: [{'url': ..., 'path': 'full/xyz.jpg', ...}]
        image_path_rel = images[0].get('path')
        full_path = os.path.join(self.images_store, image_path_rel)
        
        if not os.path.exists(full_path):
             spider.logger.error(f"SmartCloudinaryPipeline: Archivo local no encontrado: {full_path}")
             return item

        try:
            spider.logger.info(f"SmartCloudinaryPipeline: Subiendo imagen local {full_path} a Cloudinary...")
            
            # Subir a Cloudinary usando el product_id como public_id
            upload_result = cloudinary.uploader.upload(
                full_path,
                public_id=product_id,
                overwrite=True,
                resource_type="image"
            )
            
            cloudinary_url = upload_result.get('secure_url')
            
            if cloudinary_url:
                adapter['image_url'] = cloudinary_url
                spider.logger.info(f"SmartCloudinaryPipeline: Upload exitoso: {cloudinary_url}")
                spider.logger.warning(f"DEBUG CLOUDINARY - Respuesta URL: {cloudinary_url}")
            else:
                spider.logger.error(f"SmartCloudinaryPipeline: Falló upload a Cloudinary, respuesta vacía.")

        except Exception as e:
            spider.logger.error(f"SmartCloudinaryPipeline: Excepción al procesar imagen: {e}")

        return item
