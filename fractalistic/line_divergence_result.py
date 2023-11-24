class LineDivergenceResult():
    y: int
    values: list[int]

    def __init__(self, y: int, values: list[int]):
        self.y = y
        self.values = values
