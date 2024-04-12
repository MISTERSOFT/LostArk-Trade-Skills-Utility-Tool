import datetime
from enum import Enum
from .singleton import MetaSingleton
import reactivex as rx
from reactivex import operators as rxops


class LogService(metaclass=MetaSingleton):
    class LogType(Enum):
        ERROR = 0
        SUCCESS = 1
        INFO = 2
        WARNING = 3
        DEFAULT = 4

    __push = rx.Subject()  # Triggered when a text is pushed
    __clear = rx.Subject()  # Triggered when a clear of the scan acculator is requested
    pushed = rx.merge(
        __push.pipe(rxops.map(lambda text: [text])),
        # create a empty list to clear the accumulator bellow
        __clear.pipe(rxops.map(lambda _: [])),
    ).pipe(
        # accumulate all texts in a list or reset the acculuator
        rxops.scan(lambda acc, text: [] if len(text) == 0 else [*acc, *text], []),
        # concatenate all texts together
        rxops.map(lambda texts: "<br>".join(texts)),
    )

    # ---------------
    # Public methods
    # ---------------

    def log(self, text: str, type: LogType):
        match type:
            case LogService.LogType.ERROR:
                self.__push.on_next(self.__to_html("#e74c3c", text))
            case LogService.LogType.SUCCESS:
                self.__push.on_next(self.__to_html("#2ecc71", text))
            case LogService.LogType.INFO:
                self.__push.on_next(self.__to_html("#3498db", text))
            case LogService.LogType.WARNING:
                self.__push.on_next(self.__to_html("#e67e22", text))
            case LogService.LogType.DEFAULT:
                self.__push.on_next(self.__to_html("black", text))
            case _:
                pass

    def clear(self):
        self.__clear.on_next(None)

    # ---------------
    # Private methods
    # ---------------

    def __to_html(self, color: str, text: str):
        """
        Wrap text with html tags and set a color.
        """
        return f'<font color="{color}">[{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] {text}</font>'
