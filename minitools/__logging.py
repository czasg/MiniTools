import logging

from logging.handlers import TimedRotatingFileHandler

from .__path import current_file_path

__all__ = 'create_logfile',

FORMAT = "[%(asctime)s] %(levelname)s %(module)s[lines-%(lineno)d]: %(message)s"
logging.basicConfig(format=FORMAT)


def create_logfile(logger, filename, pathname, **kwargs):
    trfh = TimedRotatingFileHandler(current_file_path(filename, pathname), **kwargs)
    formatter = logging.Formatter(FORMAT)
    trfh.setFormatter(formatter)
    logger.addHandler(trfh)
