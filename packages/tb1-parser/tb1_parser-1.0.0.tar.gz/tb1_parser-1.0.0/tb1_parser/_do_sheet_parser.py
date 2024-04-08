import logging

from pandas import DataFrame

from ._regex_lib import TB1 as config
from ._sheet_parser import SheetParser
from .do_signal import DoSignal
from .signals_collection import SignalsCollection


class DoSheetParser(SheetParser):

    def __init__(self, sheet: DataFrame) -> None:
        self._logs_owner: str = self.__class__.__name__
        self._sheet = sheet

        self._result = None


    # REFACT Переписать и отдебажить метод парсинга логического значения
    def _parse_logic_value(self, input_value: str | int):
        input_value = str(input_value)
        try:
            out = int(input_value)
        except Exception as exception:
            if input_value != 'нет':
                logging.error(f'{self._logs_owner}: ошибка парсинга логического значения "{input_value}" - {exception}')
            out = None
        finally:
            return out


    def start(self) -> None:
        if not list(config['Do']['regex']['columns']['validate']['names'].keys()) == list(self._sheet):
            logging.error(f'{self._logs_owner}: передан неверный лист аналоговых сигналов')

        out = []

        for row in self._sheet.itertuples(False, 'Signal'):
            try:
                new = DoSignal()
                new.plc_module = self._parse_plc_module(row.plc_module)
                new.variable = self._parse_variable(row.variable, row.plc_module)
                new.name = self._clean_name(row.name)
                new.formated_name = self._format_signal_name(row.name)
                new.logic_value = self._parse_logic_value(row.logic_value)

                out.append(new)
                logging.info(f'{self._logs_owner}:{row.variable}: значения успешно получены')
            except Exception as error:
                logging.error(f'{self._logs_owner}:{row.variable}: ошибка парсинга - {error}')
                out.append(new)
        self._result = SignalsCollection(out)
        self._result.signals_type = 'Do'
