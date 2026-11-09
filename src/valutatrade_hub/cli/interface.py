import shlex

import prompt

from valutatrade_hub.core.exceptions import (
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.core.usecases import (
    buy_currency,
    get_rate,
    get_user_portfolio,
    login_user,
    register_user,
    sell_currency,
)

current_user = None

def run_cli():
    global current_user
    print("Добро пожаловать в ValutaTrade Hub!")
    
    while True:
        try:
            cmd_str = prompt.string("> ")
        except EOFError: break
        
        if not cmd_str.strip(): continue
        args = shlex.split(cmd_str)
        command = args[0]

        try:
            if command == "exit":
                break
            elif command == "register":
                if "--username" in args and "--password" in args:
                    u = args[args.index("--username") + 1]
                    p = args[args.index("--password") + 1]
                    print(register_user(u, p))
                else: print("Использование: register --username <name> --password <pass>")
            
            elif command == "login":
                if "--username" in args and "--password" in args:
                    u = args[args.index("--username") + 1]
                    p = args[args.index("--password") + 1]
                    res = login_user(u, p)
                    if isinstance(res, str): print(res)
                    else:
                        current_user = res
                        print(f"Вы вошли как '{current_user.username}'")
                else: print("Использование: login --username <name> --password <pass>")

            elif command == "show-portfolio":
                if not current_user:
                    print("Сначала выполните login")
                    continue
                
                base_cur = "USD"
                if "--base" in args:
                    base_cur = args[args.index("--base") + 1].upper()
                
                p = get_user_portfolio(current_user.user_id)
                if not p or not p["wallets"]:
                    print("Ваш портфель пуст.")
                    continue
                
                print(f"Портфель пользователя '{current_user.username}' (база: {base_cur})")
                total_val = 0.0
                for cur, data in p["wallets"].items():
                    bal = data["balance"]
                    if bal > 0:
                        rate = get_rate(cur, base_cur)
                        val_in_base = bal * rate
                        total_val += val_in_base
                        print(f"  - {cur}: {bal:.4f} -> {val_in_base:.2f} {base_cur}")
                print("-" * 40)
                print(f"ИТОГО: {total_val:.2f} {base_cur}")

            elif command == "get-rate":
                if "--from" in args and "--to" in args:
                    f = args[args.index("--from") + 1]
                    t = args[args.index("--to") + 1]
                    rate = get_rate(f, t)
                    print(f"Курс {f.upper()}->{t.upper()}: {rate:.6f}")
                else: print("Использование: get-rate --from <cur> --to <cur>")

            elif command == "buy":
                if not current_user:
                    print("Сначала выполните login")
                    continue
                if "--currency" in args and "--amount" in args:
                    c = args[args.index("--currency") + 1]
                    a = float(args[args.index("--amount") + 1])
                    print(buy_currency(current_user.user_id, c, a))
                else: print("Использование: buy --currency <cur> --amount <num>")

            elif command == "sell":
                if not current_user:
                    print("Сначала выполните login")
                    continue
                if "--currency" in args and "--amount" in args:
                    c = args[args.index("--currency") + 1]
                    a = float(args[args.index("--amount") + 1])
                    print(sell_currency(current_user.user_id, c, a))
                else: print("Использование: sell --currency <cur> --amount <num>")

            else:
                print("Неизвестная команда")
        except InsufficientFundsError as e:
            print(f"Ошибка: {e}")
        except CurrencyNotFoundError as e:
            print(f"Ошибка: {e}. Проверьте код валюты (help get-rate).")
        except Exception as e: #noqa: BLE001
            print(f"Ошибка: {e}")