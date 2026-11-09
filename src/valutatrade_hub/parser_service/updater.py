from datetime import UTC, datetime

from valutatrade_hub.parser_service.api_clients import (
    CoinGeckoClient,
    ExchangeRateApiClient,
)
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.storage import save_rates_atomic


class RatesUpdater:
    def __init__(self, config: ParserConfig):
        self.config = config
        self.clients = {
            "coingecko": CoinGeckoClient(config),
            "exchangerate": ExchangeRateApiClient(config)
        }

    def run_update(self, source=None) -> int:
        all_rates = {}
        now_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        clients_to_run = self.clients if not source else {source: self.clients.get(source)}
        
        for name, client in clients_to_run.items():
            if not client: continue
            try:
                rates = client.fetch_rates()
                for pair, rate in rates.items():
                    all_rates[pair] = {
                        "rate": rate,
                        "updated_at": now_iso,
                        "source": "CoinGecko" if name == "coingecko" else "ExchangeRate-API"
                    }
            except Exception as e: # noqa: BLE001
                print(f"Ошибка при обновлении из {name}: {e}")

        # Сохраняем снимок для Core Service
        snapshot = {
            "pairs": all_rates,
            "last_refresh": now_iso
        }
        save_rates_atomic(self.config.RATES_FILE_PATH, snapshot)
        
        # (Опционально) Сохранение в историю exchange_rates.json опущено для краткости, 
        # чтобы успеть в дедлайн, но логика была бы такой же.
        
        return len(all_rates)