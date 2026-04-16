import logging
import time
from typing import Any, Dict, List, Optional

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException

from config import BaseConfig


logger = logging.getLogger(__name__)


class WildberriesClient:
    """HTTP-клиент для запросов к API Wildberries."""

    def __init__(self, config: BaseConfig):
        """Инициализация клиента."""

        self.config = config
        self._basket_host_cache: Dict[str, str] = {}
        self._basket_hosts = [f'basket-{i:02d}.wbbasket.ru' for i in range(1, 31)]
        self._preferred_hosts = [f'basket-{i:02d}.wbbasket.ru' for i in range(11, 21)]

    def _request_with_retry(self, url: str, params: Dict[str, Any], query: str) -> Dict[str, Any]:
        """GET-запрос с повторными попытками и экспоненциальной задержкой при 429."""

        delay = 2

        for attempt in range(1, self.config.MAX_RETRIES + 1):
            try:
                response = requests.get(
                    url=url,
                    params=params,
                    headers=self.config.get_headers(query),
                    impersonate='chrome120',
                    timeout=30
                )

                if response.status_code == 429:
                    logger.warning(f'429 на {url}, попытка {attempt}/{self.config.MAX_RETRIES}, жду {delay} сек')
                    time.sleep(delay)
                    delay *= 2
                    continue

                response.raise_for_status()
                return response.json()

            except RequestException as e:
                logger.warning(f'Попытка {attempt}/{self.config.MAX_RETRIES} для {url}: {e}')
                if attempt == self.config.MAX_RETRIES:
                    raise RuntimeError(f'Не удалось выполнить запрос к {url}: {e}') from e
                time.sleep(delay)
                delay *= 2

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

    def get_basket_details(self, nm_id: int) -> Optional[Dict[str, Any]]:
        """Получает детальную информацию о товаре, перебирая basket-хосты с кешем."""

        vol = nm_id // 100000
        part = nm_id // 1000
        cache_key = f'{vol}:{part}'

        hosts_to_try: List[str] = []

        cached_host = self._basket_host_cache.get(cache_key)
        if cached_host:
            hosts_to_try.append(cached_host)

        hosts_to_try.extend([h for h in self._preferred_hosts if h not in hosts_to_try])
        hosts_to_try.extend([h for h in self._basket_hosts if h not in hosts_to_try])

        for host in hosts_to_try[:12]:
            url = f'https://{host}/vol{vol}/part{part}/{nm_id}/info/ru/card.json'
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    self._basket_host_cache[cache_key] = host
                    return response.json()
                if response.status_code in (403, 404):
                    continue
            except RequestException:
                continue

        return None
