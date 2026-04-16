import logging

from config import BaseConfig
from client import WildberriesClient
from save_excel import ExcelSaver
from parser import WildberriesParser


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def main():
    """Запускает парсер WB."""

    config = BaseConfig()
    client = WildberriesClient(config)
    saver = ExcelSaver(config.OUTPUT_DIR)
    parser = WildberriesParser(config, client, saver)

    query = config.QUERY

    result = parser.run(query)

    logger.info(f'Всего товаров в каталоге: {result["catalog_count"]}')
    logger.info(f'Товаров после фильтрации: {result["filtered_count"]}')
    logger.info(f'Файлы сохранены в папке: {config.OUTPUT_DIR}/')


if __name__ == '__main__':
    main()
