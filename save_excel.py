from pathlib import Path
from typing import Any, Dict, List, Tuple

from openpyxl import Workbook


class ExcelSaver:
    """Класс для сохранения данных в формат xlsx."""

    def __init__(self, output_dir: str):
        """Инициализация объекта для сохранения xlsx-файлов."""

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_headers() -> List[Tuple[str, str]]:
        """Возвращает список заголовков для xlsx-файла."""

        return [
            ('Ссылка на товар', 'product_url'),
            ('Артикул', 'article'),
            ('Название', 'name'),
            ('Цена', 'price'),
            ('Описание', 'description'),
            ('Ссылки на изображения', 'image_urls'),
            ('Все характеристики (JSON)', 'characteristics'),
            ('Название селлера', 'seller_name'),
            ('Ссылка на селлера', 'seller_url'),
            ('Размеры товара', 'sizes'),
            ('Остатки по товару', 'stocks'),
            ('Рейтинг', 'rating'),
            ('Количество отзывов', 'reviews_count'),
            ('Страна производства', 'country'),
        ]

    def save(self, rows: List[Dict[str, Any]], filename: str) -> None:
        """Сохраняет список словарей в xlsx-файл."""

        file_path = self.output_dir / filename

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'catalog'

        headers = self._get_headers()
        worksheet.append([title for title, _ in headers])

        for row in rows:
            worksheet.append([row.get(key, '') for _, key in headers])

        workbook.save(file_path)
