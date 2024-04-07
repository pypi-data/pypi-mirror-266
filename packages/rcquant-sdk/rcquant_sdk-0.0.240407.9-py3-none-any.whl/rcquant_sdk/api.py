from typing import List, Dict, Tuple, Union
from .client import FinClient
from .data.login_data import LoginData
from .data.market.ohlc_data import OHLCData
from .data.chart.chart_init_param_data import ChartInitParamData
from .data.chart.marker_graph_param_data import MarkerGraphParamData
from .data.chart.text_graph_param_data import TextGraphParamData
from .data.chart.financial_graph_param_data import FinancialGraphParamData
from .data.chart.line_graph_param_data import LineGraphParamData
from .data.chart.ohlc_value_data import OHLCValueData
from .data.chart.graph_value_data import GraphValueData
from .data.trade.order_data import OrderData
from .data.market.market_param_data import MarketParamData
from .data.market.query_param_data import QueryParamData
from .data.market.sub_ohlc_param_data import SubOHLCParamData
from .data.market.history_ohlc_param_data import HistoryOHLCParamData
from .data.market.fin_persist_read_param_data import FinPersistReadParamData
from .data.market.history_tick_param_data import HistoryTickParamData
from .data.market.basetick_data import BaseTickData
from .data.trade.trade_param_data import TradeParamData
from .data.trade.read_history_order_param_data import ReadHistoryOrderParamData
from .data.trade.read_history_tradeorder_param_data import ReadHistoryTradeOrderParamData
from .data.trade.get_account_param_data import GetAccountParamData
from .data.trade.get_orders_param_data import GetOrdersParamData
from .data.trade.get_tradeorders_param_data import GetTradeOrdersParamData
from .data.trade.get_positions_param_data import GetPositionsParamData
from .data.chart.bar_graph_param_data import BarGraphParamData


def conncet(host: str = None, port: int = None, ):
    return FinClient.instance().connect(host, port)


def is_connected():
    return FinClient.instance().is_connected()


def login(user_id: str = '', password: str = ''):
    return FinClient.instance().base_handle().login(LoginData(user_id, password))


def close():
    FinClient.instance().close()


def set_callback(**kwargs):
    '''
    设置行情回调
    :param kwargs OnTick=None,
    '''
    FinClient.instance().set_callback(**kwargs)


def set_auth_params(userid, password, host: str = None, port: int = None):
    '''
    设置登录信息
    :param userid:用户名
    :param password:密码
    :param host:网络地址默认为None
    :param port:端口号默认为None
    :return:result msg
    '''
    ret = conncet(host, port)
    if ret is None or ret[0] is False:
        return ret
    return login(userid, password)


def set_chart_init_params(params: ChartInitParamData):
    return FinClient.instance().chart_handle().set_chart_init_params(params)


def add_line_graph(id: str, plot_index=0, value_axis_id=-1, color: str = '#FFF', style=0, price_tick=0.01, tick_valid_mul=-1.0, bind_ins_id='', bind_range=''):
    '''
    添加线图
    :param id:图形ID
    :param plot_index:所在图层索引
    :param value_axis_id:所属Y轴
    :param color:颜色
    :param style:样式
    :param price_tick:最小变动刻度
    :param tick_valid_mul:显示有效的倍数 -1.0不做限制
    :param bind_ins_id:绑定合约
    :param bind_range:绑定合约周期
    :return:result msg
    '''
    return FinClient.instance().chart_handle().add_line_graph(
        LineGraphParamData(
            name=id,
            id=id,
            plot_index=plot_index,
            value_axis_id=value_axis_id,
            style=style,
            color=color,
            price_tick=price_tick,
            tick_valid_mul=tick_valid_mul,
            bind_ins_id=bind_ins_id,
            bind_range=bind_range)
    )


def add_bar_graph(id: str, plot_index=0, value_axis_id=-1, color: str = '#FFF', style=0, frame_style=2):
    """添加柱状图

    Args:
        id (str): 图形id
        plot_index (int, optional): 所在图层索引. Defaults to 0.
        value_axis_id (int, optional): 所属Y轴. Defaults to -1左边第一个Y轴.
        color (str, optional): 颜色. Defaults to '#FFF'.
        style (int, optional): 样式. Defaults to 0 box.
        frame_style (int, optional): 边框样式. Defaults to 2 线型.

    Returns:
        _type_: [bool,str]
    """

    return FinClient.instance().chart_handle().add_bar_graph(
        BarGraphParamData(
            name=id,
            id=id,
            plot_index=plot_index,
            valueaxis_id=value_axis_id,
            style=style,
            frame_style=frame_style,
            color=color,
        )
    )


