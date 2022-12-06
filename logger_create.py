import logging


def init_logger(name):
    logger = logging.getLogger(name)
    FORMAT = '%(asctime)s :: %(name)s:%(lineno)s :: %(levelname)s :: %(message)s'
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(FORMAT))
    sh.setLevel(logging.DEBUG)
    fh = logging.FileHandler('log.txt', encoding='utf-8')
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(logging.INFO)
    logger.addHandler(sh)
    logger.addHandler(fh)


if __name__ == '__main__':
    init_logger('app')
