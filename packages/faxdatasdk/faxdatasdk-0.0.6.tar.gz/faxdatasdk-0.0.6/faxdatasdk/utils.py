# coding=utf-8
from functools import wraps


def get_mac_address():
    import uuid
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    return '%s:%s:%s:%s:%s:%s' % (mac[0:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:])


def assert_auth(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        from .client import FaxDataClient
        if not FaxDataClient.instance():
            raise Exception("请先执行faxdatasdk.auth(username, password)进行登录认证")
        else:
            return func(*args, **kwargs)

    return _wrapper
