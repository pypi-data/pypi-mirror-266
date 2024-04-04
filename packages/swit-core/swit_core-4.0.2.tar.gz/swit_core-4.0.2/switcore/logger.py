import logging


def get_logger() -> logging.Logger:
    logger = logging.getLogger('[swit-logger]')
    logger.setLevel(logging.INFO)

    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(name)s - (PID: %(process)d) - (File: %(filename)s -'
            ' Function: %(funcName)s - Line: %(lineno)d) - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger
