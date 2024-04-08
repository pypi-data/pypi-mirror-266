# coding=utf-8
from .client import FaxDataClient
from .utils import *


@assert_auth
def get_factor(sec_code: str = None,
               sec_code_list: list = None,
               factor_list=None,
               factor_group_list: list = None,
               trade_date: str = None,
               start_date: str = None,
               end_date: str = None,
               start_datetime: str = None,
               end_datetime: str = None,
               stock_pool: list = None,
               dividend_type='front',
               unit: str = '1d',
               expect_df: bool = True,
               count: int = None):
    """
    查询因子库数据.

    :param sec_code: 股票代码
    :param sec_code_list: 股票代码列表
    :param factor_list: 因子列表，因子可能来源于不同的因子分组
    :param factor_group_list: 限定因子分组
    :param trade_date: 限定交易日
    :param start_date: 开始交易日
    :param end_date: 结束交易日
    :param start_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param end_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param stock_pool: 指数列表，仅加载指数成分股
    :param dividend_type: 复权选项
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param unit: 单位时间长度，支持1d、1m，默认为1d
    :param expect_df: 是否以DataFrame返回
    :param count: 数量, 返回的结果集的行数
    :return:
    """
    if factor_list is None:
        factor_list = ['close']
    return FaxDataClient.instance().get_factor(**locals())


@assert_auth
def get_transform_factor(sec_code: str = None,
                         sec_code_list: list = None,
                         factor_list=None,
                         factor_group_list: list = None,
                         trade_date: str = None,
                         start_date: str = None,
                         end_date: str = None,
                         stock_pool: list = None,
                         dividend_type='back',
                         unit: str = '1d',
                         expect_df: bool = True,
                         count: int = None):
    """
    查询因子数据的空值处理、去极值、标准化、市值中性化、行业中性化后的结果

    :param sec_code: 股票代码
    :param sec_code_list: 股票代码列表
    :param factor_list: 因子列表，因子可能来源于不同的因子分组
    :param factor_group_list: 限定因子分组
    :param trade_date: 限定交易日
    :param start_date: 开始交易日
    :param end_date: 结束交易日
    :param stock_pool: 指数列表，仅加载指数成分股。
                       选出了历史中出现在指数中所有成分，此时有未来函数，等于把低价股票提前选入了沪深300的股票池中。
                       数据分析中需要结合crud.get_index_members_lst()一起使用，过滤掉未来函数的股票。
    :param dividend_type: 复权选项
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param unit: 单位时间长度，支持1d、1m，默认为1d
    :param expect_df: 是否以DataFrame返回
    :param count: 数量, 返回的结果集的行数
    :return:
    """
    if factor_list is None:
        factor_list = ['close']
    return FaxDataClient.instance().get_transform_factor(**locals())


@assert_auth
def get_history(count: int = None,
                unit: str = '1d',
                start_date: str = None,
                end_date: str = None,
                start_datetime: str = None,
                end_datetime: str = None,
                field: str = 'close',
                security_list=None,
                stock_pool: list = None,
                expect_df=True,
                skip_paused=False,
                dividend_type='front'):
    """
    获取历史数据，可查询多个标的单个数据字段，返回数据格式为 DataFrame 或 Dict(字典)

    :param stock_pool: 股票池
    :param start_date: 开始日期
    :param end_date: 结束日期
    :param count: 数量, 返回的结果集的行数
    :param unit: 单位时间长度, 几天或者几分钟, 现在支持'1d','1m'
    :param start_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param end_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param field: 要获取的数据字段
    :param security_list: 要获取数据的股票列表
    :param expect_df: df=True: [pandas.DataFrame]对象, 行索引是[datetime.datetime]对象, 列索引是股票代号
               df=False: dict, key是股票代码, value是一个numpy数组[numpy.ndarray]
    :param skip_paused: 是否跳过不交易日期(包括停牌, 未上市或者退市后的日期)
    :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :return:
    """
    return FaxDataClient.instance().get_history(**locals())


