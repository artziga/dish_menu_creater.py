import logging


def init_logger(name):
    logger = logging.getLogger(name)
    FORMAT = '%(message)s'
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(FORMAT))
    sh.setLevel(logging.INFO)
    fh = logging.FileHandler('log.txt', encoding='utf-8')
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(logging.INFO)
    logger.addHandler(sh)
    logger.addHandler(fh)


if __name__ == '__main__':
    init_logger('app')
