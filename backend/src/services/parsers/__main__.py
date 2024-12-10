from src.services.parsers.cbr_parser import CBRParser
from src.services.parsers.parser import Parser


if __name__ == "__main__":
    parser = Parser(cbr_parser=CBRParser())
    parser.load_tomorrow_currencies()