import logging

from logging.handlers import TimedRotatingFileHandler

__all__ = ('create_logfile', 'init_logging_format', 'show_dynamic_ratio',
           'throw_moduleNotFoundError')


def init_logging_format(format=None):
    format = format or "[%(asctime)s] %(levelname)s %(module)s[lines-%(lineno)d]: %(message)s"
    logging.basicConfig(format=format)


def create_logfile(logger, filename, format=None, **kwargs):
    format = format or "[%(asctime)s] %(levelname)s %(module)s[lines-%(lineno)d]: %(message)s"
    trfh = TimedRotatingFileHandler(filename, **kwargs)
    formatter = logging.Formatter(format)
    trfh.setFormatter(formatter)
    logger.addHandler(trfh)


def show_dynamic_ratio(cur_count, all_count, text='rate'):
    ratio = cur_count / all_count
    dynamic_ratio = int(ratio * 50)
    dynamic = '#' * dynamic_ratio + ' ' * (50 - dynamic_ratio)
    percentage = int(ratio * 100)
    print("\r[{}] {}: {}/{} {}%".format(dynamic, text, cur_count, all_count, percentage),
          end='', flush=True)


def throw_moduleNotFoundError(text):
    raise RuntimeError("Please use `{}` to fetch this module!".format(text))
