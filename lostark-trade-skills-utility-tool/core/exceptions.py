class LostArkProcessNotFound(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Not able to find Lost Ark process. Make sure the game is running."
        )
