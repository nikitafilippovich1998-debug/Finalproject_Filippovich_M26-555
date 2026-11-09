from valutatrade_hub.core.models import User
from valutatrade_hub.storage import load_json, save_json

# Заглушка курсов (1 единица валюты = X USD)
RATES = {
    "USD": 1.0,
    "EUR": 1.08,
    "BTC": 59000.0,
    "RUB": 0.011
}

def register_user(username, password):
    users = load_json("users.json", [])
    if any(u["username"] == username for u in users):
        return "Имя пользователя уже занято"
    if len(password) < 4:
        return "Пароль должен быть не короче 4 символов"
    
    new_id = max([u["user_id"] for u in users], default=0) + 1
    user = User(new_id, username, password)
    users.append(user.to_dict())
    save_json("users.json", users)
    
    portfolios = load_json("portfolios.json", [])
    portfolios.append({"user_id": new_id, "wallets": {}})
    save_json("portfolios.json", portfolios)
    return f"Пользователь '{username}' зарегистрирован (id={new_id})"

def login_user(username, password):
    users = load_json("users.json", [])
    for u in users:
        if u["username"] == username:
            user = User(u["user_id"], u["username"], "", u["salt"])
            user._hashed_password = u["hashed_password"] # Восстанавливаем хеш
            if user.verify_password(password):
                return user
            return "Неверный пароль"
    return f"Пользователь '{username}' не найден"

def get_rate(from_cur, to_cur):
    f, t = from_cur.upper(), to_cur.upper()
    if f not in RATES or t not in RATES:
        raise ValueError(f"Неизвестная валюта: {f} или {t}")
    return RATES[f] / RATES[t]

def get_user_portfolio(user_id):
    portfolios = load_json("portfolios.json", [])
    for p in portfolios:
        if p["user_id"] == user_id:
            return p
    return None

def buy_currency(user_id, currency_code, amount):
    if amount <= 0: raise ValueError("Сумма должна быть > 0")
    curr = currency_code.upper()
    rate = get_rate(curr, "USD")
    cost_usd = amount * rate
    
    portfolios = load_json("portfolios.json", [])
    for p in portfolios:
        if p["user_id"] == user_id:
            wallets = p["wallets"]
            usd_balance = wallets.get("USD", {}).get("balance", 0.0)
            
            if usd_balance < cost_usd:
                raise ValueError(f"Недостаточно USD. Нужно {cost_usd:.2f}, доступно {usd_balance:.2f}")
            
            # Списываем USD
            wallets["USD"] = {"balance": usd_balance - cost_usd}
            # Добавляем купленную валюту
            current_curr_bal = wallets.get(curr, {}).get("balance", 0.0)
            wallets[curr] = {"balance": current_curr_bal + amount}
            
            save_json("portfolios.json", portfolios)
            return f"Покупка выполнена: {amount:.4f} {curr} по курсу {rate}. Списано {cost_usd:.2f} USD"

def sell_currency(user_id, currency_code, amount):
    if amount <= 0: raise ValueError("Сумма должна быть > 0")
    curr = currency_code.upper()
    rate = get_rate(curr, "USD")
    revenue_usd = amount * rate
    
    portfolios = load_json("portfolios.json", [])
    for p in portfolios:
        if p["user_id"] == user_id:
            wallets = p["wallets"]
            curr_balance = wallets.get(curr, {}).get("balance", 0.0)
            
            if curr_balance < amount:
                raise ValueError(f"Недостаточно {curr}. Доступно {curr_balance}")
            
            # Списываем валюту
            wallets[curr] = {"balance": curr_balance - amount}
            # Начисляем USD
            usd_balance = wallets.get("USD", {}).get("balance", 0.0)
            wallets["USD"] = {"balance": usd_balance + revenue_usd}
            
            save_json("portfolios.json", portfolios)
            return f"Продажа выполнена: {amount:.4f} {curr}. Начислено {revenue_usd:.2f} USD"