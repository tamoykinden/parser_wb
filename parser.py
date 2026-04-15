import logging
import time
from typing import List

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException

from config import BaseConfig

logger = logging.getLogger(__name__)


class WildberriesParser:
    """Парсер данных с WB."""

    def __init__(self, config: BaseConfig = None):
        """Инициализация парсера."""

        self.config = config if config is not None else BaseConfig()

    def get_product_ids(self, query: str, page: int = 1) -> List[int]:
        """
        Получает список ID товаров с 1 страницы поиска.

        Возвращает список ID.
        """

        params = self.config.SEARCH_PARAMS.copy()
        params['query'] = query
        params['page'] = page

        try:
            response = requests.get(
                url=self.config.SEARCH_URL,
                params=params,
                headers=self.config.HEADERS,
                impersonate='chrome120',
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            products = data.get('products', [])

            if not products:
                logger.warning(f'Страница {page}: товары не найдены')
                return []

            ids = [product['id'] for product in products]
            logger.info(f'Страница {page}: получено {len(ids)} ID')
            return ids

        except RequestException as e:
            logger.error(f'Ошибка при запросе страницы {page}: {e}')
            return []

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f'Ошибка при разборе ответа страницы {page}: {e}')
            return []

    def get_all_priduct_ids(self, query: str) -> List[int]:
        """
        Получает список всех ID товаров со всех страниц.

        Возвращает список ID.
        """

        all_ids = []
        page = 1

        while True:
            ids = self.get_product_ids(query, page)

            if not ids:
                logger.info(f'Достигнут конец выдачи на странице {page}')
                break

            all_ids.extend(ids)
            logger.info(f'Всего собрано ID: {len(all_ids)}')

            page += 1
            time.sleep(self.config.REQUEST_DELAY)

        logger.info(f'Итог ID: {len(all_ids)}')
        return all_ids