@assert_auth
def get_attribute_history(security: str,
                          count: int = None,
                          unit: str = '1d',
                          start_date: str = None,
                          end_date: str = None,
                          start_datetime: str = None,
                          end_datetime: str = None,
                          fields: list = None,
                          skip_paused: bool = True,
                          expect_df: bool = True,
                          dividend_type: str = 'front'):
    """
    获取历史数据，可查询单个标的多个数据字段，返回数据格式为 DataFrame 或 Dict(字典)

    :param start_date:
    :param end_date:
    :param start_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param end_datetime: 当unit='1m'时有效，格式：2023-03-29 14:57:00
    :param security: 股票代码
    :param count: 数量, 返回的结果集的行数
    :param unit: 单位时间长度, 1d, 1m
    :param fields: 股票属性的list, 支持：['open', ' high', 'low', 'close', 'volume', 'amount']
    :param skip_paused: 是否跳过不交易日期(包括停牌, 未上市或者退市后的日期).
    :param expect_df: 若是True, 返回[pandas.DataFrame], 否则返回一个dict, 具体请看下面的返回值介绍. 默认是True.
    :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :return:
    """
    return FaxDataClient.instance().get_attribute_history(**locals())


@assert_auth
def get_synthesize_factor(stock_pool: list,
                          start_date: str,
                          end_date: str,
                          freq: int = 5,
                          trade_date: str = None,
                          sec_code: str = None,
                          sec_code_list: list = None,
                          factor_list=None,
                          expect_df: bool = True,
                          exact_match: bool = False):
    """
    获取参数组合（stock_pool, start_date, end_date, freq）最优的合成因子数据

    :param stock_pool: 股票池
    :param start_date: 因子取数的开始日期，也是合成因子回测的开始日期
    :param end_date: 因子取数的结束日期，也是合成因子回测的结束日期
    :param freq: 调仓周期，单位为天，默认值为5
    :param trade_date: 限定交易日
    :param sec_code: 股票
    :param sec_code_list: 股票代码列表
    :param factor_list: 合成因子列表，默认返回完整的合成因子列表
    :param expect_df: 若是True, 返回[pandas.DataFrame], 否则返回一个dict, 具体请看下面的返回值介绍. 默认是True.
    :param exact_match: 是否精确匹配（stock_pool, start_date, end_date, freq），或者近似匹配
    :return:
    """
    return FaxDataClient.instance().get_synthesize_factor(**locals())


@assert_auth
def get_synthesize_portfolio(count: int = None,
                             stock_pool: list = None,
                             start_date: str = None,
                             end_date: str = None,
                             freq: int = 5,
                             trade_date_lst: list = None,
                             sec_code: str = None,
                             sec_code_list: list = None,
                             factor_list=None,
                             expect_df: bool = False,
                             exact_match: bool = False,
                             stock_size: int = 10):
    """
    获取参数组合（stock_pool, start_date, end_date, freq）最优的合成因子数据所产生的股票组合。

    :param count: 获取最新的n期调仓日数据
    :param stock_pool: 股票池
    :param start_date: 因子取数的开始日期，也是合成因子回测的开始日期
    :param end_date: 因子取数的结束日期，也是合成因子回测的结束日期
    :param freq: 调仓周期，单位为天，默认值为5
    :param trade_date_lst: 限定调仓日列表
    :param sec_code: 股票
    :param sec_code_list: 股票代码列表
    :param factor_list: 合成因子列表，默认返回完整的合成因子列表
    :param expect_df: 若是True, 返回[pandas.DataFrame], 否则返回一个dict, 具体请看下面的返回值介绍. 默认是True.
    :param exact_match: 是否精确匹配（stock_pool, start_date, end_date, freq），或者近似匹配
    :param stock_size: 股票组合的股票个数
    :return:
    """
    return FaxDataClient.instance().get_synthesize_portfolio(**locals())


__all__ = []
__all__.extend([name for name in globals().keys() if name.startswith("get")])
