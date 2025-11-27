# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from datetime import datetime
from itemadapter import ItemAdapter
import hashlib # Importamos hashlib para generar el nombre del archivo manualmente
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import pymongo
import logging


class HardwarepricesPipeline:
    def open_spider(self, spider):
        self.file = open('hardware_prices.json', 'w')
        self.file.write('[')

    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + ","
        self.file.write(line)
        return item

# class GoogleSheetsPipeline:
#     def __init__(self):
#         # --- Configuración de Google Sheets ---
#         # Asegúrate de que 'credentials.json' esté en la carpeta raíz del proyecto.
#         # Comparte tu Google Sheet con el 'client_email' de ese archivo.
#         self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#         self.creds_file = 'credentials.json'
#         self.spreadsheet_name = 'Hardware_Scrapping'  # <-- CAMBIA ESTO por el nombre de tu hoja de cálculo
#         self.sheet_name = 'Sheet1'
#         self.sheet = None
#         self.header_written = False
#         # Define el orden deseado para las columnas en la hoja de cálculo
#         self.column_order = ['product_id', 'product_name', 'price', 'store', 'link', 'date']
#         # El campo 'currency' se omitirá de la hoja de cálculo
# 
#         self.existing_links = set()
#         self.link_column_index = -1
#         self.product_id_counter = 1
#         self.product_id_column_index = -1
#         # Buffer para acumular items antes de escribirlos en lote
#         self.items_buffer = []
# 
#     def open_spider(self, spider):
#         """
#         Se ejecuta cuando la araña se abre. Realiza la conexión con Google Sheets.
#         """
#         try:
#             creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, self.scope)
#             client = gspread.authorize(creds)
#             spreadsheet = client.open(self.spreadsheet_name)
#             self.sheet = spreadsheet.worksheet(self.sheet_name)
# 
#             headers = self.column_order
#             # Encuentra los índices de las columnas 'link' y 'product_id'
#             try:
#                 self.link_column_index = headers.index('link') + 1  # gspread usa índices base 1
#                 self.product_id_column_index = headers.index('product_id') + 1
#             except ValueError:
#                 spider.logger.error("El `column_order` en la pipeline debe contener 'link' y 'product_id'.")
#                 return
# 
#             all_values = self.sheet.get_all_values()
# 
#             # Escribe los encabezados si la hoja está vacía
#             if not all_values:
#                 self.sheet.append_row(headers, value_input_option='USER_ENTERED')
#                 self.header_written = True
#             else:
#                 # Si no está vacía, verifica si falta la columna 'date'
#                 current_headers = all_values[0]
#                 if 'date' not in current_headers:
#                     spider.logger.info("Agregando columna 'date' a los encabezados existentes...")
#                     self.sheet.update_cell(1, len(current_headers) + 1, 'date')
# 
#                 # Si no está vacía, calcula el siguiente ID y carga los links
#                 spider.logger.info("Cargando links existentes para de-duplicación...")
#                 # Extrae los valores de las columnas de una sola vez
#                 link_col_vals = [row[self.link_column_index - 1] for row in all_values[1:] if len(row) >= self.link_column_index]
#                 id_col_vals = [row[self.product_id_column_index - 1] for row in all_values[1:] if len(row) >= self.product_id_column_index]
# 
#                 self.existing_links = set(link_col_vals)
# 
#                 # Calcula el siguiente ID
#                 numeric_ids = [int(id_val) for id_val in id_col_vals if id_val.isdigit()]
#                 if numeric_ids:
#                     self.product_id_counter = max(numeric_ids) + 1
#                 
#                 spider.logger.info(f"El siguiente ID de producto será: {self.product_id_counter}")
# 
#             spider.logger.info(f"Conectado exitosamente a Google Sheet: '{self.spreadsheet_name}' -> Hoja: '{self.sheet_name}'")
#         except gspread.exceptions.SpreadsheetNotFound:
#             spider.logger.error(f"ERROR: No se encontró la hoja de cálculo '{self.spreadsheet_name}'.")
#         except gspread.exceptions.WorksheetNotFound:
#             spider.logger.error(f"ERROR: No se encontró la hoja de trabajo '{self.sheet_name}' en la hoja de cálculo.")
#         except Exception as e:
#             spider.logger.error(f"Fallo al conectar con Google Sheets: {e}")
# 
#     def close_spider(self, spider):
#         """
#         Se ejecuta cuando la araña se cierra. Escribe todos los items acumulados
#         en la hoja de cálculo de una sola vez.
#         """
#         if not self.items_buffer:
#             spider.logger.info("No hay nuevos items para añadir a Google Sheets.")
#             return
# 
#         try:
#             spider.logger.info(f"Añadiendo {len(self.items_buffer)} nuevos items a Google Sheets en un solo lote...")
#             self.sheet.append_rows(self.items_buffer, value_input_option='USER_ENTERED')
#             spider.logger.info("Items añadidos exitosamente a Google Sheets.")
#         except Exception as e:
#             spider.logger.error(f"Fallo al escribir el lote de items en Google Sheets: {e}")
# 
#     def process_item(self, item, spider):
#         """
#         Procesa cada item y lo añade como una nueva fila en la hoja de cálculo.
#         """
#         if self.sheet is None or self.link_column_index == -1 or self.product_id_column_index == -1:
#             return item  # Si la conexión falló o faltan campos, no hagas nada.
# 
#         adapter = ItemAdapter(item)
#         item_link = adapter.get('link')
#         
#         # Agregamos la fecha actual
#         adapter['date'] = datetime.now().strftime("%Y-%m-%d")
# 
#         # if item_link in self.existing_links:
#         #     spider.logger.debug(f"Item duplicado omitido: {adapter.get('product_name')}")
#         #     return item  # Omite el item
# 
#         # Asigna el nuevo ID único
#         adapter['product_id'] = self.product_id_counter
# 
#         # Asegura que los datos se escriban en el mismo orden que los encabezados
#         row = []
#         for field_name in self.column_order:
#             row.append(adapter.get(field_name, '')) # Usa '' para campos vacíos
# 
#         # En lugar de escribir la fila, la añadimos al buffer
#         self.items_buffer.append(row)
#         self.existing_links.add(item_link) # Añade el nuevo link al set para esta sesión
#         self.product_id_counter += 1 # Incrementa el contador para el siguiente item
#         spider.logger.debug(f"Item '{adapter.get('product_name')}' añadido al buffer.")
#         return item

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
            # Ejemplo: [{'url': '...', 'path': 'full/hash.jpg', 'checksum': '...'}]
            image_path = images[0].get('path')
            adapter['image_path'] = image_path # Guardamos el path local en el item
            spider.logger.info(f"DEBUG - Image Path Extracted from Pipeline: {image_path}")
        elif image_urls and len(image_urls) > 0:
            # FALLBACK: Si ImagesPipeline no llenó el campo 'images' (por razón desconocida),
            # calculamos manualmente dónde DEBERÍA estar la imagen.
            # Scrapy por defecto usa el hash SHA1 de la URL.
            first_image_url = image_urls[0]
            image_guid = hashlib.sha1(first_image_url.encode('utf-8')).hexdigest()
            image_path = f'full/{image_guid}.jpg'
            adapter['image_path'] = image_path
            spider.logger.warning(f"DEBUG - Image Path Calculated Manually (Fallback): {image_path}")
        else:
            spider.logger.warning(f"DEBUG - No images found for product: {adapter.get('product_name')}")

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
