import logging
import re

from pandas import DataFrame
from transliterate import translit

from ._regex_lib import PARSER as config
from .signals_collection import SignalsCollection


class SheetParser:

    def __init__(self, sheet: DataFrame) -> None:
        self._logs_owner: str = self.__class__.__name__
        self._sheet = sheet

        self._result = None


    def _clean_name(self, input_value: str):
        return input_value.replace('\n', '')


    # REFACT Отрефакторить метод поиска количества каналов для модуля
    def _find_count_plc_channels(self, raw_plc_module: str):
        try:
            sheet: DataFrame = self._sheet
            count: int = len(sheet[sheet['plc_module'] == raw_plc_module])
            return count
        except Exception as exception:
            pass
        finally:
            pass


    def _parse_variable(self, raw_variable: str, raw_plc_module: str) -> int | tuple[int]:
        type_regex = r'^\D{2}'
        clean_input = lambda x: re.sub(type_regex, '', x)
        clear_variable = clean_input(raw_variable)
        try:
            if 'ai' in raw_variable.lower():
                out = int(clear_variable)
            else:
                out = nums = tuple(map(int, clear_variable.split('-')))

        except ValueError as value_error:
            logging.warning(f'{self._logs_owner}: некорректный номер переменной "{raw_variable}"')
            count_plc_channels = self._find_count_plc_channels(raw_plc_module)
            nums = tuple(map(int, clear_variable.split('-')))

            if len(nums) == 2:
                logging.info(f'{self._logs_owner}: вычисление порядкового номера "{raw_variable}"')
                out = count_plc_channels * nums[0] + nums[1]
                logging.warning(f'{self._logs_owner}: номер переменной "{raw_variable}" принудительно нормализован - "{out}"')
            else:
                raise ValueError('попытка вычисления порядкового номера переменной провалена')
            
        except Exception as exception:
            logging.error(f'{self._logs_owner}: ошибка парсинга "{raw_variable}" переменной - {type(exception).__name__}:{exception}')
            out = None

        finally:
            return out

    
    # REFACT Переписать метод транслитерациии названия параметра
    def _format_signal_name(self, name: str) -> str:
        replace_data = config['signals']['format_variable_name']
        try:
            for key, value in replace_data.items():
                name = re.sub(key, value, name)
            name = translit(name, 'ru', reversed=True)
            name = re.split(r'\s+|\-|\,', name)
            name = (word for word in name if word != '')
            name = '_'.join(name).replace('\'', '')
            out: str = name
        except Exception as error:
            logging.error(f'{self._logs_owner}: ошибка транслитерации "{name}" названия параметра - {error}')
            out = None
        finally:
            return out
    

    # REFACT Переписать метод парсинга канала модуля плк
    def _parse_plc_module(self, raw_string: str) -> str:
        try:
            out = re.findall(config['signals']['find_plc_module'], raw_string)[0][1:]
            out = tuple(map(int, out))
            if not out:
                raise ValueError('ошибка сопоставления с шаблоном')
        except Exception as error:
            logging.error(f'{self._logs_owner}: ошибка парсинга "{raw_string.replace('\n', '')}" модуля плк - {error}')
            out = None
        finally:
            return out


    def get_result(self) -> SignalsCollection | None:
        if out := self._result:
            return out
        else:
            logging.error(f'{self._logs_owner}: перед получением результатов парсинга воспользуйтесь методом start()')
            raise IndentationError