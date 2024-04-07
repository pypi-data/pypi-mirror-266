from ...interface import IPacker
from ...data.market.fin_persist_filed_data import FinPersistFiledData


class FinPersistSaveParamDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        tempfileds = []
        for filed in self._obj.Fileds:
            tempfileds.append(filed.obj_to_tuple())

        return [str(self._obj.TableName), str(self._obj.Range), tempfileds, bool(self._obj.Append),
                str(self._obj.BasePath)]

    def tuple_to_obj(self, t):
        if len(t) >= 5:
            self._obj.TableName = t[0]
            self._obj.Range = t[1]
            for temp in t[2]:
                fd = FinPersistFiledData()
                fd.tuple_to_obj(temp)
                self._obj.Fileds.append(fd)
            self._obj.Append = t[3]
            self._obj.BasePath = t[4]

            return True
        return False
