import logging

from core.proxy_helper import ProxyHelper


def get_proxy(user_name, password):
    proxy = ProxyHelper(user_name, password)
    try:
        return proxy.get_proxy()
    except Exception as e:
        logging.error(e)
    return None
