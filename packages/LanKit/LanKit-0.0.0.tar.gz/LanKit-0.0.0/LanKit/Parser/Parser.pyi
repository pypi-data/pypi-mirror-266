"""
Предоставляет набор инструментов, для удобной
реализации собственных парсеров
"""

from typing import Any, Callable, Type, NamedTuple
from LanKit.Lexer import Token, NoneToken
from math import inf

from abc import *


PATTERN = list[Callable | str]
SUCC_PATTERN_NUM = int


class IsSet:
    """
    Класс, применяемый в классе абстрактных классах-парсерах
    * Отвечает на вопрос: "Равен ли <свойство парсера> None?"

    Например:
    ```python
    ...
    def expression_nonterm(self):
        # 2 + 3 + 4
        if self.next().name == 'SUM':
            self.jump(2)
            right = self.expression_nonterm()
            
            self.jump(-2)
            left = self.expression_term()
            
            # Тут идёт проверка: есть ли результат
            # от работы "next" в коде "if self.next().name == 'SUM':"
            if self.isSet.next:
                return left + right
    ...
    ```
    """
    def __init__(self) -> None:
        self.next: bool


class PRParser(ABC):
    """
    Абстрактный класс, который используется для создания
    ваших классов-парсеров

    PRParser - парсер, работающий по принципу
    "Процедурный-рекурсивный парсер"

    В этом классе обязательно должен быть метод "main", он
    является стартовой точкой для парсера:
    ```python
    def main(self) -> Any:
        ...
    ```

    Особенности:
    * Все методы non-terminal возвращают результат, который попадёт в "formList"
    * Разрешено создавать, удалять и изменять объекты в таком классе
    * Здесь нет контекстно-свободных граматик

    Пример:
    ```python
    # Это тестовый парсер
    class Test(PRParser):
        def __init__(self):
            pass
        
        # Эта функция - non-terminal
        def main(self):
            self.form(['PRINT', self.choose])

        # Эта функция - non-terminal
        def expression(self):
            match self.this.name:
                case 'HI':
                    print('Hi, world!')
                
                case 'HELLO':
                    print('Hello, world!')

    # Инициализация
    testParser = Test()
    testParser.build(tokens)
    ```
    """
    def __init__(self, *args, **kwargs) -> None:
        self.formList: list[Any]
        self.pointer: int
        self.isSet: IsSet
        self.resultOffset: int
        self.stopForm: bool
        listNumber = 0

    @abstractmethod
    def build(self, tokens: list[Token]):
        """
        Запускает процесс парсинга
        """

    @abstractmethod
    def notEnd(self) -> bool:
        """
        Маленькая функция, полезная при циклическом парсинге, например,
        когда речь идёт о блоке команд, и надо этот блок распарсить в
        цикле "while"
        """
        return len(self.tokens) > self.pointer

    @abstractmethod
    def form(self, *args: list[PATTERN]) -> SUCC_PATTERN_NUM:
        """
        * Функция, для форматированного поиска в текущем списке токенов.
        * В результате своей работы, устанавливает в поле "formList"
        форматированный ответ

        * Данно: [A, B, C, D, E, F]
        * Формат: form(['A', 'B', expression, 'F'])

        * expression - это функция, которая возвращает значения типа bool
        
        Ход действий:
        1. Проверит на соответствие текущих токенов в начале на 'A', 'B'
        2. Запустит указанную функцию (для передачи управления парсингом)
        """

    @abstractmethod
    def check(self, *args: list[str]) -> bool:
        """
        Проверяет: соответствуют ли поля "name" токенов, относительно
        указателя, указанным ожидаемым значениям полей "name" этих токенов

        * Данно: [A, B, C, D, E, F]
        * Указатель: B
        * Формат: check('C', 'D')
        """

    @abstractmethod
    def jump(self, steps: range[-inf, +inf]) -> None:
        """
        Функция, перемещает указатель на указанное смещение
        с учётом позиции указателя

        Список: [A, B, C, D, E, F]
        Текущая позиция: B -> jump(3) -> E
        """

    @abstractmethod
    def next(self, offset: range[-inf, +inf] = 1) -> Token | NoneToken:
        """
        Функция, которая возвращает указанный токен из текущего списка токенов
        с учётом позиции указателя

        Формат: [A, B, C, D, E, F] -> next(2) -> D
        * Текущая позиция: B
        """

    @abstractmethod
    def select(self, x1: range[-inf, +inf], x2: range[-inf, +inf]) -> list[Token]:
        """
        Функция для выбора подсписка из текущего списка токенов
        с учётом позиции указателя

        Формат: [A, B, C, D, E, F] -> select(-1, 2) -> [A, B, C, D]
        * Текущая позиция: B
        """
