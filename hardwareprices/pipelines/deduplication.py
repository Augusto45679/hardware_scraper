from itemadapter import ItemAdapter
from hardwareprices.utils.hashing import generate_content_hash, generate_product_id

class DeduplicationPipeline:
    def __init__(self):
        self.seen_ids = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Generar IDs si no existen
        if not adapter.get('product_id'):
            store_id = adapter.get('store_id', spider.name)
            # Usamos product_url como identificador único por defecto si no hay external_id
            unique_id = adapter.get('external_id') or adapter.get('product_url')
            adapter['product_id'] = generate_product_id(store_id, unique_id)
            
        # Generar Content Hash
        adapter['content_hash'] = generate_content_hash(adapter.asdict())
        
        # Deduplicación simple en memoria (por ejecución)
        # Nota: Para producción real, esto debería ser contra una DB o Redis
        pid = adapter['product_id']
        if pid in self.seen_ids:
            # Opcional: DropItem si es duplicado exacto, o dejar pasar si queremos actualizar 'last_seen'
            # Por ahora solo logueamos
            spider.logger.debug(f"Duplicate product_id found: {pid}")
        else:
            self.seen_ids.add(pid)

        return item
