from inspect import cleandoc

class Command():
    # No type definition for funct because of weird behaviour
    # of linter due to assignment to a Callable

    help: str
    accepted_arg_counts: int
    extra_help: str | None
    
    def __init__(self, funct, help: str, accepted_arg_counts: list[int], extra_help: str | None = None):
        self.funct = funct
        self.help = help
        self.accepted_arg_count = accepted_arg_counts
        self.extra_help = extra_help

class CommandIncrementArgParseResult():
    success: bool = False
    error_message: str | None = None
    new_value: int | float | None = None


class CommandIncrement(Command):
    min_value: int | None
    max_value: int | None
    app_attribute: str

    def __init__(self, app_attribute: str, min_value = None, max_value = None, *args, **kwargs):
        super().__init__(
            *args, 
            **kwargs, 
            extra_help=cleandoc(
                """
                [green]Usage : +/- \\[value].
                Usage : \\[value].
                Usage : no args.[/green]
                - If no arguments are passed, the current value is printed out.
                - If no sign is specified but an argument is provided, the value is set to the one specified.
                - If a sign is specified, the value is incremented or decremented by the second argument.\
                """
            ), 
            accepted_arg_counts=[0, 1, 2]
        )
        self.max_value = max_value
        self.min_value = min_value
        self.app_attribute = app_attribute



    def parse_args(self, current_attrib_value, args):
        """Returns the new value if the args are valid, else None"""
        result = CommandIncrementArgParseResult()
        if len(args) == 0:
            result.error_message = f"The value is currently set to [blue]{current_attrib_value}"
            return result

        elif len(args) == 1:
            try:
                result.new_value = int(args[0])
            except ValueError:
                result.error_message = "[red]The value must be an integer"
                return result
        
        elif len(args) == 2:
            sign = args[0]
            value = args[1]

            if not sign in ["+", "-"]:
                result.error_message = f"[red]Unknown sign: {sign}"
                return result
            
            try:
                value = int(value)
            except ValueError:
                result.error_message = "[red]The increment value must be an integer"
                return result
            
            result.new_value = current_attrib_value + (value if sign == "+" else -value)

        if not self.min_value is None and result.new_value < self.min_value:
            result.error_message = f"[red]The new value must be greater than {self.min_value}"
            return result

        if not self.max_value is None and result.new_value > self.max_value:
            result.error_message = f"[red]The new value must not be greater than {self.max_value}"
            return result
        
        result.success = True
        return result