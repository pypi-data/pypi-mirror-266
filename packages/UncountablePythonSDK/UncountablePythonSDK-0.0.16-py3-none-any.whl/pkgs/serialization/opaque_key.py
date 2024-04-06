# Blocks a string key value from being interpreted for case conversion
class OpaqueKey(str):
    def __new__(cls, key: str) -> "OpaqueKey":
        return str.__new__(cls, key)
