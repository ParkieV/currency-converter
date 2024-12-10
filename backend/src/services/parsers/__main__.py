import asyncio

from src.logger import logger
from src.services.parsers.cbr_parser import CBRParser
from src.services.parsers.parser import Parser


if __name__ == "__main__":
    parser = Parser(cbr_parser=CBRParser())
    try:
        asyncio.run(parser.load_tomorrow_currencies())
    except Exception as e:
        logger.error('Failed to load currencies')
