class LexingError(Exception):
    def __init__(self, charnum):
        message = f'Ошибка в {charnum}'
        super().__init__(message)