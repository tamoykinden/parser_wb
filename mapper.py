import json
from typing import Any, Dict, List


def extract_sizes(product: Dict[str, Any]) -> List[str]:
    """Извлекает список уникальных размеров."""

    sizes: List[str] = []
    for size_item in product.get('sizes', []):
        size_name = size_item.get('origName') or size_item.get('name')
        if size_name and size_name not in sizes:
            sizes.append(str(size_name))
    return sizes


def extract_stocks(product: Dict[str, Any]) -> int:
    """Суммирует остатки товара по всем складам и размерам."""

    total_qty = 0
    for size_item in product.get('sizes', []):
        for stock in size_item.get('stocks', []):
            qty = stock.get('qty')
            if isinstance(qty, int):
                total_qty += qty
    return total_qty


def extract_price(product: Dict[str, Any]) -> float:
    """цена товара в рублях."""

    direct_price = product.get('salePriceU') or product.get('priceU')
    if isinstance(direct_price, (int, float)) and direct_price > 0:
        return round(float(direct_price) / 100, 2)

    for size_item in product.get('sizes', []):
        price_obj = size_item.get('price', {})
        if not isinstance(price_obj, dict):
            continue
        candidate = price_obj.get('product') or price_obj.get('basic')
        if isinstance(candidate, (int, float)) and candidate > 0:
            return round(float(candidate) / 100, 2)

    return 0.0


def extract_characteristics(product: Dict[str, Any]) -> List[Dict[str, str]]:
    """Извлекает характеристики товара из поисковой выдачи."""

    characteristics: List[Dict[str, str]] = []
    for option in product.get('options', []) or []:
        name = option.get('name')
        value = option.get('value')
        if name:
            characteristics.append({'name': str(name), 'value': str(value)})
    return characteristics


def extract_country(characteristics: List[Dict[str, str]]) -> str:
    """Ищет страну производства в списке характеристик."""

    for item in characteristics:
        key = str(item.get('name', '')).lower()
        if 'страна' in key:
            return str(item.get('value', '')).strip().lower()
    return ''


def merge_characteristics(existing: List[Dict[str, str]], incoming: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Объединяет два списка характеристик без дублирования по имени."""

    existing_keys = {
        str(item.get('name', '')).strip().lower()
        for item in existing
        if isinstance(item, dict)
    }
    merged = list(existing)
    for option in incoming:
        name = str(option.get('name', '')).strip()
        value = str(option.get('value', '')).strip()
        if not name or name.lower() in existing_keys:
            continue
        merged.append({'name': name, 'value': value})
        existing_keys.add(name.lower())
    return merged


def collect_options_from_details(details: Dict[str, Any]) -> List[Dict[str, str]]:
    """Собирает характеристики из детальной карточки товара."""

    options: List[Dict[str, str]] = []
    seen = set()

    def add_option(name: Any, value: Any) -> None:
        key = str(name).strip()
        val = str(value).strip()
        if not key:
            return
        dedup = (key.lower(), val.lower())
        if dedup in seen:
            return
        seen.add(dedup)
        options.append({'name': key, 'value': val})

    for option in details.get('options', []) or []:
        add_option(option.get('name', ''), option.get('value', ''))

    for group in details.get('grouped_options', []) or []:
        for option in group.get('options', []) or []:
            add_option(option.get('name', ''), option.get('value', ''))

    return options


def build_images(nm_id: int, pics_count: int, template: str) -> List[str]:
    """список ссылок на изображения товара."""

    count = pics_count if pics_count > 0 else 1
    return [template.format(nm_id=nm_id, index=i) for i in range(1, count + 1)]


def map_product(product: Dict[str, Any], config: Any) -> Dict[str, Any]:
    """Преобразует JSON товара из поиска в строку для экселя."""

    nm_id = int(product.get('id', 0))
    characteristics = extract_characteristics(product)
    country = extract_country(characteristics)

    supplier_id = product.get('supplierId')
    seller_url = config.SELLER_URL_TEMPLATE.format(supplier_id=supplier_id) if supplier_id else ''

    return {
        'product_url': config.PRODUCT_URL_TEMPLATE.format(nm_id=nm_id),
        'article': str(nm_id),
        'name': product.get('name', ''),
        'price': extract_price(product),
        'description': product.get('description', ''),
        'image_urls': ', '.join(build_images(nm_id, int(product.get('pics', 0)), config.IMAGE_URL_TEMPLATE)),
        'characteristics': json.dumps(characteristics, ensure_ascii=False),
        'seller_name': product.get('supplier', ''),
        'seller_url': seller_url,
        'sizes': ', '.join(extract_sizes(product)),
        'stocks': extract_stocks(product),
        'rating': float(product.get('rating', 0) or 0),
        'reviews_count': int(product.get('feedbacks', 0) or 0),
        'country': country,
    }


def enrich_product(row: Dict[str, Any], details: Dict[str, Any], config: Any) -> Dict[str, Any]:
    """Деталиизурет строку каталога данными из детальной карточки."""

    if not row.get('description'):
        row['description'] = str(details.get('description', '') or '')

    incoming_options = collect_options_from_details(details)
    if incoming_options:
        try:
            existing_options = json.loads(row.get('characteristics') or '[]')
        except (TypeError, ValueError):
            existing_options = []
        merged_options = merge_characteristics(existing_options, incoming_options)
        row['characteristics'] = json.dumps(merged_options, ensure_ascii=False)
        if not row.get('country'):
            row['country'] = extract_country(merged_options)

    if not row.get('image_urls'):
        photo_count = int((details.get('media') or {}).get('photo_count') or 0)
        if photo_count > 0:
            article = int(row.get('article', 0))
            row['image_urls'] = ', '.join(build_images(article, photo_count, config.IMAGE_URL_TEMPLATE))

    return row
