import logging

import devtools
from loguru import logger

httpx_logger = logging.getLogger("httpx")
httpx_logger.disabled = True


__all__ = ["logger", "devtools"]
