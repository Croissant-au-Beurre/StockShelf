import logging
import logging.config


def get_logger(module_name):
    formatter = logging.Formatter(
        '%(levelname)s\tP:%(process)s\tT:%(thread)s\t%(filename)s:%(lineno)s\t%(asctime)s\t%(message)s')

    # シェルログ
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    # ファイルログ
    fh = logging.FileHandler('app.log')
    fh.setFormatter(formatter)

    # ログ
    logger = logging.getLogger(module_name)
    logger.addHandler(sh)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)

    return logger