class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""


class NoVersionsFoundError(Exception):
    """Исключение, возникающее, когда не найдены версии документации."""
