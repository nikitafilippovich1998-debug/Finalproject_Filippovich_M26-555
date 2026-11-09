from abc import ABC, abstractmethod

from valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    def __init__(self, name: str, code: str):
        if not name: raise ValueError("Имя не может быть пустым")
        if not code or not (2 <= len(code) <= 5) or code != code.upper():
            raise ValueError("Код валюты должен быть 2-5 символов в верхнем регистре")
        self.name = name
        self.code = code

    @abstractmethod
    def get_display_info(self) -> str:
        pass

class FiatCurrency(Currency):
    def __init__(self, name: str, code: str, issuing_country: str):
        super().__init__(name, code)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"

class CryptoCurrency(Currency):
    def __init__(self, name: str, code: str, algorithm: str, market_cap: float):
        super().__init__(name, code)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"

# Реестр валют (Фабрика)
_CURRENCIES = {
    "USD": FiatCurrency("US Dollar", "USD", "United States"),
    "EUR": FiatCurrency("Euro", "EUR", "Eurozone"),
    "RUB": FiatCurrency("Russian Ruble", "RUB", "Russia"),
    "BTC": CryptoCurrency("Bitcoin", "BTC", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("Ethereum", "ETH", "Ethash", 3.5e11)
}

def get_currency(code: str) -> Currency:
    curr = _CURRENCIES.get(code.upper())
    if not curr:
        raise CurrencyNotFoundError(f"Неизвестная валюта '{code}'")
    return curr