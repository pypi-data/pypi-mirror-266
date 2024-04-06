from PySide6.QtCore import QObject, Signal


def create_signal(signal_type):
    """根据传入类型，创建相应的信号类。"""
    class CustomSignal(QObject):
        signal = Signal(signal_type)

    return CustomSignal()


class ResponseProgressSignal:
    """需要某个功能类继承它，并连接response_progress_signal方法到某一信号。
    然后根据需要实现各种progress_xxx方法，即可根据不同状态自动调用相应的处理方法。"""

    def response_progress_signal(self, state: tuple):
        state_flag, data = state
        if state_flag == ProgressState.flag_start:
            self.progress_start(data)
        elif state_flag == ProgressState.flag_doing:
            self.progress_doing(data)
        elif state_flag == ProgressState.flag_success:
            self.progress_success(data)
        elif state_flag == ProgressState.flag_failed:
            self.progress_failed(data)
        elif state_flag == ProgressState.flag_end:
            self.progress_end(data)
        elif state_flag == ProgressState.flag_info:
            self.progress_info(data)
        elif state_flag == ProgressState.flag_other1:
            self.progress_other1(data)
        elif state_flag == ProgressState.flag_other2:
            self.progress_other2(data)
        elif state_flag == ProgressState.flag_other3:
            self.progress_other3(data)
        else:
            raise ValueError(f'传递的信号数据错误。应该是 tuple ，但得到的是 {type(state)}')

    def progress_start(self, data: list = None):
        pass

    def progress_doing(self, data: list = None):
        pass

    def progress_success(self, data: list = None):
        pass

    def progress_failed(self, data: list = None):
        pass

    def progress_end(self, data: list = None):
        pass

    def progress_info(self, data: list = None):
        pass

    def progress_other1(self, data: list = None):
        pass

    def progress_other2(self, data: list = None):
        pass

    def progress_other3(self, data: list = None):
        pass


class ProgressState:
    """发射信号时应该使用此类来传输数据。

    Example:
        # 具体数据应使用list包裹，这利于处理复杂形态的数据。
        some_signal.emit(ProgressState.start(['处理开始']))

    """
    flag_start = 0
    flag_doing = 1
    flag_end = 2
    flag_success = 3
    flag_failed = 4
    flag_info = 5
    # 预留的其他状态量
    flag_other1 = 6
    flag_other2 = 7
    flag_other3 = 8

    @staticmethod
    def start(data: list = None) -> tuple:
        return ProgressState.flag_start, data

    @staticmethod
    def doing(data: list = None) -> tuple:
        return ProgressState.flag_doing, data

    @staticmethod
    def end(data: list = None) -> tuple:
        return ProgressState.flag_end, data

    @staticmethod
    def success(data: list = None) -> tuple:
        return ProgressState.flag_success, data

    @staticmethod
    def failed(data: list = None) -> tuple:
        return ProgressState.flag_failed, data

    @staticmethod
    def info(data: list = None) -> tuple:
        return ProgressState.flag_info, data

    @staticmethod
    def other1(data: list = None) -> tuple:
        return ProgressState.flag_other1, data

    @staticmethod
    def other2(data: list = None) -> tuple:
        return ProgressState.flag_other2, data

    @staticmethod
    def other3(data: list = None) -> tuple:
        return ProgressState.flag_other3, data
