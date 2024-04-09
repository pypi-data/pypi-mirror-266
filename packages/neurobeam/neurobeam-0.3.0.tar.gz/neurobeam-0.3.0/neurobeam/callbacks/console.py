from ..tools import FORMAT_TERMINAL


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// REPORTING CALLBACKS (CONSOLE)
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


def reporting_console_start() -> None:
    print(FORMAT_TERMINAL("PROBE STARTED", "header"))


def reporting_console_stop() -> None:
    print(FORMAT_TERMINAL("PROBE STOPPED", "header"))


def reporting_console_task_start() -> None:
    print(FORMAT_TERMINAL("TASK STARTED", "header"))


def reporting_console_task_finished() -> None:
    print(FORMAT_TERMINAL("TASK FINISHED", "header"))


def reporting_console_concluded() -> None:
    print(FORMAT_TERMINAL("PROBE CONCLUDED", "header"))


def reporting_console_progress_state(state: str, progress: float) -> None:
    print(FORMAT_TERMINAL(f"{state} Progress: ", "local_progress") + f"{progress:.0f}%")


def reporting_console_progress_task(task: str, progress: float) -> None:
    print(FORMAT_TERMINAL(f"{task.capitalize()} Progress: ", "global_progress") + f"{progress:.0f}%")
