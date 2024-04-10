import re

from typing import Callable
from LanKit.errors import *


LEXER_RULE = dict[str, list[str]]
LEXER_IGNORE = tuple[list[str]]

# Номер символа в коде
LEXING_ERROR_CHAR_NUMBER = int
USER_ITERRULE_PARAM = tuple[str, tuple[str, int], re.Match]
USER_ITERIGNORE_PARAM = tuple[tuple[str, int], re.Match]


class Token:
    __slots__ = ('value', 'name', 'objMatch')
    name: str
    value: str
    objMatch: re.Match


class NoneToken:
    def __init__(self) -> None:
        self.name = self.value = self.objMatch = None


class Lexer:
    __slots__ = ('rules', 'ignore', 'code', 'errorHandler', 'iterRuleHandler', 'iterIgnoreHandler')


    def __std_error_handler(error: LEXING_ERROR_CHAR_NUMBER):
        print(error)


    def __init__(self, rules: LEXER_RULE, ignore=LEXER_IGNORE) -> None:
        self.rules = rules
        self.ignore = ignore

        self.errorHandler = self.__std_error_handler
        self.iterRuleHandler = None
        self.iterIgnoreHandler = None
    

    def build(self, code: str) -> list[Token]:
        self.code = code
        tokens: list[Token] = []
        charnum = 0

        while charnum < len(self.code):
            # Получаем результат из rule
            resultMatch = self.__match_rule(self.code[charnum:])

            # Если результат есть
            if resultMatch:
                tokens.append(resultMatch)
                charnum += resultMatch.objMatch.regs[0][1]
                continue
            
            # Если результата нет
            if not resultMatch:
                resultMatch = self.__match_ignore(self.code[charnum:])

            # Если результат есть
            if resultMatch:
                charnum += resultMatch.regs[0][1]

            elif self.errorHandler:
                self.errorHandler('хуй пососи')
                raise LexingError(charnum)

            else:
                raise LexingError(charnum)
        
        return tokens


    def __match_rule(self, code) -> Token | None:
        for ruleName, ruleSettings in self.rules.items():
            rule, flags = ruleSettings
            result: re.Match = re.match('^' + rule, code, flags=re.M | flags)

            if result:
                # Если разраб хочет тонко настраивать создание токенов
                if self.iterRuleHandler:
                    # Передаём такое: ( 'NAME', (r'\d+', 0), re.Match(...) )
                    iterFuncResult = self.iterRuleHandler( (ruleName, ruleSettings, result) )
                    # Если результат кастом. итерации - None, то не подменяем результат
                    if iterFuncResult:
                        return iterFuncResult
                    
                token = Token()
                token.name = ruleName
                token.value = result.group(0)
                token.objMatch = result
                
                return token
            
    def __match_ignore(self, code) -> Token | None:
        for ruleIngore in self.ignore:
            rule, flags = ruleIngore
            result: re.Match = re.match('^' + rule, code, flags=re.M | flags)

            # Если разраб хочет тонко настраивать итарацию
            # Передаём такое: ( r'\d+', 0), re.Match(...) )
            if self.iterIgnoreHandler:
                self.iterIgnoreHandler((ruleIngore, result))

            return result


    def iterRule(self, func) -> Callable:
        def params(rule):
            pass

        self.iterRuleHandler = func
        return params
    

    def iterIgnore(self, func) -> Callable:
        def params(rule):
            pass

        self.iterIgnoreHandler = func
        return params
    

    def error(self, func) -> Callable:
        def params(rule):
            return func
        
        self.errorHandler = func
        return params
