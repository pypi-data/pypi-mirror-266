from ...interface import IPacker


class FinPersistFiledDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return [int(self._obj.Day), str(self._obj.Mark), bytes(self._obj.Buffer)]

    def tuple_to_obj(self, t):
        if len(t) >= 3:
            self._obj.Day = t[0]
            self._obj.Mark = t[1]
            self._obj.Buffer = t[2]

            return True
        return False
