from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter

class ValidationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Campos obligatorios
        required_fields = ['product_name', 'price_current', 'product_url']
        
        for field in required_fields:
            if not adapter.get(field):
                raise DropItem(f"Missing required field: {field} in {item}")
        
        # Validación de precio positivo
        if adapter.get('price_current') <= 0:
             raise DropItem(f"Invalid price: {adapter.get('price_current')} in {item}")

        return item
