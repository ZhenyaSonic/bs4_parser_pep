from pathlib import Path

# URLs для документации
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'

# Путь к директории проекта
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'

# Форматы даты и времени
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

# Параметры загрузки
DOWNLOADS = 'downloads'

# Форматы вывода
FORMAT_PRETTY = 'pretty'
FORMAT_FILE = 'file'

# Результаты
RESULTS = 'results'

# Формат логирования
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

# Ожидаемые статусы
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active')
}
