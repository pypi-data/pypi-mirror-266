from ..tools import FORMAT_TERMINAL


def announcement(message: str) -> None:
    print(FORMAT_TERMINAL(message, "announcement"))
