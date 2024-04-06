from enum import Enum

class PatchOperation(str, Enum):
    """
    Enum class for defining the operation of a settings patch.
    """
    Add = "add"
    Replace = "replace"
    Test = "test"
    Remove = "remove"
    Move = "move"
    Copy = "copy"
