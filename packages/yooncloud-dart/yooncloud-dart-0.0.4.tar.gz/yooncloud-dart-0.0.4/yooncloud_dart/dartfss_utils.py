# -*- coding: utf-8 -*-
"""
dart_fss 라이브러리의 utils 함수들을 한 모듈로 다이어트 시킨 파일입니다.
여기부터 아래 코드는 utils.datatime.py
"""
from typing import  Union
from datetime import datetime

str_or_datetime = Union[str, datetime]


def get_datetime(date: str_or_datetime) -> datetime:
    """ 문자열을 datetime올 변환

    Parameters
    ----------
    date: str or datetime
        datetime 문자열

    Returns
    -------
    datetime
        변환된 datetime

    """
    if isinstance(date, str):
        return datetime.strptime(date, '%Y%m%d')
    elif isinstance(date, datetime):
        return date
    else:
        raise ValueError('Invalid datetime format')


def check_datetime(date: str_or_datetime,
                   start_date: str_or_datetime = None,
                   end_date: str_or_datetime = None) -> bool:
    """ Date가 올바른지 체크하는 함수

    Parameters
    ----------
    date: str or datetime
        체크할 값
    start_date: str or datetime
        시작 일자
    end_date: str or datetime
        종료 일자

    Returns
    -------
    bool
        Date가 start_date와 end_date 사이에 있는지 여부
    """
    date = get_datetime(date)
    if start_date is not None:
        start_date = get_datetime(start_date)
        if date < start_date:
            return False
    if end_date is not None:
        end_date = get_datetime(end_date)
        if date > end_date:
            return False
    return True


"""
여기부터 아래 코드는 utils.regex.py
"""

# -*- coding: utf-8 -*-
import re


def is_operator(item):
    """  연산자 여부 검색

    Parameters
    ----------
    item : str
        단어

    Returns
    -------
    bool
        True: 연산자 / False: 일단단어

    """
    if item in ['AND', 'OR']:
        return True
    return False


def precedence(symbol):
    """ 연산자 우선수위

    Parameters
    ----------
    symbol: str
        연산자

    Returns
    -------
    int
        연산자 순위

    """
    if symbol in ['AND', 'OR']:
        return 1
    return 0


def infix_to_postfix(infix):
    """ infix를 postfix로 변환하는 함수

    Parameters
    ----------
    infix: str
        infix 형태로 표현된 문장

    Returns
    -------
    str
        postfix로 변횐된 문장
    """
    stack = []
    results = []
    parenthesis = 0
    for item in infix:
        if item == '(':
            parenthesis = parenthesis + 1
            stack.append(item)
        elif item == ')':
            parenthesis = parenthesis - 1
            if parenthesis < 0:
                raise SyntaxError('Missing left parentheses.')
            while stack[-1] != '(':
                v = stack.pop()
                results.append(v)
            stack.pop()
        elif is_operator(item):
            if len(stack) > 0:
                if precedence(stack[-1]) < precedence(item):
                    stack.append(item)
                else:
                    v = stack.pop()
                    stack.append(item)
                    results.append(v)
            else:
                stack.append(item)
        else:
            results.append(item)
    while len(stack) > 0:
        results.append(stack.pop())

    if parenthesis > 0:
        raise SyntaxError('Missing right parentheses.')

    return results


def str_to_regex(query):
    """ regular expression

    Parameters
    ----------
    query: str
        검색 문구

    Returns
    -------
    Pattern
        regular expression pattern
    """
    return re.compile(str_to_pattern(query))


def str_to_pattern(query):
    """ AND OR 등 연산자를 regular expression 표현으로 변경

    Parameters
    ----------
    query: str
        검색 문구

    Returns
    -------
    str
        검색 pattern
    """
    query = query.replace('(', ' ( ').replace(')', ' ) ').split()
    postfix = infix_to_postfix(query)

    stack = []
    for item in postfix:
        if is_operator(item):
            if item == 'AND':
                operand1 = stack.pop()
                operand2 = stack.pop()
                pattern = r'(?=.*{0})(?=.*{1})'.format(operand2, operand1)
            elif item == 'OR':
                operand1 = stack.pop()
                operand2 = stack.pop()
                pattern = r'({0}|{1})'.format(operand2, operand1)
            stack.append(pattern)
        else:
            stack.append(item)
    return stack.pop()


"""
여기부터 아래 코드는 utils.string.py
"""

import re
from typing import Union


CURRENCY = {
    '원': 'KWR',
    '달러': 'USD',
    '엔': 'JPY',
}


def str_compare(str1: str, str2: str) -> bool:
    """문자열 비교

    Parameters
    ----------
    str1: str
        string
    str2: str
        string

    Returns
    -------
    bool
        문자열이 동일하다면 True
    """
    if not isinstance(str1, str) or not isinstance(str2, str):
        return False
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()
    return str1 == str2


def str_unit_to_number_unit(str_unit: str) -> int:
    """ 통화 단위를 숫자로 변화

    Parameters
    ----------
    str_unit: str
        통화 단위

    Returns
    -------
    int
        환산값
    """
    str_unit = re.sub(r'\s+', '', str_unit)

    str_unit_to_unit = {
        '억원': 100000000,
        '천만원': 10000000,
        '백만원': 1000000,
        '십만원': 100000,
        '만원': 10000,
        '천원': 1000,
        '백원': 100,
        '십원': 10,
    }

    for k, v in CURRENCY.items():
        str_unit_to_unit[k] = 1
        str_unit_to_unit[v] = 1

    return str_unit_to_unit[str_unit]


def get_currency_str(unit: str) -> Union[str, None]:
    regex_str = ' OR '.join(CURRENCY.keys())
    str_unit = str_to_regex(regex_str).search(unit)
    if str_unit:
        str_unit = str_unit.group(0)
        return CURRENCY[str_unit]

    regex_str = ' OR '.join([v for _, v in CURRENCY.items()])
    str_unit = str_to_regex(regex_str).search(unit)
    if str_unit:
        return str_unit.group(0)

    return None


__all__ = ['check_datetime', 'str_compare', 'str_unit_to_number_unit', 'get_currency_str', 'str_to_regex']