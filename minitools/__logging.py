import logging

from logging.handlers import TimedRotatingFileHandler

from .__path import current_file_path

__all__ = ('create_logfile', 'init_logging_format')


def init_logging_format(format=None):
    format = format or "[%(asctime)s] %(levelname)s %(module)s[lines-%(lineno)d]: %(message)s"
    logging.basicConfig(format=format)


def create_logfile(logger, filename, pathname, format=None, **kwargs):
    format = format or "[%(asctime)s] %(levelname)s %(module)s[lines-%(lineno)d]: %(message)s"
    trfh = TimedRotatingFileHandler(current_file_path(filename, pathname), **kwargs)
    formatter = logging.Formatter(format)
    trfh.setFormatter(formatter)
    logger.addHandler(trfh)
