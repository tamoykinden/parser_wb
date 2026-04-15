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

        impersonate_list = ['chrome120', 'chrome124', 'chrome131', 'safari17_0', 'firefox133']
        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                impersonate = impersonate_list[attempt % len(impersonate_list)]

                response = requests.get(
                    url=self.config.SEARCH_URL,
                    params=params,
                    headers=self.config.get_headers(),
                    impersonate=impersonate,
                    timeout=30
                )

                if response.status_code == 429:
                    wait_time = retry_delay * (attempt + 1)
                    logger.warning(
                        f'Страница {page}: 429 Too Many Requests, попытка {attempt + 1}/{max_retries}, жду {wait_time} сек'
                    )
                    time.sleep(wait_time)

                    continue

                response.raise_for_status()
                data = response.json()

                logger.info(f'Ключи: {list(data.keys())}')

                if 'data' in data:
                    products = data.get('data', {}).get('products', [])
                else:
                    products = data.get('products', [])

                if not products:
                    logger.warning(f'Страница {page}: товары не найдены')
                    return []

                ids = [product['id'] for product in products]
                logger.info(f'Страница {page}: получено {len(ids)} ID')
                return ids

            except RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f'Ошибка при запросе страницы {page}: {e}')
                    return []

                wait_time = retry_delay * (attempt + 1)
                logger.warning(f'Страница {page}: ошибка {e}, попытка {attempt + 1}/{max_retries}, жду {wait_time} сек')
                time.sleep(wait_time)

            except (KeyError, ValueError, TypeError) as e:
                logger.error(f'Ошибка при разборе ответа страницы {page}: {e}')
                return []

        return []

    def get_all_product_ids(self, query: str) -> List[int]:
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
