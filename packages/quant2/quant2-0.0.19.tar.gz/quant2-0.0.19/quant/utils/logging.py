import logging


def setup_logging(filename="runs/log.txt", level=logging.INFO):
    logging.basicConfig(
        filename=filename,
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
        datefmt="%Y%m%d %H%M%S",
        level=level,
        encoding="utf8",
    )


def get_logger(name, propagate=True, filename="runs/log.txt", fmt=None, datefmt=None, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.propagate = propagate

    if logger.hasHandlers():
        return logger

    fmt = fmt or "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    datefmt = datefmt or "%Y%m%d %H%M%S"

    handler = logging.FileHandler(filename, encoding="utf8")
    formatter = logging.Formatter(fmt, datefmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def print_log(msg, verbose=True, logger=None, level=logging.INFO):
    if verbose:
        print(msg)
    if logger is not None:
        logger.log(level, msg)
