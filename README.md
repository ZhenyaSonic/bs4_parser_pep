# Проект парсинга pep
Парсер собирает информацию с сайтов https://docs.python.org/3/ и https://peps.python.org/.
У парсера 4 есть варианта работы:

whats-new собирает ссылки на статьи о нововведениях в Python, переходит по ним и забирает информацию об авторах и редакторах статей.

latest_versions cобирает информацию о статусах версий Python.

download скачивает архив с актуальной документацией Python.

pep собирает данные обо всех документах PEP и формирует таблицу со статусами PEP и количеством документов с такими статусами.

Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

git clone git@github.com:ZhenyaSonic/bs4_parser_pep.git
cd BS4_PARSER_PEP/
Создать и активировать виртуальное окружение и установить зависимости:

python -m venv venv
source venv/Scripts/activate
Обновить pip и установить зависимости:

python -m pip install --upgrade pip
pip install -r requirements.txt
Сменить директорию на src

cd src/
Запустить парсер

python main.py [вариант парсера] [аргументы]
Варианты парсера

whats-new
latest_versions
download
pep
Аргументы

-h, --help Общая информация о командах.
-c, --clear-cache Очистка кеша перед выполнением парсинга.

Дополнительные способы вывода данных:
-o pretty, --output pretty Вывод данных в командной строке в виде таблицы

-o file, --output file Сохранение информации в формате csv в папке ./results/