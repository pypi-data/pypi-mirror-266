import logging


class CustomStreamHandler(logging.StreamHandler):
    def __init__(self, custom_logger, *args, **kwargs):
        self.logger = custom_logger
        super().__init__(*args, **kwargs)

    def emit(self, record):
        if record.levelno == logging.ERROR:
            custom_message = "%(module)s:%(lineno)d in %(funcName)s: %(message)s" % {
                'module': record.module,
                'lineno': record.lineno,
                'funcName': record.funcName,
                'message': record.msg
            }
            record.msg = custom_message
        super().emit(record)


class Logger(object):
    def __init__(self, name=None):
        scan_logger = logging.getLogger(name)
        scan_logger.setLevel(logging.DEBUG)

        ch = CustomStreamHandler(custom_logger=scan_logger)
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        ch.setFormatter(formatter)
        scan_logger.addHandler(ch)

        self.logger = scan_logger


def logger(name):
    return Logger(name).logger
