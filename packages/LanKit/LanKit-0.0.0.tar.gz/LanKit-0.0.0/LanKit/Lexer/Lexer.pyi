"""
Модуль для описания работы лексера
"""

from typing import Callable
from re import Match


LEXER_RULE = dict[str, list[str]]
LEXER_IGNORE = tuple[list[str]]

# Номер символа в коде
LEXING_ERROR_CHAR_NUMBER = int
USER_ITERRULE_PARAM = tuple[str, tuple[str, int], Match]
USER_ITERIGNORE_PARAM = tuple[tuple[str, int], Match]


class Token:
    """
    Токен - итог работы лексера
    * name - маркер для именования значения
    * value - итог работы лексера (конкретное значение)
    * objMatch - объект, который получился в результате вычисления токена
    """
    value: str
    name: str
    objMatch: Match


class NoneToken:
    """
    Это токен (Token), но с константными, пустыми полями
    """
    __slots__ = ('value', 'name', 'objMatch')
    name = None
    value = None
    objMatch = None



class Lexer:
    """
    Описания лексера
    """
    
    def __init__(self, rules: LEXER_RULE, ignore=LEXER_IGNORE) -> None:
        """
        rules:
        * Описание: соотнесение имени токена с его ожидаемым значение
        * Формат: <имя токена>: (<регулярное выражение>, <флаги регулярного выражения>)

        ignore:
        * Описание: соотнесение имени токена с его ожидаемым значение, и пропуск этого токена
        * Формат: (<регулярное выражение>, <флаги регулярного выражения>)

        Пример:
        ```
        ...
        lexer = Lexer(
            rules={
                'STR': (r'.*?', 0)
            },
            ignore=(
                (r'\s+', 0)
            )
        )
        ...
        ```
        """
    
    def build(self) -> list[Token]:
        """
        Возвращает токены, запускает лексер
        """

    def iterIgnore(self, func: Callable[[USER_ITERIGNORE_PARAM]]) -> Callable:
        """
        * Это декоратор
        * Работает также, как и "iterRule"
        * Он позволяет более тонко контролировать процесс получения
        токенов из исходного кода, **а конкретнее - те что из
        словаря "ignore", который вы передаёте в конструктор "Lexer"**

        * "func" - функция, которая принимает в свой 1 параметр (с любым названием)
        кортеж вида "USER_ITERIGNORE_PARAM"
        * Такая функция ничего не возвращает

        Пример:
        ```
        ...
        @lexer.iterIgnore
        def index(result):
            print(result[0]) # (r'\".*?\"', 0)
            print(result[1]) # re.Match(...)
        ...
        ```
        """

    def iterRule(self, func: Callable[[USER_ITERRULE_PARAM], None | Token]) -> Callable:
        """
        * Это декоратор
        * Работает также, как и "iterRule"
        * Он позволяет более тонко контролировать процесс получения
        токенов из исходного кода, **а конкретнее - те что из
        словаря "ignore", который вы передаёте в конструктор "Lexer"**

        * "func" - функция, которая принимает в свой 1 параметр (с любым названием)
        кортеж вида "USER_ITERRULE_PARAM"
        * Такая функция возвращает что то одно из:
            * None - не добавлять найденное совпадение в список токенов
            * Token - токен, оторый он добавит в список токенов

        Пример:
        ```
        ...
        @lexer.iterRule
        def index(result):
            print(result[0]) # 'STR'
            print(result[1]) # (r'\".*?\"', 0)
            print(result[2]) # re.Match(...)
        ...
        ```
        """

    def error(self, func: LEXING_ERROR_CHAR_NUMBER):
        """
        * Это декоратор
        * Отслежевание ошибок
        """