import logging
import sys
from typing import Literal

from pandas import DataFrame, ExcelFile

from ._regex_lib import TB1 as config
from ._tb1_sheet_reader import TB1SheetReader
from ._tb1_readed_sheets_collection import TB1ReadedSheetsCollection


all_avaible_sheets = list(config)


class TB1FileReader:

    def __init__(self, filepath: str) -> None:
        self.__logs_owner: str = self.__class__.__name__
        self.__filepath = filepath

        self.sheets: TB1ReadedSheetsCollection[str, DataFrame] = {}


    def __read_file(self) -> ExcelFile:
        logging.info(f'{self.__logs_owner}: открытие файла "{self.__filepath}"..')
        try:
            excel_file = ExcelFile(self.__filepath)
            logging.info(f'{self.__logs_owner}: файл успешно открыт')
            return excel_file
        except Exception as error:
            logging.error(f'{self.__logs_owner}: не удалось открыть файл - {error}')
            sys.exit(1)


    def isvalid_sheet_type(self, input: str) -> bool:
        return input in all_avaible_sheets


    def read(self, sheets: str | list[Literal['Ai', 'Di', 'Do']] = all_avaible_sheets):
        logging.info(f'{self.__logs_owner}: начало чтения ТБ1..')

        if not self.isvalid_sheet_type(sheets):
            pass

        sheet_reader = TB1SheetReader(self.__read_file())

        if isinstance(sheets, list):
            for sheet in sheets:
                self.sheets[sheet] = sheet_reader.get(sheet)
        if isinstance(sheets, str):
            self.sheets[sheets] = sheet_reader.get(sheets)


    def get(self, sheet: Literal['Ai', 'Di', 'Do']):
        return self.sheets.get(sheet)