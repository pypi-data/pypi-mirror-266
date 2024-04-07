from ...interface import IPacker


class BaseTickDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return [str(self._obj.InstrumentID), str(self._obj.ExchangeID), str(self._obj.TradingDay), str(self._obj.ActionDay),
                str(self._obj.TradingTime), float(self._obj.LastPrice), int(self._obj.LastVolume), float(self._obj.AskPrice),
                int(self._obj.AskVolume), float(self._obj.BidPrice), int(self._obj.BidVolume)]

    def tuple_to_obj(self, t):
        if len(t) >= 11:
            self._obj.InstrumentID = t[0]
            self._obj.ExchangeID = t[1]
            self._obj.TradingDay = t[2]
            self._obj.ActionDay = t[3]
            self._obj.TradingTime = t[4]
            self._obj.LastPrice = t[5]
            self._obj.LastVolume = t[6]
            self._obj.AskPrice = t[7]
            self._obj.AskVolume = t[8]
            self._obj.BidPrice = t[9]
            self._obj.BidVolume = t[10]

            return True
        return False
