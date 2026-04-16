# Парсер каталога Wildberries

Сбор товаров по запросу «пальто из натуральной шерсти» и выгрузка в xlsx.

## Установка

```bash
git clone git@github.com:tamoykinden/parser_wb.git
cd parser_wb
```

### Виртуальное окружение
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Зависимости

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python3 main.py
```

## Результат
Файлы в папке output/:

catalog.xlsx - полный каталог.
catalog_filtered.xlsx - товары с рейтингом больше или равно 4.5, ценой меньше или равно 10000 рублей, страна Россия.