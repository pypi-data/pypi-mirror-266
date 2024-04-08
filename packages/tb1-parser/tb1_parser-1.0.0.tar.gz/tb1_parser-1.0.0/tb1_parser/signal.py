from dataclasses import dataclass


@dataclass
class Signal(object):
    
    def __init__(self) -> None:
        '''
        Дата-класс. Шаблон для наследования.
        '''
        self.variable: None | str
        self.name: None | str
        self.formated_name: None | str
        self.plc_module: None | int | tuple[int]


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str(self.__dict__)[1:-1]})'
    

    def isreserv(self) -> bool:
        return self.name.lower() == 'резерв'