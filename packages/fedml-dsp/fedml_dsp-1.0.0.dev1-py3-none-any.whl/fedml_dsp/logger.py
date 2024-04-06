import sys
import logging

class Logger(object):
    logger = None
    
    def __init__(self):
        raise RuntimeError('Call get_instance() instead')
        

    @classmethod
    def get_instance(cls):
        if cls.logger is None:
            cls.logger = cls.get_logger()
        return cls.logger

    @classmethod
    def get_logger(cls):
        formatter= logging.Formatter('%(asctime)s: %(name)s %(levelname)s: %(message)s')
        h1 = logging.StreamHandler(sys.stdout)
        h1.setFormatter(formatter)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(h1)
        return logger