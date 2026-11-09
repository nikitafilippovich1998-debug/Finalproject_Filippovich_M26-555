from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import (
    InsufficientFundsError,
)
from valutatrade_hub.core.models import User
from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra.database import DatabaseManager

# Имитация курсов
RATES = {"USD": 1.0, "EUR": 1.08, "BTC": 59000.0, "RUB": 0.011, "ETH": 3500.0}
db = DatabaseManager()

def register_user(username, password):
    users = db.load("users.json", [])
    if any(u["username"] == username for u in users):
        return "Имя пользователя уже занято"
    if len(password) < 4:
        return "Пароль должен быть не короче 4 символов"
    
    new_id = max([u["user_id"] for u in users], default=0) + 1
    user = User(new_id, username, password)
    users.append(user.to_dict())
    db.save("users.json", users)
    
    portfolios = db.load("portfolios.json", [])
    portfolios.append({"user_id": new_id, "wallets": {}})
    db.save("portfolios.json", portfolios)
    return f"Пользователь '{username}' зарегистрирован (id={new_id})"

def login_user(username, password):
    users = db.load("users.json", [])
    for u in users:
        if u["username"] == username:
            user = User(u["user_id"], u["username"], "", u["salt"])
            user._hashed_password = u["hashed_password"]
            if user.verify_password(password):
                return user
            return "Неверный пароль"
    return f"Пользователь '{username}' не найден"

def get_user_portfolio(user_id):
    portfolios = db.load("portfolios.json", [])
    for p in portfolios:
        if p["user_id"] == user_id:
            return p
    return None

def get_rate(from_cur, to_cur):
    get_currency(from_cur) # Валидация
    get_currency(to_cur)   # Валидация
    return RATES[from_cur.upper()] / RATES[to_cur.upper()]

@log_action("BUY")
def buy_currency(user_id, currency_code, amount):
    if amount <= 0: raise ValueError("Сумма должна быть > 0")
    get_currency(currency_code) # Валидация (выбросит CurrencyNotFoundError)
    
    curr = currency_code.upper()
    rate = get_rate(curr, "USD")
    cost_usd = amount * rate
    
    portfolios = db.load("portfolios.json", [])
    for p in portfolios:
        if p["user_id"] == user_id:
            wallets = p["wallets"]
            usd_balance = wallets.get("USD", {}).get("balance", 0.0)
            
            if usd_balance < cost_usd:
                raise InsufficientFundsError(f"Недостаточно средств: доступно {usd_balance:.2f} USD, требуется {cost_usd:.2f} USD")
            
            wallets["USD"] = {"balance": usd_balance - cost_usd}
            current_bal = wallets.get(curr, {}).get("balance", 0.0)
            wallets[curr] = {"balance": current_bal + amount}
            
            db.save("portfolios.json", portfolios)
            return f"Покупка выполнена: {amount:.4f} {curr} по курсу {rate}. Списано {cost_usd:.2f} USD"

@log_action("SELL")
def sell_currency(user_id, currency_code, amount):
    if amount <= 0: raise ValueError("Сумма должна быть > 0")
    get_currency(currency_code)
    
    curr = currency_code.upper()
    rate = get_rate(curr, "USD")
    revenue_usd = amount * rate
    
    portfolios = db.load("portfolios.json", [])
    for p in portfolios:
        if p["user_id"] == user_id:
            wallets = p["wallets"]
            curr_balance = wallets.get(curr, {}).get("balance", 0.0)
            
            if curr_balance < amount:
                raise InsufficientFundsError(f"Недостаточно средств: доступно {curr_balance:.4f} {curr}")
            
            wallets[curr] = {"balance": curr_balance - amount}
            usd_balance = wallets.get("USD", {}).get("balance", 0.0)
            wallets["USD"] = {"balance": usd_balance + revenue_usd}
            
            db.save("portfolios.json", portfolios)
            return f"Продажа выполнена: {amount:.4f} {curr}. Начислено {revenue_usd:.2f} USD"

# show_portfolio оставляем как было, но через db.load

def show_portfolio(user_id, base_currency="USD"):
    portfolio = get_user_portfolio(user_id)
    
    if not portfolio or not portfolio["wallets"]:
        return "У вас пока нет кошельков."

    base = base_currency.upper()
    if base not in RATES:
        return f"Неизвестная базовая валюта '{base}'"

    print(f"\nПортфель пользователя (база: {base})")
    total_value = 0.0
    
    for cur_code, wallet_data in portfolio["wallets"].items():
        balance = wallet_data["balance"]
        if balance == 0:
            continue
            
        if cur_code not in RATES:
            print(f"- {cur_code}: {balance:.4f} (курс неизвестен)")
            continue
            
        rate = get_rate(cur_code, base)
        value_in_base = balance * rate
        total_value += value_in_base
        print(f"- {cur_code}: {balance:.4f} -> {value_in_base:.2f} {base}")
        
    print("-" * 40)
    print(f"ИТОГО: {total_value:.2f} {base}\n")
    return ""
