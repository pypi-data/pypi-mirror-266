import logging
import re

from pandas import DataFrame, ExcelFile, read_excel

from ._regex_lib import TB1 as config


class TB1SheetReader:

    def __init__(self, file: ExcelFile) -> None:
        self.__logs_owner: str = self.__class__.__name__
        self.__file = file
    

    def __find_sheet_name(self, content_type: str) -> str | None:
        '''
        Приватный метод для поиска названия конкретного листа ТБ1.\n
        На входе принимает тип содержимого листа, если в либе с регулярками прописаны все его настройки.\n
        Примеры инпута: 'Ai', 'Di', 'Do'
        '''
        logging.info(f'{self.__logs_owner}:{content_type}: начало поиска названия листа в файле..')
        matches: list[str] = []
        try:
            for sheet_name in map(str, self.__file.sheet_names):
                name_pattern = config[f'{content_type}']['regex']['sheet']['validate']['name']
                if match := re.fullmatch(name_pattern, sheet_name):
                    matches.append(match.string)

            matches_count: int = len(matches)
            if matches_count == 1:
                out: str = matches[0]
                logging.info(f'{self.__logs_owner}:{content_type}: название листа успешно найдено - "{out}"')
                return out
            else:
                raise ValueError(f'некорректное число совпадений с шаблоном ({matches_count})')
            
        except Exception as error:
            logging.error(f'{self.__logs_owner}:{content_type}: ошибка поиска названия листа - {error}')
            return
    

    def __find_sheet_columns(self, content_type: str, dataframe_head: list[list]) -> dict[str:int]: # REFACT Переписать метод поиска столбцов
        '''
        Приватный метод для поиска индексов колонок конкреного листа ТБ1, перечисленных в либе регулярок.\n
        На входе тип содержимого листа и датафрейм из его шапки с названиями колонок.
        На выходе словарь с нормальизованными названиями колонок и их индексы.
        '''

        logging.info(f'{self.__logs_owner}:{content_type}: поиск столбцов для чтения..')

        columns_config = config[f'{content_type}']['regex']['columns']
        required_columns: dict = columns_config['validate']['names']
        replace_config = columns_config['replace']['trash']

        out: dict = {key:None for key in required_columns}

        # Для столбцов из либы регулярок
        try:
            for requared_column, pattern in required_columns.items():
                # logging.info(f'{self.__logs_owner}:{content_type}: поиск столбца "{requared_column}"..')
                already_found_indexes = tuple(index for index in out.values() if index is not None)

                # Для строки в массиве из инпута
                for row in dataframe_head:

                    # Для ячейки в строке
                    for cell_index, cell_value in enumerate(row):
                        if (not isinstance(cell_value, str)) or (cell_index in already_found_indexes): 
                            continue
                        
                        # Очистка содержимого ячейки от мусора
                        clear_cell_value = re.sub(replace_config['pattern'], replace_config['new_value'], cell_value)

                        if re.fullmatch(pattern, clear_cell_value):
                            logging.info(f'{self.__logs_owner}:{content_type}: '\
                                         f'столбец "{requared_column}" успешно найден - "{cell_value.replace('\n', ' ')}"')
                            out[requared_column] = cell_index
                            break
 
            if True not in tuple((xz is not None) for _, xz in out.items()):
                raise ValueError('Напомните разрабу о том, что делать такие вложенные циклы - нехорошо')
            
        except Exception as error:
            logging.error(f'{self.__logs_owner}:{content_type}: ошибка поиска столбцов - {error}')
        finally:
            return out

    
    def __read_sheet(self, content_type: str) -> None | DataFrame: # REFACT Переписать метод чтения листов
        '''
        Приватный метод для чтения конкретного листа ТБ1.
        Анализириует и нормальизует шапку, считывает только те столбцы, что указаны в либе регулярок.\n
        На входе указывается только тип искомого наполнения.
        На выходе датафрейм, с которым можно стандартно работать при помощи pandas.
        '''
        # TODO Логи
        # TODO Исключения

        # REFACT Перенести в метод валидации FileReader'а
        if not isinstance(content_type, str):
            raise TypeError(f'{type(content_type)} не является допустимым типом данных для "content_type"')
        if content_type not in list(config):
            raise ValueError(f'нет подходящего шаблона для "{content_type}" типа листов ТБ1')
        
        sheet_name: str | None = self.__find_sheet_name(content_type)
        if not sheet_name: return
        
        # Создание тестового фрейма
        test_df: DataFrame = read_excel(self.__file, sheet_name, header=None, nrows=10)

        # Поиск первой строки с контентом
        first_col_content: list = test_df.iloc[:, 0].tolist()
        for index, row in enumerate(first_col_content):
            if content_type.upper() in str(row):
                start_index: int = index
                break

        # Анализ шапки тестового датафрейма. Поиск столбцов, прописанных в либе ргулярок + их индексы
        columns: dict = self.__find_sheet_columns(
            content_type,
            list(test_df.loc[row_index].tolist() for row_index in range(start_index))
            )

        # Фильтрация только обнаруженных в ТБ1 столбцов (для предотвращения глюка с чтением содержимого столбцов)
        existing_columns: dict = {key:value for key, value in columns.items() if value is not None}
        # Сортировка по индексу
        existing_columns = dict(sorted(existing_columns.items(), key=lambda item: item[1]))

        # Чтение листа
        sheet: DataFrame = read_excel(
            self.__file,
            sheet_name,
            header = None,
            skiprows = range(0, start_index),
            usecols = ','.join(chr(i + 97) for i in existing_columns.values()).upper()
        ).ffill().drop_duplicates()
        
        # Переименование столбцов и очистка датафрейма от мусора
        sheet = sheet.rename(columns=dict(zip(list(sheet), existing_columns)))
        # sheet = sheet.loc[sheet['name'] != 'Резерв'].dropna(axis=0, how='all').reset_index() # Читать без резервов
        sheet = sheet.dropna(axis=0, how='all').reset_index() # С резервами
        del sheet['index']

        # Добавление в датафрейм столбцов, которые есть в либе регулярок, но нет в ТБ1
        if len(empty_columns := tuple(col for col in columns if col not in existing_columns)) != 0:
            logging.warning(
                f'{self.__logs_owner}: при чтении листа "{content_type}" не обнаружены столбцы: {', '.join(empty_columns)}. '\
                'Они будут созданы и заполнены принудительно.'
                )
            for empty_col in empty_columns:
                logging.warning(
                f'{self.__logs_owner}: принудительное создание и заполнение столбца "{empty_col}" для листа "{content_type}"')
                sheet[empty_col] = None
        sheet = sheet[[*columns]].copy()

        return sheet


    def get(self, content_type: str) -> None | DataFrame:
        return self.__read_sheet(content_type)