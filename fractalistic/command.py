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