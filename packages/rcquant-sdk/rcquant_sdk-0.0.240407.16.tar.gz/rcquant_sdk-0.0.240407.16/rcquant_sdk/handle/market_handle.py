from typing import Tuple
import msgpack
import lzma
import zlib
import datetime
import pickle


from .req_rsp import ReqRspDict, ReqRsp
from ..listener import IListener
from ..interface import IData, MsgID
from ..tsocket import TSocket
from ..data.message_data import MessageData

from ..data.market.market_param_data import MarketParamData
from ..data.market.sub_ohlc_param_data import SubOHLCParamData
from ..data.market.query_param_data import QueryParamData

from ..data.market.tick_data import TickData
from ..data.market.basetick_data import BaseTickData
from ..data.market.ohlc_data import OHLCData
from ..data.market.history_ohlc_param_data import HistoryOHLCParamData
from ..data.market.history_tick_param_data import HistoryTickParamData
from ..data.market.fin_persist_filed_data import FinPersistFiledData
from ..data.market.fin_persist_save_param_data import FinPersistSaveParamData
from ..data.market.fin_persist_read_param_data import FinPersistReadParamData
import pandas as pd


class MarketHandle():
    __ReqID: int = 0
    __Listener: IListener = None
    __ReqRspDict: ReqRspDict = ReqRspDict()
    __BaseTick_Columns = ['ExchangeID', 'InstrumentID', 'ActionDay', 'ActionTime', 'UpdateMillisec',
                          'LastPrice', 'LastVolume', 'BidPrice', 'BidVolume', 'AskPrice', 'AskVolume',
                          'TotalTurnover', 'TotalVolume', 'OpenInterest', 'PreClosePrice',
                          'PreSettlementPrice', 'PreOpenInterest']
    __OHLC_Columns = ['ExchangeID', 'InstrumentID', 'TradingDay', 'TradingTime', 'StartTime', 'EndTime', 'ActionDay',
                      'ActionTimeSpan', 'Range', 'Index', 'OpenPrice', 'HighestPrice', 'LowestPrice', 'ClosePrice',
                      'TotalTurnover', 'TotalVolume', 'OpenInterest', 'PreSettlementPrice', 'OpenBidPrice', 'OpenAskPrice', 'OpenBidVolume', 'OpenAskVolume', 'HighestBidPrice', 'HighestAskPrice',
                      'HighestBidVolume', 'HighestAskVolume', 'LowestBidPrice', 'LowestAskPrice', 'LowestBidVolume', 'LowestAskVolume',
                      'CloseBidPrice', 'CloseAskPrice', 'CloseBidVolume', 'CloseAskVolume']

    def __init__(self, tsocket: TSocket):
        self.__TSocket = tsocket
        self.__TSocket.set_market_callback(self.__recv_msg)

    def set_callback(self, **kwargs):
        if kwargs is None:
            return
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_listener(self, listener: IListener):
        self.__Listener = listener

    def set_market_params(self, params: MarketParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.MSGID_Market_SetParams.value), params)

    def subscribe(self, params: QueryParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.MSGID_Market_Sub.value), params)

    def subscribe_ohlc(self, params: SubOHLCParamData) -> Tuple[bool, str]:
        return self.__wait_send_msg(int(MsgID.MSGID_Market_SubOHLC.value), params)

    def get_history_tick(self, params: HistoryTickParamData) -> Tuple[bool, str, pd.DataFrame]:
        self.__ReqID = self.__ReqID + 1
        mid = int(MsgID.MSGID_Market_GetHistoryTick.value)
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            msg.UData = params.pack()

        key = '%s_%s' % (mid, self.__ReqID)
        req_rsp = self.__ReqRspDict.new_reqrsp(key, msg)
        if self.__TSocket.send_message(msg) is False:
            self.__ReqRspDict.remove(key)
            return [False, '发送命令失败', None]

        rsp = req_rsp.wait_last_rsp(60)
        if rsp is None:
            self.__ReqRspDict.remove(key)
            return [False, '获取历史OHLC数据超时', None]

        ret = [True, "", None]
        if params.IsReturnList is True:
            ret = [rsp.RspSuccess, rsp.RspMsg, self.__unpack_tick_list(req_rsp)]
        else:
            ret = [rsp.RspSuccess, rsp.RspMsg, self.__unpack_tick_dataframe(req_rsp)]

        self.__ReqRspDict.remove(key)
        return ret

    def get_history_ohlc(self, params: HistoryOHLCParamData) -> Tuple[bool, str, pd.DataFrame]:
        self.__ReqID = self.__ReqID + 1
        mid = int(MsgID.MSGID_Market_GetHistoryOHLC.value)
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            msg.UData = params.pack()

        key = '%s_%s' % (mid, self.__ReqID)
        req_rsp = self.__ReqRspDict.new_reqrsp(key, msg)
        if self.__TSocket.send_message(msg) is False:
            self.__ReqRspDict.remove(key)
            return [False, '发送命令失败', None]

        rsp = req_rsp.wait_last_rsp(60)
        if rsp is None:
            self.__ReqRspDict.remove(key)
            return [False, '获取历史OHLC数据超时', None]

        ret = [True, "", None]
        rspparams = HistoryOHLCParamData()
        if params.IsReturnList is True:
            ret = [rsp.RspSuccess, rsp.RspMsg, self.__unpack_ohlc_list(req_rsp, rspparams)]
        else:
            ret = [rsp.RspSuccess, rsp.RspMsg, self.__unpack_ohlc_dataframe(req_rsp, rspparams)]

        self.__ReqRspDict.remove(key)
        return ret

    def fin_save_ohlc_list(self, instrument_id: str, range: str, df, **kwargs) -> Tuple[bool, str]:
        if not isinstance(df, pd.DataFrame):
            return [False, "df 数据类型格式不是 DataFrame", {}]

        if df.columns.to_list() != self.__OHLC_Columns:
            return [False, "df 数据列名称不匹配,当前:%s 应为:%s" % (df.columns.to_list(), self.__OHLC_Columns)]

        b, m, params = self.__create_fin_persists_save_param_data(instrument_id, range, df, kwargs=kwargs)
        if b == False:
            return [b, m]

        return self.__wait_send_msg(int(MsgID.MSGID_Market_FinSaveOHLCList.value), params)

    def fin_read_ohlc_list(self, params: FinPersistReadParamData, is_return_list: bool = False) -> Tuple[bool, str, pd.DataFrame]:
        self.__ReqID = self.__ReqID + 1
        mid = int(MsgID.MSGID_Market_FinReadOHLCList.value)
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            msg.UData = params.pack()

        key = '%s_%s' % (mid, self.__ReqID)
        req_rsp = self.__ReqRspDict.new_reqrsp(key, msg)
        if self.__TSocket.send_message(msg) is False:
            self.__ReqRspDict.remove(key)
            return [False, '发送命令失败', None]

        rsp = req_rsp.wait_last_rsp(60)
        if rsp is None:
            self.__ReqRspDict.remove(key)
            return [False, '获取历史OHLC数据超时', None]

        ret = [True, "", None]
        if is_return_list is True:
            ret = [rsp.RspSuccess, rsp.RspMsg, self.__unpack_ohlc_list_v2(req_rsp)]
        else:
            ret = [rsp.RspSuccess, rsp.RspMsg, self.__unpack_fin_persist_read_param_data_to_df(req_rsp, self.__OHLC_Columns)]

        self.__ReqRspDict.remove(key)
        return ret

    def fin_save_basetick_list(self, instrument_id, df, **kwargs) -> Tuple[bool, str]:
        if not isinstance(df, pd.DataFrame):
            return [False, "df 数据类型格式不是 DataFrame", {}]

        if df.columns.to_list() != self.__BaseTick_Columns:
            return [False, "df 数据列名称不匹配,当前:%s 应为:%s" % (df.columns.to_list(), self.__BaseTick_Columns)]

        b, m, params = self.__create_fin_persists_save_param_data(instrument_id, "BTick", df, kwargs=kwargs)
        if b == False:
            return [b, m]

        return self.__wait_send_msg(int(MsgID.MSGID_Market_FinSaveBaseTickList.value), params)

    def fin_read_basetick_list(self, params: FinPersistReadParamData, is_return_list: bool = False) -> Tuple[bool, str, pd.DataFrame]:
        self.__ReqID = self.__ReqID + 1
        mid = int(MsgID.MSGID_Market_FinReadBaseTickList.value)
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            msg.UData = params.pack()

        key = '%s_%s' % (mid, self.__ReqID)
        req_rsp = self.__ReqRspDict.new_reqrsp(key, msg)
        if self.__TSocket.send_message(msg) is False:
            self.__ReqRspDict.remove(key)
            return [False, '发送命令失败', None]

        rsp = req_rsp.wait_last_rsp(60)
        if rsp is None:
            self.__ReqRspDict.remove(key)
            return [False, '获取历史basetick数据超时', None]

        ret = [True, "", None]
        if is_return_list is True:
            ret = [rsp.RspSuccess, rsp.RspMsg, self.__unpack_basetick_list(req_rsp)]
        else:
            ret = [rsp.RspSuccess, rsp.RspMsg, self.__unpack_fin_persist_read_param_data_to_df(req_rsp, self.__BaseTick_Columns)]

        self.__ReqRspDict.remove(key)
        return ret

    def __notify_on_tick(self, msg: MessageData):
        hasontick = hasattr(self, 'on_tick')
        if hasontick is False and self.__Listener is None:
            print('未定义任何on_tick回调方法')
            return
        t = TickData()
        if t.un_pack(msg.UData) is True:
            if hasontick is True:
                self.on_tick(t)
            if self.__Listener is not None:
                self.__Listener.on_tick(t)

    def __notify_on_ohlc(self, msg: MessageData):
        hasonohlc = hasattr(self, 'on_ohlc')
        if hasonohlc is False and self.__Listener is None:
            print('未定义任何on_ohlc回调方法')
            return
        o = OHLCData()
        if o.un_pack(msg.UData) is True:
            if hasonohlc is True:
                self.on_ohlc(o)
            if self.__Listener is not None:
                self.__Listener.on_ohlc(o)

    def __unpack_ohlc_list(self, reqrsp: ReqRsp, rspparams):
        ohlcs = list()
        rsp_list = reqrsp.get_rsp_list()
        for r in rsp_list:
            if len(r.UData) > 0:
                rspparams.un_pack(r.UData)
                for ot in rspparams.OHLCList:
                    o = OHLCData()
                    o.tuple_to_obj(ot)
                    ohlcs.append(o)
        return ohlcs

    def __unpack_ohlc_list_v2(self, reqrsp: ReqRsp):
        tempbytes = self.__unpack_decompress_buffers(reqrsp)
        ohlcs = list()
        for b in tempbytes:
            if len(b) <= 0:
                continue
            ticklist = msgpack.unpackb(b)
            for bt in ticklist:
                o = OHLCData()
                o.tuple_to_obj(bt)
                ohlcs.append(o)
        return ohlcs

    def __unpack_basetick_list(self, reqrsp: ReqRsp):
        tempbytes = self.__unpack_decompress_buffers(reqrsp)
        ticks = list()
        for b in tempbytes:
            if len(b) <= 0:
                continue
            ticklist = msgpack.unpackb(b)
            for bt in ticklist:
                o = BaseTickData()
                o.tuple_to_obj(bt)
                ticks.append(o)
        return ticks

    def __unpack_ohlc_dataframe(self, reqrsp: ReqRsp, rspparams):
        '''暂时保留，兼容旧接口'''
        dfrtn = pd.DataFrame()
        rsp_list = reqrsp.get_rsp_list()
        for r in rsp_list:
            if len(r.UData) > 0:
                rspparams.un_pack(r.UData)
                df = pd.DataFrame(rspparams.OHLCList, columns=['ExchangeID', 'InstrumentID', 'TradingDay', 'TradingTime', 'StartTime', 'EndTime', 'ActionDay',
                                                               'ActionTimeSpan', 'Range', 'Index', 'OpenPrice', 'HighestPrice', 'LowestPrice', 'ClosePrice',
                                                               'TotalTurnover', 'TotalVolume', 'OpenInterest', 'PreSettlementPrice', 'ChangeRate', 'ChangeValue',
                                                               'OpenBidPrice', 'OpenAskPrice', 'OpenBidVolume', 'OpenAskVolume', 'HighestBidPrice', 'HighestAskPrice',
                                                               'HighestBidVolume', 'HighestAskVolume', 'LowestBidPrice', 'LowestAskPrice', 'LowestBidVolume', 'LowestAskVolume',
                                                               'CloseBidPrice', 'CloseAskPrice', 'CloseBidVolume', 'CloseAskVolume'])
                dfrtn = pd.concat([dfrtn, df], ignore_index=True, copy=False)
        return dfrtn

    def __unpack_fin_persist_read_param_data_to_df(self, reqrsp: ReqRsp, columns):
        olist = self.__unpack_decompress_buffers(reqrsp, columns)
        return pd.concat(olist)

    def __unpack_stream_buffer(self, buffer, columns):
        o_list = []
        sz = int.from_bytes(buffer[:4], byteorder='little')
        while len(buffer) >= sz + 4 and sz > 0:
            o_list.extend(msgpack.unpackb(buffer[4:sz + 4], raw=False))
            buffer = buffer[sz + 4:]
            sz = int.from_bytes(buffer[:4], byteorder='little')
        return pd.DataFrame(o_list, columns=columns)

    def __unpack_decompress_buffers(self, req_rsp: ReqRsp, columns):
        rsp_list = req_rsp.get_rsp_list()
        dflist = []
        for r in rsp_list:
            if len(r.UData) <= 0:
                continue
            rspparams = FinPersistReadParamData()
            rspparams.un_pack(r.UData)
            for df in rspparams.DataFileds:
                marks = df.Mark.split(",")
                if len(marks) != 3:
                    continue

                decombytes = b''
                if marks[0] == 'zip':
                    decombytes = zlib.decompress(df.Buffer)
                elif marks[0] == 'xz':
                    decombytes = lzma.decompress(df.Buffer)
                elif marks[0] == 'qtzip':
                    decombytes = zlib.decompress(df.Buffer[4:])
                elif marks[0] == '0':
                    dflist.append(self.__unpack_stream_buffer(df.Buffer, columns))
                    continue

                if len(decombytes) == 0:
                    continue

                if marks[2] == 'pickle':
                    dflist.append(pickle.loads(decombytes))
                else:
                    dflist.append(pd.DataFrame(msgpack.unpackb(decombytes, raw=False), columns=columns))

        return dflist

    def __create_fin_persists_save_param_data(self, instrument_id: str, range: str, df, **kwargs):
        if not isinstance(df, pd.DataFrame):
            return [False, "df 数据类型格式不是 DataFrame", {}]

        compress = 'zip' if 'compress' not in kwargs.keys() else kwargs.get('compress')
        level = -1 if 'level' not in kwargs.keys() else kwargs.get('level')
        pack = 'msgpack' if 'pack' not in kwargs.keys() else kwargs.get('pack')
        vacuum = True if 'vacuum' not in kwargs.keys() else kwargs.get('vacuum')

        params: FinPersistSaveParamData = FinPersistSaveParamData()
        params.Append = False
        params.Range = range
        params.TableName = instrument_id
        params.Vacuum = bool(vacuum)
        groups = df.groupby('ActionDay')
        buffer_sz = 0
        for day, day_list in groups:
            filed = FinPersistFiledData()
            filed.Day = int(day)
            filed.Mark = '%s,%s,%s' % (compress, level, pack)
            pack_buffer = b''

            if pack == 'pickle':
                pack_buffer = pickle.dumps(day_list)
            else:
                pack_buffer = msgpack.packb(day_list.values.tolist(), use_bin_type=True)

            if compress == 'zip':
                filed.Buffer = zlib.compress(pack_buffer, level=level)
            else:
                filed.Buffer = lzma.compress(pack_buffer)

            buffer_sz = buffer_sz + len(filed.Buffer)
            params.Fileds.append(filed)
        return [True, "", params]

    def __recv_msg(self, msg: MessageData):
        if msg.MID == int(MsgID.MSGID_Market_Tick.value):
            self.__notify_on_tick(msg)
            return
        elif msg.MID == int(MsgID.MSGID_Market_OHLC.value):
            self.__notify_on_ohlc(msg)
            return

        key = '%s_%s' % (msg.MID, msg.RequestID)
        reqrsp: ReqRsp = self.__ReqRspDict.get_reqrsp(key)
        if reqrsp is not None:
            reqrsp.append_rsp(msg)

    def __wait_send_msg(self, mid, params: IData):
        self.__ReqID = self.__ReqID + 1
        msg = MessageData(mid=mid, request_id=self.__ReqID)
        if params is not None:
            msg.UData = params.pack()

        key = '%s_%s' % (mid, self.__ReqID)

        req_rsp = self.__ReqRspDict.new_reqrsp(key, msg)
        if self.__TSocket.send_message(msg) is False:
            self.__ReqRspDict.remove(key)
            return [False, '发送命令失败']

        rsp = req_rsp.wait_last_rsp(60)
        if rsp is None:
            self.__ReqRspDict.remove(key)
            return [False, '发送命令超时']

        ret = [rsp.RspSuccess, rsp.RspMsg]
        self.__ReqRspDict.remove(key)
        return ret
