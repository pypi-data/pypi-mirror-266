from ...interface import IData
from ...packer.market.basetick_data_packer import BaseTickDataPacker


class BaseTickData(IData):
    def __init__(self, instrument_id: str = '', exchange_id: str = '', trading_day: str = '', action_day: str = '',
                 trading_time: str = '', last_price: float = 0.0, last_volume: int = 0, ask_price: float = 0.0,
                 ask_volume: int = 0, bid_price: float = 0.0, bid_volume: int = 0):
        super().__init__(BaseTickDataPacker(self))
        self._InstrumentID: str = instrument_id
        self._ExchangeID: str = exchange_id
        self._TradingDay: str = trading_day
        self._ActionDay: str = action_day
        self._TradingTime: str = trading_time
        self._LastPrice: float = last_price
        self._LastVolume: int = last_volume
        self._AskPrice: float = ask_price
        self._AskVolume: int = ask_volume
        self._BidPrice: float = bid_price
        self._BidVolume: int = bid_volume

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def ExchangeID(self):
        return self._ExchangeID

    @ExchangeID.setter
    def ExchangeID(self, value: str):
        self._ExchangeID = value

    @property
    def TradingDay(self):
        return self._TradingDay

    @TradingDay.setter
    def TradingDay(self, value: str):
        self._TradingDay = value

    @property
    def ActionDay(self):
        return self._ActionDay

    @ActionDay.setter
    def ActionDay(self, value: str):
        self._ActionDay = value

    @property
    def TradingTime(self):
        return self._TradingTime

    @TradingTime.setter
    def TradingTime(self, value: str):
        self._TradingTime = value

    @property
    def LastPrice(self):
        return self._LastPrice

    @LastPrice.setter
    def LastPrice(self, value: float):
        self._LastPrice = value

    @property
    def LastVolume(self):
        return self._LastVolume

    @LastVolume.setter
    def LastVolume(self, value: int):
        self._LastVolume = value

    @property
    def AskPrice(self):
        return self._AskPrice

    @AskPrice.setter
    def AskPrice(self, value: float):
        self._AskPrice = value

    @property
    def AskVolume(self):
        return self._AskVolume

    @AskVolume.setter
    def AskVolume(self, value: int):
        self._AskVolume = value

    @property
    def BidPrice(self):
        return self._BidPrice

    @BidPrice.setter
    def BidPrice(self, value: float):
        self._BidPrice = value

    @property
    def BidVolume(self):
        return self._BidVolume

    @BidVolume.setter
    def BidVolume(self, value: int):
        self._BidVolume = value
