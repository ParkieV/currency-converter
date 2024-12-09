from typing import Any

import pytest


class TestParser:

    @pytest.mark.parametrize("country,excepted", [
        ('Россия', [
                      {
                        "value": "Российский рубль",
                        "unrestricted_value": "Российский рубль",
                        "data": {
                          "code": "643",
                          "strcode": "RUB",
                          "name": "Российский рубль",
                          "country": "Россия",
                          "cdr_id": None
                        }
                      }
                ]
         ),
        ('неверное_значение', []),
        ('Бела', [
                      {
                        "value": "Белорусский рубль",
                        "unrestricted_value": "Белорусский рубль",
                        "data": {
                          "code": "933",
                          "strcode": "BYN",
                          "name": "Белорусский рубль",
                          "country": "Беларусь",
                          "cdr_id": "R01090B"
                        }
                      }
                ]
         ),
        ('Бел', [])
    ])
    @pytest.mark.asyncio
    async def test_get_gov_currency_data(self,
                                         country: str,
                                         excepted: list[dict[str, Any]],
                                         set_env_vars):
        from src.services.parsers import Parser


        parser = Parser()

        assert await parser.get_gov_currency_data(country) == excepted

