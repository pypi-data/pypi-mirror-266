from dbt.events.base_types import (
    InfoLevel,
)
from typing import Dict
import colorama
from dbt.events.format import format_fancy_output_line

COLORS: Dict[str, str] = {
    "red": colorama.Fore.RED,
    "green": colorama.Fore.GREEN,
    "yellow": colorama.Fore.YELLOW,
    "blue": colorama.Fore.BLUE,
    "reset_all": colorama.Style.RESET_ALL,
}


def color(text: str, color_code: str) -> str:
    return "{}{}{}".format(color_code, text, COLORS["reset_all"])


def yellow(text: str) -> str:
    return color(text, COLORS["yellow"])


def red(text: str) -> str:
    return color(text, COLORS["red"])


def blue(text: str) -> str:
    return color(text, COLORS["blue"])


class LogModelResult(InfoLevel):
    def code(self) -> str:
        return "IK001"

    def message(self) -> str:

        if self.index == 0 and self.total == 0:
            info = "OK"
            status = yellow("NONE TEST")
        elif self.status == "error":
            info = "ERROR creating"
            status = red("UNIT TEST")
        else:
            info = "OK created"
            status = blue("UNIT TEST")

        msg = f"{info} {self.description}"
        return format_fancy_output_line(
            msg=msg,
            status=status,
            index=self.index,
            total=self.total,
            execution_time=self.execution_time,
        )
