from .do_signal import DoSignal


class DiSignal(DoSignal):

    def __init__(self) -> None:
        '''
        Дата-класс для дискретных выходных сигналов, потомок 'Signal -> DoSignal'.
        '''
        super().__init__()
        self.alarm_signal: None | bool
        self.warning_signal: None | bool
        self.tele_signal: None | bool
        self.error_signal: None | bool
            