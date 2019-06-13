import asyncio
import liteconfig
import logging

import smtp_handler


class Singleton(type):
    """Singleton realization via metaclass https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


config = liteconfig.Config('afsmtpd-my.ini')
# TODO: check config sanity.

if __name__ == '__main__':
    # TODO: make it running as windows service

    # import os
    # os.remove('afsmtpd.log')

    logging.basicConfig(filename='afsmtpd.log',
                        format='%(asctime)s | %(funcName)s, %(lineno)d: %(message)s',
                        datefmt='%m/%b/%Y %H:%M:%S')
    logging.getLogger().setLevel(config.main.loglevel)
    loop = asyncio.get_event_loop()
    loop.create_task(smtp_handler.smtp_server(config.server.ip, config.server.port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
