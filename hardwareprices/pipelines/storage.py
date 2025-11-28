import json
from datetime import datetime
from itemadapter import ItemAdapter
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('hardware_prices_new.json', 'w', encoding='utf-8')
        self.file.write('[')
        self.first_item = True

    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(',\n')
        self.first_item = False
        
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False, indent=4)
        self.file.write(line)
        return item

# class GoogleSheetsPipeline:
#     def __init__(self):
#         # --- Configuración de Google Sheets ---
#         self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#         self.creds_file = 'credentials.json'
#         self.spreadsheet_name = 'Hardware_Scrapping'
#         self.sheet_name = 'Sheet1'
#         self.sheet = None
        
#         # Mapeo de campos del Item a columnas del Sheet
#         # Ajustado al nuevo esquema pero manteniendo compatibilidad visual
#         self.column_order = [
#             'product_id', 'store_name', 'product_name', 'price_current', 
#             'price_original', 'discount_percentage', 'product_url', 'scraped_at'
#         ]
        
#         self.items_buffer = []

#     def open_spider(self, spider):
#         try:
#             creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, self.scope)
#             client = gspread.authorize(creds)
#             spreadsheet = client.open(self.spreadsheet_name)
#             self.sheet = spreadsheet.worksheet(self.sheet_name)
            
#             # Verificar encabezados
#             all_values = self.sheet.get_all_values()
#             if not all_values:
#                 self.sheet.append_row(self.column_order, value_input_option='USER_ENTERED')
            
#             spider.logger.info(f"Conectado a Google Sheet: {self.spreadsheet_name}")
#         except Exception as e:
#             spider.logger.error(f"Error conectando a Google Sheets: {e}")
#             self.sheet = None

#     def close_spider(self, spider):
#         if self.items_buffer and self.sheet:
#             try:
#                 spider.logger.info(f"Escribiendo {len(self.items_buffer)} items a Google Sheets...")
                
#                 # Calculamos explícitamente la próxima fila vacía para forzar la escritura en la columna A
#                 # Esto evita que gspread detecte erróneamente el final de la tabla y escriba en columnas desplazadas
#                 all_values = self.sheet.get_all_values()
#                 next_row = len(all_values) + 1
#                 range_start = f"A{next_row}"
                
#                 self.sheet.update(range_name=range_start, values=self.items_buffer, value_input_option='USER_ENTERED')
#             except Exception as e:
#                 spider.logger.error(f"Error escribiendo en Google Sheets: {e}")

#     def process_item(self, item, spider):
#         if not self.sheet:
#             return item

#         adapter = ItemAdapter(item)
#         row = []
#         for field in self.column_order:
#             val = adapter.get(field, '')
#             row.append(str(val)) # Convertir a string para asegurar compatibilidad
            
#         self.items_buffer.append(row)
#         return item
