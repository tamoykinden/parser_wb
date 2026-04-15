import logging
from parser import WildberriesParser

from config import BaseConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():

    config = BaseConfig()
    parser = WildberriesParser(config)

    query = config.QUERY

    logger = logging.getLogger(__name__)
    logger.info(f'Парсинг по запросу: "{query}"')

    ids = parser.get_all_priduct_ids(query)

    if ids:
        logger.info(f'Всего получено ID: {len(ids)}')
        logger.info(f'Первые 5 ID: {ids[:5]}')
        logger.info(f'Последние 5 ID: {ids[-5:]}')
    else:
        logger.warning('ID не получены')


if __name__ == '__main__':
    main()
