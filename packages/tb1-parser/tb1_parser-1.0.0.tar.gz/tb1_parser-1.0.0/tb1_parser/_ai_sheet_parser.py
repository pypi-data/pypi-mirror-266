import logging
import re

from pandas import DataFrame

from ._regex_lib import TB1
from ._sheet_parser import SheetParser
from .ai_signal import AiSignal
from .signals_collection import SignalsCollection


config = TB1['Ai']['regex']


class AiSheetParser(SheetParser):

    def __init__(self, sheet: DataFrame) -> None:
        self._logs_owner: str = self.__class__.__name__
        self._sheet = sheet

        self._result = None


    # REFACT Переписать метод парсинга единицы измерения из диапазона
    def __find_unit(self, range: str) -> str:
        out = None
        try:
            if (unit := range.split(' ')[-1]) and unit != 'нет':
                out = unit
                out = re.sub(r'\d+', '', out)
        except Exception as error:
            logging.error(f'{self._logs_owner}: ошибка поиска единицы измерения в "{range}" диапазоне измерения - {error}')
        finally:
            return out


    # REFACT Отрефакторить метод парсинга диапазонов
    def __parse_range(self, raw_range: str | None) -> list:
        start = end = None
        try:
            # Отсев пустого диапазона
            if raw_range is None or re.fullmatch(config['content']['validate']['empty_range'], raw_range):
                return start, end
            
            else:
                # Очистка инпута от мусора
                replace_methods: dict = config['content']['replace']
                for method in replace_methods:
                    method_data: dict = replace_methods.get(method)
                    pattern, new_value = (i for i in method_data.values())
                    raw_range = re.sub(pattern, new_value, raw_range)

                # Если диапазон простой
                simple_range_regex = config['content']['validate']['simple_range']
                if re.fullmatch(simple_range_regex, raw_range):
                    simple_range = re.findall(simple_range_regex, raw_range)
                    start= simple_range[0][0]
                    end = simple_range[0][2]

                else:
                    # Поиск значений в очищеном инпуте
                    matches_list = re.findall(config['content']['validate']['range_value'], raw_range)
                    matches_count = len(matches_list)

                    if matches_count == 1:
                        for match in matches_list:
                            if '<' in match[0]:
                                start = match[1]
                            elif '>' in match[0]:
                                end = match[1]
                    elif matches_count == 2:
                        start, end = [i[1] for i in matches_list]
                    else:
                        raise ValueError('некорректное число совпадений с шаблоном')

                # Финальное форматирование - конвертация в float
                format_func = \
                    lambda x: float(x.replace(',', '.')) if isinstance(x, str) else x
                out = [format_func(i) for i in (start, end)]

                # Если стартовое значение больше конечного
                if len(out) == 2 and None not in out:
                    if out[0] > out[1]:
                        logging.warning(f'{self._logs_owner}: предупреждение при получении диапазона из "{raw_range}" - некорректно заполнено в ТБ1')
                        out = sorted(out)
                        logging.warning(f'{self._logs_owner}: диапазон "{raw_range}" принудительно нормализован - {tuple(out)}')
                return out

        except Exception as exception:
            logging.error(f'{self._logs_owner}: ошибка получения диапазона из "{raw_range}" - {exception}')
            return [*['parse_error']*2]

    
    def start(self) -> None:
        if not list(config['columns']['validate']['names'].keys()) == list(self._sheet):
            logging.error(f'{self._logs_owner}: передан неверный лист аналоговых сигналов')

        out = []

        for row in self._sheet.itertuples(False, 'Signal'):
            try:
                new = AiSignal()
                new.plc_module = self._parse_plc_module(row.plc_module)
                new.variable = self._parse_variable(row.variable, row.plc_module)
                new.name = self._clean_name(row.name)
                new.formated_name = self._format_signal_name(row.name)
                new.unit = row.unit if row.unit else self.__find_unit(row.range)
                new.LL, new.HL = self.__parse_range(row.range)
                new.LW, new.HW = self.__parse_range(row.warning_range)
                new.LA, new.HA = self.__parse_range(row.alarm_range)
                new.LE, new.HE = self.__parse_range(row.error_range)
                # TODO Написать валидацию границ уставок

                out.append(new)
                logging.info(f'{self._logs_owner}:{row.variable}: значения успешно получены')
            except Exception as error:
                logging.error(f'{self._logs_owner}:{row.variable}: ошибка парсинга - {error}')
                out.append(new)
        self._result = SignalsCollection(out)
        self._result.signals_type = 'Ai'
