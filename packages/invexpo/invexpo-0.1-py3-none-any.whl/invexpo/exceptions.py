class ArgumentError(Exception):
    pass

class NotFittedError(Exception):
    def __init__(self, method_name) -> None:
       super().__init__(f"You must fit() some data before calling {method_name}().") 
