import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL, DOWNLOADS
from exceptions import NoVersionsFoundError
from outputs import control_output
from utils import get_response, find_tag


def parse_response(response):
    if response is None:
        return None
    return BeautifulSoup(response.text, 'lxml')


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = parse_response(response)
    if soup is None:
        return

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        soup = parse_response(response)
        if soup is None:
            logging.warning(f'''
                           Пропущена итерация для
                           {version_link}: ответ не получен или некорректен.
                           ''')
            continue
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    soup = parse_response(response)
    if soup is None:
        return
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise NoVersionsFoundError(
            'Ничего не нашлось: не найдены версии документации.'
        )
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version = a_tag.text
            status = ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    soup = parse_response(response)
    if soup is None:
        return
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a',
                          attrs={'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    log_messages = []
    amount_statuses = {}

    response = get_response(session, PEP_URL)
    soup = parse_response(response)
    if soup is None:
        return
    numerical_section = find_tag(
        soup,
        'section',
        attrs={'id': 'numerical-index'}
    )
    numerical_table = find_tag(
        numerical_section,
        'table',
        attrs={'class': 'pep-zero-table docutils align-default'}
    )
    tbody = find_tag(
        numerical_table,
        'tbody'
    )

    tr_tags = tbody.find_all('tr')
    results = [('Статус', 'Количество')]

    for tr_tag in tqdm(tr_tags):
        abbr_tag = find_tag(tr_tag, 'abbr')
        type_status = abbr_tag['title']
        status = re.search(
            r'.*, (?P<status>\w+)$',
            type_status).group('status')

        a_tag = find_tag(
            tr_tag,
            'a',
            attrs={'class': 'pep reference internal'}
        )
        pep_link = urljoin(PEP_URL, a_tag['href'])

        response = get_response(session, pep_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, 'lxml')
        abbr_tag = find_tag(soup, 'abbr')
        status_on_page = abbr_tag.text

        if status_on_page != status:
            log_messages.append(
                f'Несовпадающие статусы: {pep_link} |'
                f'Статус в таблице: {status} |'
                f'Статус на странице: {status_on_page}'
            )

        amount_statuses[status_on_page] = amount_statuses.get(
            status_on_page, 0) + 1
        if status_on_page not in {
            'Accepted',
            'Active',
            'Deferred',
            'Draft',
            'Final',
            'Provisional',
            'Rejected',
            'Superseded',
            'Withdrawn'
        }:
            log_messages.append(
                f'''
                Обнаружен неизвестный статус на странице:
                {pep_link} | {status_on_page}
            ''')

    for message in log_messages:
        logging.info(message)

    results.extend(amount_statuses.items())
    results.append(('Total', sum(amount_statuses.values())))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        logging.info('Парсер запущен!')
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(f'Аргументы командной строки: {args}')

        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)

        logging.info('Парсер завершил работу.')

    except Exception as e:
        logging.error(f'Произошла ошибка: {e}', exc_info=True)


if __name__ == '__main__':
    main()
