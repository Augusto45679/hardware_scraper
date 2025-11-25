import re
import unicodedata

def clean_price(price_str: str) -> int:
    """
    Limpia un string de precio, eliminando símbolos y puntos, y lo convierte a entero.
    Ejemplo: "$ 1.234,50" -> 1234
    """
    if not price_str:
        return 0
    # Elimina el símbolo de la moneda, puntos, comas y espacios en blanco.
    # Asumimos que los decimales se descartan o que el precio es entero.
    # Si hay decimales con coma, split y tomar la parte entera.
    price_str = price_str.split(',')[0] 
    cleaned_price = re.sub(r'[^\d]', '', price_str)
    try:
        return int(cleaned_price)
    except (ValueError, TypeError):
        return 0

def normalize_text(text: str) -> str:
    """
    Normaliza un texto: elimina acentos, convierte a minúsculas y elimina espacios extra.
    Ejemplo: "  Placa de Video   " -> "placa de video"
    """
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'\s+', ' ', text)
