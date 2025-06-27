class Priority(int):

    ALL = -1
    URGENT = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

    def __init__(self, value):
        super().__init__()