def add_financial_graph(id: str, plot_index=0, value_axis_id=-1, style=0, price_tick=0.01, tick_valid_mul=-1.0, bind_ins_id='', bind_range=''):
    '''
    添加线图
    :param id:图形编号
    :param name:图形名称
    :param style:样式
    :param plot_index:所在图层索引
    :param value_axis_id:所属Y轴
    :param price_tick:最小变动刻度
    :param tick_valid_mul:显示有效的倍数 -1.0不做限制
    :param bind_ins_id:绑定合约
    :param bind_range:绑定合约周期
    :return: [result,msg] True 添加成功, False 添加失败
    '''
    return FinClient.instance().chart_handle().add_financial_graph(
        FinancialGraphParamData(
            id=id,
            name=id,
            style=style,
            plot_index=plot_index,
            value_axis_id=value_axis_id,
            price_tick=price_tick,
            tick_valid_mul=tick_valid_mul,
            bind_ins_id=bind_ins_id,
            bind_range=bind_range)
    )


def chart_init_show():
    return FinClient.instance().chart_handle().chart_init_show()


def add_line_value(graphid: str, key: float = 0.0, value: float = 0.0, mill_ts: int = -1):
    return FinClient.instance().chart_handle().add_graph_value(GraphValueData(
        graph_id=graphid,
        key=key,
        mill_ts=mill_ts,
        value=value)
    )


def add_marker_graph(param: MarkerGraphParamData):
    return FinClient.instance().chart_handle().add_marker_graph(param)


def add_graph_value(gv: GraphValueData):
    return FinClient.instance().chart_handle().add_graph_value(gv)


def add_graph_value_list(gvl):
    gvdl = []
    for gv in gvl:
        gvdl.append(GraphValueData(graph_id=gv[0], mill_ts=gv[1], value=gv[2]))
    return FinClient.instance().chart_handle().add_graph_value_list(gvdl)


def add_timespan_graphvalue_list(timespans: List[int], graph_values: Dict[str, List[float]] = {}, ohlc_values: Dict[str, Tuple[List[float], List[float], List[float], List[float]]] = {}):
    return FinClient.instance().chart_handle().add_timespan_graphvalue_list(timespans, graph_values, ohlc_values)


def add_ohlc_value(ov: OHLCValueData):
    return FinClient.instance().chart_handle().add_ohlc_value(ov)


def add_ohlc_value_list(ovl: List[OHLCValueData]):
    return FinClient.instance().chart_handle().add_ohlc_value_list(ovl)


def add_ohlc(graph_id: str, o: OHLCData):
    '''
    添加OHLC值
    :param graph_id:图形名称
    :param o:ohlc
    :return:result,msg
    '''
    return FinClient.instance().chart_handle().add_ohlc_value(
        OHLCValueData(
            graph_id=graph_id,
            ohlc_data=o)
    )


def draw_text(plot_index: int, value_axis_id: int, key: float, value: float, text: str, color: str = '#FFF'):
    '''
    画文本
    :param plot_index:所在图层索引
    :param value_axis_id:所属Y轴
    :param key:x轴值
    :param value:y轴值
    :param text:文本
    :param color:颜色
    :return:[result,msg]
    '''
    return FinClient.instance().chart_handle().add_text_graph(
        TextGraphParamData(
            plot_index=plot_index,
            value_axis_id=value_axis_id,
            key=key,
            value=value,
            text=text,
            color=color)
    )


def add_text_graph(param: TextGraphParamData):
    return FinClient.instance().chart_handle().add_text_graph(param)


def draw_text_milltime(plot_index, value_axis_id, mill_ts, value, text, color='#FFF'):
    '''
    画文本
    :param plot_index:所在图层索引
    :param value_axis_id:所属Y轴
    :param mill_ts:x时间戳
    :param value:y轴值
    :param text:文本
    :param color:颜色
    :return:result,msg
    '''
    return FinClient.instance().chart_handle().add_text_graph(
        TextGraphParamData(
            plot_index=plot_index,
            value_axis_id=value_axis_id,
            mill_ts=mill_ts,
            value=value,
            text=text,
            color=color)
    )


