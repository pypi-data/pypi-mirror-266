from LanKit.Lexer import Token, NoneToken


class IsSet:
    def __init__(self) -> None:
        self.next: bool


class PRParser:
    def __init__(self, *args, **kwargs):
        self.formList = []  # Результат форм
        self.pointer = 0  # Указатель на текущий токен
        self.isSet = IsSet()  # Информация о устанвках полей
        self.resultOffset = 0  # Результирующее смещение после form
        self.notStopForm = True  # Не выходить ли из парсинга паттерна? (form)
        self.__listOffset = 0 # смещение подсписка основного списка токенов

    
    def build(self, tokens):
        self.tokens = tokens
        self.main()


    def form(self, *args: list[list[str, callable]]):
        self.__listOffset = 0
        # то, что станет formResult (fromList)
        result = []
        # номер текущего паттерна переданного списка
        listNumber = 0

        # шарпаем по BNF списку
        for pattern in args:
            # выбираем строку/функцию
            for part in pattern:
                if isinstance(part, str):
                    if part == self.tokens[self.pointer + self.__listOffset].name:
                        result.append( self.tokens[self.pointer + self.__listOffset] )
                        self.__listOffset += 1
                    else:
                        # если часть не подошла, то перебераем след. паттерн
                        listNumber += 1
                        break

                elif callable(part):
                    # вхождение
                    self.pointer += self.__listOffset
                    funcResult = part()
                    self.pointer -= self.__listOffset
                    # маршрутизация ответа
                    if self.notStopForm:
                        self.__listOffset += self.resultOffset
                        self.resultOffset = 0
                        result.append(funcResult)
                    else:
                        self.__listOffset = 0
                        listNumber += 1
                        self.resultOffset = 0
                        break

                # если часть не типа str/callable
                else:
                    raise TypeError(part)
                
                # если паттерн закончился
                if len(result) == len(pattern):
                    self.formList = result
                    self.pointer += self.__listOffset
                    return listNumber
    

    def notEnd(self):
        return len(self.tokens) > self.pointer


    def jump(self, steps):
        self.pointer += steps


    def next(self, offset = 1):
        if offset + self.pointer <= len(self.tokens):
            self.isSet.next = True
            return self.tokens[offset + self.pointer]
        
        self.isSet.next = False
        return NoneToken()
    

    def select(self, x1, x2):
        left = (x1 + self.pointer <= len(self.tokens)) and (x1 + self.pointer >= 0)
        right = (x2 + self.pointer <= len(self.tokens)) and (x2 + self.pointer >= 0)
        
        if left and right:
            return self.tokens[x1: x2] if x1 < x2 else self.tokens[x2: x1]
