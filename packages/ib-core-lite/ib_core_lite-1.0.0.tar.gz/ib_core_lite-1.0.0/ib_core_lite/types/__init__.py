class _NoneDataType:
    def __init__(self):
        pass

    def __bool__(self):
        return False

    def __repr__(self):
        return "NoneData"

    def __getattr__(self, item):
        return self


NoneData = _NoneDataType()

__all__ = ['NoneData']
