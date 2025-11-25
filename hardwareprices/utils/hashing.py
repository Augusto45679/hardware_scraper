import hashlib
import json

def generate_content_hash(item_dict: dict, fields_to_hash: list = None) -> str:
    """
    Genera un hash MD5 basado en el contenido de los campos especificados.
    Útil para detectar cambios en el producto.
    """
    if fields_to_hash is None:
        # Campos por defecto que definen la "identidad" del contenido mutable
        fields_to_hash = ['price_current', 'availability', 'product_name']
    
    data_to_hash = {k: item_dict.get(k) for k in fields_to_hash if k in item_dict}
    
    # Ordenamos las llaves para asegurar consistencia
    serialized_data = json.dumps(data_to_hash, sort_keys=True, default=str)
    return hashlib.md5(serialized_data.encode('utf-8')).hexdigest()

def generate_product_id(store_id: str, unique_identifier: str) -> str:
    """
    Genera un ID único para el producto basado en la tienda y su ID externo/URL.
    """
    raw_id = f"{store_id}:{unique_identifier}"
    return hashlib.md5(raw_id.encode('utf-8')).hexdigest()