def set_market_params(market_names):
    '''
    设置行情参数
    :param market_names:行情名称多个时候用逗号分隔
    :return:result,msg
    '''
    return FinClient.instance().market_handle().set_market_params(
        MarketParamData(market_names=market_names)
    )


def subscribe(market_name: str, exchang_id: str, instrument_id: str):
    '''
    订阅行情
    :param market_name:行情名称
    :param exchang_id:交易所编码
    :param instrument_id:合约编码
    :return:result,msg
    '''
    return FinClient.instance().market_handle().subscribe(
        QueryParamData(
            market_name=market_name,
            exchange_id=exchang_id,
            instrument_id=instrument_id)
    )


def subscribe_ohlc(market_name: str, exchang_id: str, instrument_id: str, range: str):
    '''
    订阅行情
    :param market_name:行情名称
    :param exchang_id:交易所编码
    :param instrument_id:合约编码
    :param range:周期
    :return:result,msg
    '''
    return FinClient.instance().market_handle().subscribe_ohlc(
        SubOHLCParamData(
            market_name=market_name,
            exchange_id=exchang_id,
            instrument_id=instrument_id,
            range=range)
    )


def get_history_ohlc(market_name: str, exchang_id: str, instrument_id: str, range: str,
                     start_date: str, end_date: str, is_return_list: bool = False):
    '''
    获取历史ohlc数据
    :param market_name:行情名称
    :param exchang_id:交易所编码
    :param instrument_id:合约编码
    :param range:周期
    :param start_date 开始日期
    :param end_date 结束日期
    :param is_return_list 是否返回list格式
    :return:result,msg
    '''
    return FinClient.instance().market_handle().get_history_ohlc(
        HistoryOHLCParamData(
            market_name=market_name,
            exchange_id=exchang_id,
            instrument_id=instrument_id,
            range=range,
            start_date=start_date,
            end_date=end_date,
            is_return_list=is_return_list)
    )


def fin_save_ohlc_list(instrument_id: str, range: str, df, compress: str = 'zip', level: int = -1, pack: str = 'msgpack'):
    """批量按天保存OHLC数据

    Args:
        instrument_id (str, optional) 合约编码 Defaults  to ''.
        range (str, optional) 周期 Defaults  to ''
        df (DataFrame, optional): 数据集 Defaults to
        列及类型
        ['ExchangeID':str, 'InstrumentID':str, 'TradingDay':str, 'TradingTime':str, 'StartTime':str,
        'EndTime':str, 'ActionDay':str, 'ActionTimeSpan':int, 'Range':int, 'Index':int,
        'OpenPrice':float, 'HighestPrice':float, 'LowestPrice':float, 'ClosePrice':float,
        'TotalTurnover':float, 'TotalVolume':int, 'OpenInterest':float, 'PreSettlementPrice':float,
        'OpenBidPrice':float, 'OpenAskPrice':float, 'OpenBidVolume':int, 'OpenAskVolume':int,
        'HighestBidPrice':float, 'HighestAskPrice':float, 'HighestBidVolume':int, 'HighestAskVolume':int,
        'LowestBidPrice':float, 'LowestAskPrice':float, 'LowestBidVolume':int, 'LowestAskVolume':int,
        'CloseBidPrice':float, 'CloseAskPrice':float, 'CloseBidVolume':int, 'CloseAskVolume':int].
        compress (str, optional): 压缩方式 Defaults to 'xz'.
        level 压缩等级
        pack 序列化方式 msgpack pickle Defaults to 'msgpack'.
    Returns:
        _type_: [bool,str]
    """

    return FinClient.instance().market_handle().fin_save_ohlc_list(instrument_id, range, df, compress, level, pack)


def fin_read_ohlc_list(instrument_id: str, range: str, start_date: int, end_date: int, base_path: str = '', is_return_list: bool = False):
    '''
    获取ohlc数据
    :param instrument_id:合约编码
    :param range:周期
    :param start_date 开始日期
    :param end_date 结束日期
    :param base_path 存储路径,为空使用系统默认
    :param is_return_list 是否返回list格式
    :return:result,msg
    '''
    return FinClient.instance().market_handle().fin_read_ohlc_list(FinPersistReadParamData(instrument_id=instrument_id, range=range, start_date=start_date, end_date=end_date, base_path=base_path), is_return_list=is_return_list)


