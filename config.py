class BaseConfig:
    """Базовые настройки парсера."""

    SEARCH_URL = 'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search'

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

    HEADERS = {
        'Accept': '*/*',
        'Accept-Language': 'ru,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://www.wildberries.ru',
        'Referer': 'https://www.wildberries.ru/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="142", "YaBrowser";v="25.12", "Not_A Brand";v="99", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'x-requested-with': 'XMLHttpRequest',
        'x-spa-version': '14.5.6',
    }

    QUERY = 'пальто из натуральной шерсти'

    REQUEST_DELAY = 0.5
