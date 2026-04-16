import uuid
from urllib.parse import quote_plus


class BaseConfig:
    """
    Базовые настройки парсера.

    SEARCH_URL - URL для поиска товаров через API.
    BASKET_URL_TEMPLATE - шаблон URL для получения детальной карточки товара.
    PRODUCT_URL_TEMPLATE - шаблон ссылки на карточку товара на сайте.
    SELLER_URL_TEMPLATE - шаблон ссылки на страницу продавца.
    IMAGE_URL_TEMPLATE - шаблон ссылки на изображение товара.
    SEARCH_PARAMS - параметры GET-запроса к поисковому API.
    QUERY - поисковый запрос, по которому собирается каталог.
    REQUEST_DELAY - задержка в секундах между запросами к поиску.
    DETAIL_DELAY - задержка в секундах между запросами детальных карточек.
    MAX_RETRIES - максимальное количество повторных попыток при ошибках.
    RATING_THRESHOLD - минимальный рейтинг товара для попадания в выборку.
    MAX_PRICE_RUB - максимальная цена товара в рублях для попадания в выборку.
    REQUIRED_COUNTRY - требуемая страна производства (в нижнем регистре).
    OUTPUT_DIR - директория для сохранения выходных XLSX-файлов.
    CATALOG_FILENAME - имя файла с полным каталогом товаров.
    FILTERED_FILENAME - имя файла с отфильтрованной выборкой.
    """

    SEARCH_URL = 'https://search.wb.ru/exactmatch/ru/common/v4/search'
    BASKET_URL_TEMPLATE = 'https://basket-01.wbbasket.ru/vol{vol}/part{part}/{nm_id}/info/ru/card.json'
    PRODUCT_URL_TEMPLATE = 'https://www.wildberries.ru/catalog/{nm_id}/detail.aspx'
    SELLER_URL_TEMPLATE = 'https://www.wildberries.ru/seller/{supplier_id}'
    IMAGE_URL_TEMPLATE = 'https://images.wbstatic.net/big/new/{nm_id}-{index}.jpg'

    SEARCH_PARAMS = {
        'ab_testing': 'false',
        'appType': '1',
        'curr': 'rub',
        'dest': '1259570983',
        'hide_vflags': '4294967296',
        'inheritFilters': 'false',
        'lang': 'ru',
        'resultset': 'catalog',
        'sort': 'popular',
        'spp': '30',
        'suppressSpellcheck': 'false',
    }

    QUERY = 'пальто из натуральной шерсти'

    REQUEST_DELAY = 3.0
    DETAIL_DELAY = 0.15
    MAX_RETRIES = 5

    RATING_THRESHOLD = 4.5
    MAX_PRICE_RUB = 10000
    REQUIRED_COUNTRY = 'россия'

    OUTPUT_DIR = 'output'
    CATALOG_FILENAME = 'catalog.xlsx'
    FILTERED_FILENAME = 'catalog_filtered.xlsx'

    def __init__(self):
        """Генерирует уникальные deviceid и x-queryid для обхода защиты."""

        self.device_id = f'site_{uuid.uuid4().hex}'
        self.query_id = f'qid{uuid.uuid4().hex[:30]}'

    def get_headers(self, query: str) -> dict:
        """
        Возвращает заголовки HTTP-запроса с id. Заголовки имитируют запрос из браузера
        """

        return {
            'Accept': '*/*',
            'Accept-Language': 'ru,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://www.wildberries.ru',
            'Referer': f'https://www.wildberries.ru/catalog/0/search.aspx?search={quote_plus(query)}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "YaBrowser";v="25.12", "Not_A Brand";v="99", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'x-requested-with': 'XMLHttpRequest',
            'x-spa-version': '14.5.6',
            'deviceid': self.device_id,
            'x-queryid': self.query_id,
        }
