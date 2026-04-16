import logging
import time
from typing import Any, Dict, List

from client import WildberriesClient
from config import BaseConfig
from mapper import enrich_product, map_product
from save_excel import ExcelSaver

logger = logging.getLogger(__name__)


class WildberriesParser:
    """Управляет сбором каталога, сбором деталей, фильтрацией и сохранением."""

    def __init__(self, config: BaseConfig = None, client: WildberriesClient = None, saver: ExcelSaver = None):
        """Инициализация парсера."""

        self.config = config if config is not None else BaseConfig()
        self.client = client if client is not None else WildberriesClient(self.config)
        self.saver = saver if saver is not None else ExcelSaver(self.config.OUTPUT_DIR)

    def collect_catalog(self, query: str) -> List[Dict[str, Any]]:
        """
        Собирает все товары по поисковому запросу со всех страниц.
        Останавливается, если страница вернула пустой список товаров или если 5 страниц подряд не дали ни одного нового товара.
        """

        rows: List[Dict[str, Any]] = []
        seen_ids = set()
        page = 1
        no_new_pages = 0
        max_no_new_pages = 5

        while True:
            try:
                products = self.client.search_page(query, page)
            except RuntimeError as e:
                logger.error(f'Страница {page}: не удалось загрузить ({e})')
                break

            if not products:
                logger.info(f'Страница {page}: товары закончились')
                break

            fresh_count = 0
            for product in products:
                nm_id = int(product.get('id', 0))
                if not nm_id or nm_id in seen_ids:
                    continue
                seen_ids.add(nm_id)
                rows.append(map_product(product, self.config))
                fresh_count += 1

            logger.info(f'Страница {page}: добавлено {fresh_count} товаров, всего {len(rows)}')

            if fresh_count == 0:
                no_new_pages += 1
                if no_new_pages >= max_no_new_pages:
                    logger.info(f'Остановка: {max_no_new_pages} страниц подряд без новых товаров')
                    break
            else:
                no_new_pages = 0

            page += 1
            time.sleep(self.config.REQUEST_DELAY)

        logger.info(f'Сбор завершён. Всего товаров: {len(rows)}')
        return rows

    def enrich_catalog(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Собирает детальную информацию."""

        enriched: List[Dict[str, Any]] = []
        total = len(rows)

        for index, row in enumerate(rows, start=1):
            article = int(row.get('article', 0) or 0)
            if article:
                details = self.client.get_basket_details(article)

                if details:
                    row = enrich_product(row, details, self.config)

            enriched.append(row)

            if index % 50 == 0 or index == total:
                logger.info(f'Сбор деталей: {index}/{total}')

            time.sleep(self.config.DETAIL_DELAY)

        return enriched

    def filter_catalog(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Фильтрует каталог."""

        filtered: List[Dict[str, Any]] = []
        for row in rows:
            rating = float(row.get('rating', 0) or 0)
            price = float(row.get('price', 0) or 0)
            country = str(row.get('country', '')).lower()

            if (
                rating >= self.config.RATING_THRESHOLD
                and price <= self.config.MAX_PRICE_RUB
                and self.config.REQUIRED_COUNTRY in country
            ):
                filtered.append(row)

        logger.info(f'Отобрано {len(filtered)} товаров из {len(rows)}')
        return filtered

    def run(self, query: str) -> Dict[str, Any]:
        """Запускает сбор, фильтрацию, сохранение."""

        rows = self.collect_catalog(query)
        rows = self.enrich_catalog(rows)
        filtered = self.filter_catalog(rows)

        self.saver.save(rows, self.config.CATALOG_FILENAME)
        self.saver.save(filtered, self.config.FILTERED_FILENAME)

        logger.info(f'Полный каталог сохранен: {self.config.OUTPUT_DIR}/{self.config.CATALOG_FILENAME}')
        logger.info(f'Выборка сохранена: {self.config.OUTPUT_DIR}/{self.config.FILTERED_FILENAME}')

        return {
            'catalog_count': len(rows),
            'filtered_count': len(filtered),
        }
