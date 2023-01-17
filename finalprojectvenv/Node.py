
class TreeNode:
    _value = None
    _level = None

    def __init__(self, value, level):
        self._value = value
        self._level = level

    def getValue(self):
        return self._value

    def getLevel(self):
        return self._level