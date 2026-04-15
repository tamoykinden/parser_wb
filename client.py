import logging
import time
from typing import Any, Dict, List

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException

from config import BaseConfig


logger = logging.getLogger(__name__)


class WildberriesClient:
    """
    HTTP-клиент для запросов к API Wildberries.

    Отвечает за поиск товаров и получение детальных карточек.
    """

    def __init__(self, config: BaseConfig):
        """Инициализация клиента."""

        self.config = config

    def _request_with_retry(self, url: str, params: Dict[str, Any], query: str) -> Dict[str, Any]:
        """GET-запрос с повторными попытками при ошибках."""

        for attempt in range(1, self.config.MAX_RETRIES + 1):
            try:
                response = requests.get(
                    url=url,
                    params=params,
                    headers=self.config.get_headers(query),
                    impersonate='chrome120',
                    timeout=30
                )
                response.raise_for_status()
                return response.json()

            except RequestException as e:
                logger.warning(f'Попытка {attempt}/{self.config.MAX_RETRIES} для {url}: {e}')
                if attempt == self.config.MAX_RETRIES:
                    raise RuntimeError(f'Не удалось выполнить запрос к {url}: {e}') from e
                time.sleep(2)

        raise RuntimeError(f'Не удалось выполнить запрос к {url}')

    def search_page(self, query: str, page: int) -> List[Dict[str, Any]]:
        """Получает список товаров с одной страницы поисковой выдачи."""
        params = self.config.SEARCH_PARAMS.copy()
        params['query'] = query
        params['page'] = page

        data = self._request_with_retry(self.config.SEARCH_URL, params, query)
        products = data.get('data', {}).get('products', [])
        if not products:
            products = data.get('products', [])

        return products

    def get_basket_details(self, nm_id: int) -> Dict[str, Any]:
        """Получает детальную информацию о товаре с basket-хоста."""

        vol = nm_id // 100000
        part = nm_id // 1000

        url = self.config.BASKET_URL_TEMPLATE.format(vol=vol, part=part, nm_id=nm_id)

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        return response.json()