def fin_save_basetick_list(instrument_id, df, compress: str = 'zip', level: int = -1, pack: str = 'msgpack'):
    """批量按天保存行情数据

    Args:
        instrument_id (str, optional) 合约编码 Defaults  to ''.
        df (DataFrame, optional): 数据集
        包含列
        ['ExchangeID':str, 'InstrumentID':str, 'ActionDay':str, 'ActionTime':str, 'UpdateMillisec':int,
        'LastPrice':float, 'LastVolume':int, 'BidPrice':float, 'BidVolume':int, 'AskPrice':float, 'AskVolume':int,
        'TotalTurnover':float, 'TotalVolume':int, 'OpenInterest':float, 'PreClosePrice':float,
        'PreSettlementPrice':float, 'PreOpenInterest':float]
        compress (str, optional):zip xz 压缩方式 Defaults to 'zip'.
        level 压缩等级
        pack 序列化方式 msgpack pickle Defaults to 'msgpack'.

    Returns:
        _type_: [bool,str]
    """
    return FinClient.instance().market_handle().fin_save_basetick_list(instrument_id, df, compress, level, pack)


def fin_read_basetick_list(instrument_id: str, start_date: int = 0, end_date: int = 99999999, base_path: str = '', is_return_list: bool = False):
    '''
    获取basetick数据
    :param instrument_id:合约编码
    :param start_date 起始日期
    :param end_date 结束日期
    :param base_path 路径
    :param is_return_list 是否返回list格式
    :return: result,msg
    '''
    return FinClient.instance().market_handle().fin_read_basetick_list(
        FinPersistReadParamData(table_name=instrument_id, range='BTick', start_date=start_date,
                                end_date=end_date, base_path=base_path), is_return_list=is_return_list)


def set_trade_params(tradenames: str):
    return FinClient.instance().trade_handle().set_trade_params(TradeParamData(trade_names=tradenames))


def insert_order(trade_name, exchange_id: str, instrument_id: str, direc: int, price: float, vol: int, open_close_type: int):
    return FinClient.instance().trade_handle().insert_order(
        OrderData(
            exchange_id=exchange_id,
            instrument_id=instrument_id,
            price=price,
            direction=direc,
            volume=vol,
            investor_id=trade_name,
            open_close_type=open_close_type
        )
    )


def cancel_order_by_data(order: OrderData):
    return FinClient.instance().trade_handle().cancel_order(order)


def cancel_order(trade_name: str, order_id: str, instrument_id: str, order_ref: str, price: float):
    return FinClient.instance().trade_handle().cancel_order(
        OrderData(
            investor_id=trade_name,
            order_id=order_id,
            instrument_id=instrument_id,
            order_ref=order_ref,
            price=price
        )
    )


def read_history_orders(start_date: str, end_date: str):
    return FinClient.instance().trade_handle().read_history_orders(
        ReadHistoryOrderParamData(
            start_date=start_date,
            end_date=end_date
        )
    )


def read_history_tradeorders(start_date: str, end_date: str):
    return FinClient.instance().trade_handle().read_history_tradeorders(
        ReadHistoryTradeOrderParamData(
            start_date=start_date,
            end_date=end_date
        )
    )


def get_orders(trade_name: str):
    return FinClient.instance().trade_handle().get_orders(
        GetOrdersParamData(
            trade_name=trade_name
        )
    )


def get_tradeorders(trade_name: str):
    return FinClient.instance().trade_handle().get_tradeorders(
        GetTradeOrdersParamData(
            trade_name=trade_name
        )
    )


def get_positions(trade_name: str):
    return FinClient.instance().trade_handle().get_positions(
        GetPositionsParamData(
            trade_name=trade_name
        )
    )


def get_account(trade_name: str):
    return FinClient.instance().trade_handle().get_account(
        GetAccountParamData(
            trade_name=trade_name
        )
    )


def save_chart_data(file_name: str):
    '''
    保存图数据
    :param file_name 文件名称
    :return [result,msg]
    '''
    return FinClient.instance().chart_handle().save_chart_data(file_name)


def load_chart_data(file_name: str):
    '''
    加载图数据
    :param file_name 文件名称
    :return [result,msg]
    '''
    return FinClient.instance().chart_handle().load_chart_data(file_name)
