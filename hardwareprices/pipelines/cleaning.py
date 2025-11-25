from itemadapter import ItemAdapter
from hardwareprices.utils.parsing import clean_price, normalize_text

class CleaningPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Limpieza de precios
        if adapter.get('price_current'):
            # Si ya es int, lo dejamos, si es str, lo limpiamos
            if isinstance(adapter['price_current'], str):
                adapter['price_current'] = clean_price(adapter['price_current'])
        
        if adapter.get('price_original'):
             if isinstance(adapter['price_original'], str):
                adapter['price_original'] = clean_price(adapter['price_original'])

        # Normalización de textos
        for field in ['product_name', 'brand', 'category', 'store_name']:
            if adapter.get(field):
                adapter[field] = normalize_text(adapter[field])
                
        # Calculo de descuento si aplica
        price_curr = adapter.get('price_current')
        price_orig = adapter.get('price_original')
        
        if price_curr and price_orig and price_orig > price_curr:
            discount = ((price_orig - price_curr) / price_orig) * 100
            adapter['discount_percentage'] = round(discount, 2)
        else:
            adapter['discount_percentage'] = 0.0

        return item
