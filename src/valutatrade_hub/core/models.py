import hashlib
import secrets
from datetime import datetime

class User:
    def __init__(self, user_id, username, password, salt=None):
        self._user_id = user_id
        self._username = username
        self._salt = salt if salt else secrets.token_hex(8)
        self._hashed_password = self._hash_password(password)
        self._registration_date = datetime.now().isoformat()

    def _hash_password(self, password):
        return hashlib.sha256((password + self._salt).encode()).hexdigest()

    @property
    def user_id(self): return self._user_id
    @property
    def username(self): return self._username
    @property
    def hashed_password(self): return self._hashed_password
    @property
    def salt(self): return self._salt
    @property
    def registration_date(self): return self._registration_date

    def verify_password(self, password):
        return self._hashed_password == self._hash_password(password)

    def change_password(self, new_password):
        if len(new_password) < 4:
            raise ValueError("Пароль должен быть не короче 4 символов")
        self._hashed_password = self._hash_password(new_password)

    def to_dict(self):
        return {
            "user_id": self._user_id, "username": self._username,
            "hashed_password": self._hashed_password, "salt": self._salt,
            "registration_date": self._registration_date
        }

class Wallet:
    def __init__(self, currency_code, balance=0.0):
        self.currency_code = currency_code.upper()
        self._balance = balance

    @property
    def balance(self): return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0 or not isinstance(value, (int, float)):
            raise ValueError("Баланс не может быть отрицательным")
        self._balance = value

    def deposit(self, amount):
        if amount <= 0: raise ValueError("Сумма должна быть > 0")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0: raise ValueError("Сумма должна быть > 0")
        if amount > self._balance: raise ValueError("Недостаточно средств")
        self._balance -= amount

class Portfolio:
    def __init__(self, user_id):
        self._user_id = user_id
        self._wallets = {} # {'USD': Wallet('USD')}

    @property
    def user_id(self): return self._user_id
    @property
    def wallets(self): return self._wallets.copy()

    def add_currency(self, currency_code):
        code = currency_code.upper()
        if code not in self._wallets:
            self._wallets[code] = Wallet(code)

    def get_wallet(self, currency_code):
        return self._wallets.get(currency_code.upper())