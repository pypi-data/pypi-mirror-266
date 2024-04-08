import logging
import colorlog


class Logger:
    # 日志级别：（critical > error > warning > info > debug）
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    def __init__(self, name=None, file_name=None, console_level=None, file_level=None):
        """
        自定义日志对象
        :param name: logger名称
        :param file_name: 输出文件路径
        :param console_level: 控制台日志级别
        :param file_level: 日志文件的日志级别
        """
        if name is None:
            name = 'faxdatasdk'

        if console_level is None:
            console_level = self.DEBUG

        if file_level is None:
            file_level = self.ERROR  # # 默认只有error和critical级别才会写入日志文件

        # 获取logger对象
        self.logger = logging.getLogger(name)
        # 阻止日志消息从当前Logger向父级Logger传递
        self.logger.propagate = False

        # 指定最低日志级别：（critical > error > warning > info > debug）
        self.logger.setLevel(level=self.DEBUG)

        # 控制台输出不同级别日志颜色设置
        color_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'purple',
        }

        # -------------------------
        # 输出到控制台
        # 日志格化字符串
        # -------------------------
        console_fmt = '%(log_color)s%(asctime)s: %(levelname)s %(message)s'
        console_formatter = colorlog.ColoredFormatter(fmt=console_fmt, log_colors=color_config)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(console_level)
        self.logger.addHandler(console_handler)

        # -------------------------
        # 输出到文件
        # -------------------------
        if file_name:
            self.add_file_handler(name=name, file_name=file_name, level=file_level)

    def add_file_handler(self,
                         name: str = 'faxdatasdk',
                         file_name: str = None,
                         level=logging.ERROR,
                         file_fmt: str = None):
        if file_fmt is None:
            file_fmt = '%(asctime)s: %(levelname)s %(message)s'
        file_formatter = logging.Formatter(fmt=file_fmt)
        file_handler = logging.FileHandler(filename=file_name, mode='a', encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        logging.getLogger(name).addHandler(file_handler)

    def set_level(self, name: str = 'faxdatasdk', level=logging.INFO):
        logging.getLogger(name).setLevel(level)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


# 创建全局logger
log = Logger(name='faxdatasdk')
