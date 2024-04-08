import logging

from ._ai_sheet_parser import AiSheetParser
from ._di_sheet_parser import DiSheetParser
from ._do_sheet_parser import DoSheetParser
from ._tb1_file_reader import TB1FileReader
from ._tb1_readed_sheets_collection import TB1ReadedSheetsCollection
from .parsed_tb1_collection import ParsedTB1Collection


class TB1Parser:

    def __init__(self, filepath: str) -> None:
        self.__logs_owner: str = self.__class__.__name__
        self.__filepath: str = filepath

        self.collection: ParsedTB1Collection = {}


    def read(self):
        try:
            file_reader = TB1FileReader(self.__filepath)
            file_reader.read()

            readed_sheets: TB1ReadedSheetsCollection = file_reader.sheets

            for sheet_type, sheet_dataframe in readed_sheets.items():
                logging.info(f'{self.__logs_owner}:{sheet_type}: начало парсинга..')
                match sheet_type:
                    case 'Ai':
                        parser = AiSheetParser(sheet_dataframe)
                    case 'Di':
                        parser = DiSheetParser(sheet_dataframe)
                    case 'Do':
                        parser = DoSheetParser(sheet_dataframe)
                    case _:
                        raise ValueError('передан неопознанный тип листа')
                parser.start()
                self.collection[sheet_type] = parser.get_result()
        except Exception as error:
            logging.error(f'{self.__logs_owner}: ошибка парсинга входных листов - {error}')
