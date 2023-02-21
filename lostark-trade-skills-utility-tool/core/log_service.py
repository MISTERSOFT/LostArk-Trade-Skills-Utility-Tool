import datetime
from .singleton import MetaSingleton
import reactivex as rx
from reactivex import operators as rxops


class LogService(metaclass=MetaSingleton):
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

    def push_error(self, text: str):
        """
        Emit an error text.
        """
        self.__push.on_next(self.__to_html("#e74c3c", text))

    def push_success(self, text: str):
        """
        Emit a success text.
        """
        self.__push.on_next(self.__to_html("#2ecc71", text))

    def push_info(self, text: str):
        """
        Emit an information text.
        """
        self.__push.on_next(self.__to_html("#3498db", text))

    def push_warning(self, text: str):
        """
        Emit a warning text.
        """
        self.__push.on_next(self.__to_html("#e67e22", text))

    def push_default(self, text: str):
        """
        Emit a simple text.
        """
        self.__push.on_next(self.__to_html("black", text))

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
