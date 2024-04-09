# add logging
import logging
from dataclasses import dataclass

# Set log level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class ParacordCLI:
    def __init__(self):
        pass

    def hello(self):
        logger.info("Hello, World!")
        return "Hello, World!"
