class Command():
    # No type definition for funct because of weird behaviour
    # of linter due to assignment to a Callable

    help: str

    def __init__(self, funct, help: str):
        self.funct = funct
        self.help = help