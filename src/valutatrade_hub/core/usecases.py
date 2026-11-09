from valutatrade_hub.core.models import User, Portfolio
from valutatrade_hub.storage import load_json, save_json

# Заглушка курсов (для простоты)
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
    
    # Создаем пустой портфель
    portfolios = load_json("portfolios.json", [])
    portfolios.append({"user_id": new_id, "wallets": {}})
    save_json("portfolios.json", portfolios)
    
    return f"Пользователь '{username}' зарегистрирован (id={new_id})"

def login_user(username, password):
    users = load_json("users.json", [])
    for u in users:
        if u["username"] == username:
            user = User(u["user_id"], u["username"], "", u["salt"])
            if user.verify_password(password):
                return user
            return "Неверный пароль"
    return f"Пользователь '{username}' не найден"

def get_rate(from_cur, to_cur):
    f, t = from_cur.upper(), to_cur.upper()
    if f not in RATES or t not in RATES:
        raise ValueError("Неизвестная валюта")
    # Конвертация через USD
    return RATES[f] / RATES[t]