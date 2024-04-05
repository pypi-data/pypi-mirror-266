import logging
import os

def configure_logging():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-5.5s [%(name)s][pid:%(process)s tid:%(thread)s] %(message)s'
    )
    handler.setFormatter(formatter)

    log_level = (os.getenv('DISCOVERY_LOG_LEVEL') or 'INFO').upper()
    log_level = getattr(logging, log_level, logging.INFO)

    logger = logging.getLogger('atlasai.discovery')
    logger.setLevel(log_level)
    logger.addHandler(handler)
