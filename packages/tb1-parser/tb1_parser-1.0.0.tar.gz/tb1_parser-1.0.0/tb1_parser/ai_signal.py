from .signal import Signal


class AiSignal(Signal):

    def __init__(self) -> None:
        '''
        Дата-класс для аналоговых входных сигналов, потомок 'Signal'.
        '''
        super().__init__()
        self.unit: None | str
        self.LL: None | float
        self.LA: None | float
        self.LW: None | float
        self.HW: None | float
        self.HA: None | float
        self.HL: None | float
        self.LE: None | float
        self.HE: None | float
