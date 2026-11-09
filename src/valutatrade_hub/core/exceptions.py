class CurrencyNotFoundError(Exception):
    """Неизвестная валюта."""

class InsufficientFundsError(Exception):
    """Недостаточно средств."""

class ApiRequestError(Exception):
    """Сбой внешнего API."""
