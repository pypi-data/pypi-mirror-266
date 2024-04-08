# fax-datasdk

#### 介绍
Fax-数据接口客户端，用于分布式数据访问和客户端访问


### 安装方法
```shell
# 首次安装, 在项目的根目录下添加requirements.txt文件，增加内容如下：
Cython==0.29.34
ply==3.11
msgpack>=0.4.7
pandas==1.4.4
setuptools==66.0.0
six==1.16.0
thriftpy2==0.4.16
wheel==0.38.4
faxdatasdk==0.0.2

# 在命令行执行：
pip install -r requirements.txt
# 如果安装失败，请指定官方镜像源
pip install -r requirements.txt -i https://pypi.org/simple

# 安装指定的版本： pip install ttdatasdk==<version>
pip install ttdatasdk==0.0.1

# 升级版本
pip install -U faxdatasdk
# 如果安装失败，请指定官方镜像源
pip install -U faxdatasdk -i https://pypi.org/simple
```


### 使用方法
```python
import faxdatasdk

"""账号认证"""
faxdatasdk.auth(username, password)

"""使用 token 认证账号"""
faxdatasdk.auth_by_token(token="")

# 获取因子数据
factor_list = ['float_share', 'pe', 'pe_ttm', 'ma_5', 'ema_5', 'dv_ratio']
df = faxdatasdk.get_factor(stock_pool=['000300.SH'], trade_date='2023-03-29', factor_list=factor_list)
print(df)
```

```shell
                            open        high  ...      volume       amount
sec_code  trade_date                          ...                         
000001.SZ 2023-03-29       12.73       12.74  ...   596064.33   750687.551
000002.SZ 2023-03-29       15.41       15.62  ...   654848.26  1012734.687
000063.SZ 2023-03-29   34.435106   34.553575  ...   782218.36  2685933.703
000069.SZ 2023-03-29         4.7        4.75  ...   324836.19   152639.669
000100.SZ 2023-03-29    3.989899    4.044431  ...  1604844.15   707678.236
...                          ...         ...  ...         ...          ...
688363.SH 2023-03-29  111.999999  113.159999  ...    30500.33   341085.693
688396.SH 2023-03-29   59.307833   61.559399  ...    75640.44   458018.471
688561.SH 2023-03-29   72.570005   72.570005  ...    87323.24   605371.703
688599.SH 2023-03-29   51.750011   52.490011  ...    149553.3   768914.461
688981.SH 2023-03-29   49.189988   50.319988  ...   708926.22  3496451.834

[300 rows x 6 columns]
                                    open   high  ...  volume      amount
sec_code  datetime                               ...                    
000001.SZ 2023-03-29 14:56:00  12.529999  12.54  ...  3274.0   4103280.0
          2023-03-29 14:57:00      12.54  12.54  ...  5943.0   7450969.0
          2023-03-29 14:58:00      12.54  12.54  ...   122.0    152976.0
          2023-03-29 14:59:00      12.54  12.54  ...     0.0         0.0
          2023-03-29 15:00:00      12.54  12.54  ...  9497.0  11900655.0

[5 rows x 6 columns]

```

