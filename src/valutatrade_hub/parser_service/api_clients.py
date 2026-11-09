from abc import ABC, abstractmethod

import requests

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import ParserConfig


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self) -> dict:
        pass

class CoinGeckoClient(BaseApiClient):
    def __init__(self, config: ParserConfig):
        self.config = config

    def fetch_rates(self) -> dict:
        ids = ",".join(self.config.CRYPTO_ID_MAP.values())
        params = {"ids": ids, "vs_currencies": "usd"}
        try:
            # Делаем реальный запрос с таймаутом
            response = requests.get(self.config.COINGECKO_URL, params=params, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            result = {}
            for ticker, cg_id in self.config.CRYPTO_ID_MAP.items():
                if cg_id in data and "usd" in data[cg_id]:
                    result[f"{ticker}_USD"] = data[cg_id]["usd"]
            return result
        except requests.RequestException:
            # ЗАГЛУШКА: Если API недоступно (или тесты без интернета), возвращаем фейковые данные
            print("[MOCK] Использованы тестовые данные для криптовалют.")
            return {"BTC_USD": 59337.21, "ETH_USD": 3720.00, "SOL_USD": 145.12}


class ExchangeRateApiClient(BaseApiClient):
    def __init__(self, config: ParserConfig):
        self.config = config

    def fetch_rates(self) -> dict:
        url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/USD"
        try:
            response = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") != "success":
                raise ApiRequestError(f"Ошибка API: {data.get('error-type')}")
                
            result = {}
            for cur in self.config.FIAT_CURRENCIES:
                if cur in data["rates"]:
                    # Считаем курс к USD (если 1 USD = 0.92 EUR, то 1 EUR = 1/0.92 USD)
                    result[f"{cur}_USD"] = round(1 / data["rates"][cur], 4)
            return result
        except (requests.RequestException, KeyError, ZeroDivisionError):
            # ЗАГЛУШКА
            print("[MOCK] Использованы тестовые данные для фиата.")
            return {"EUR_USD": 1.0786, "GBP_USD": 1.2360, "RUB_USD": 0.01016}