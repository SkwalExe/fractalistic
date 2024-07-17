from collections.abc import Callable, Sequence
from typing import Optional


class Command:
    # No type definition for funct because of weird behaviour
    # of linter due to assignment to a Callable

    help: str
    accepted_arg_counts: int
    extra_help: str | None

    def __init__(
        self,
        funct: Callable,
        hlp: str,
        accepted_arg_counts: list[int],
        extra_help: str | None = None,
    ) -> None:
        self.funct = funct
        self.help = hlp
        self.accepted_arg_count = accepted_arg_counts
        self.extra_help = extra_help


class CommandIncrementArgParseResult:
    success: bool = False
    error_message: str | None = None
    new_value: int | float | None = None


class CommandIncrement(Command):
    min_value: int | None
    max_value: int | None
    app_attribute: str

    def __init__(
        self,
        app_attribute: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        *args,  # noqa: ANN002
        **kwargs,  # noqa: ANN003
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
            extra_help=(
                "[green]Usage : +/- \\[value].\n"
                "Usage : \\[value].\n"
                "Usage : no args.[/green]\n"
                "- If no arguments are passed, the current value is printed out.\n"
                "- If no sign is specified but an argument is provided, the value is set to the one specified.\n"
                "- If a sign is specified, the value is incremented or decremented by the second argument."
            ),
            accepted_arg_counts=[0, 1, 2],
        )
        self.max_value = max_value
        self.min_value = min_value
        self.app_attribute = app_attribute

    def parse_args(self, current_attrib_value: int, args: Sequence[str]) -> CommandIncrementArgParseResult:
        """Returns the new attribute value if the args are valid, else None"""
        result = CommandIncrementArgParseResult()

        # len(args) == 0 is handled by app.py:parse_command

        # If there is only one argument, it must be an absolute value to set the parameter to.
        if len(args) == 1:
            try:
                result.new_value = int(args[0])
            except ValueError:
                result.error_message = "[red]The value must be an integer"
                return result

        # If there are two arguments, it must be of the form "+/- increment"
        elif len(args) == 2:
            sign = args[0]
            value = args[1]

            if sign not in ["+", "-"]:
                result.error_message = f"[red]Unknown sign: {sign}"
                return result

            try:
                value = int(value)
            except ValueError:
                result.error_message = "[red]The increment value must be an integer"
                return result

            result.new_value = current_attrib_value + (value if sign == "+" else -value)

        # We must handle this case to make pyright hapy
        else:
            raise Exception("Invalid number of command argument provided to CommandIncrement.parse_args()")

        # Check that the new value is inside the configured bounds -------------------------------
        if self.min_value is not None and result.new_value < self.min_value:
            result.error_message = f"[red]The new value must be greater than {self.min_value}"
            return result

        if self.max_value is not None and result.new_value > self.max_value:
            result.error_message = f"[red]The new value must not be greater than {self.max_value}"
            return result
        # ----------------------------------------------------------------------------------------

        result.success = True
        return result
