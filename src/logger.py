import logging
# import time

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    # datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)