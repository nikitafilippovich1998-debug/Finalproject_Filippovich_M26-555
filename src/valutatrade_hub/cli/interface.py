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
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.updater import RatesUpdater

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

            # НОВАЯ КОМАНДА: update-rates
            elif command == "update-rates":
                source = None
                if "--source" in args:
                    source = args[args.index("--source") + 1]
                
                print("INFO: Starting rates update...")
                try:
                    updater = RatesUpdater(ParserConfig())
                    count = updater.run_update(source)
                    print(f"Update successful. Total rates updated: {count}")
                except Exception as e: # noqa: BLE001
                    print(f"Ошибка обновления: {e}")

            # НОВАЯ КОМАНДА: show-rates
            elif command == "show-rates":
                import json
                import os
                path = ParserConfig().RATES_FILE_PATH
                if not os.path.exists(path):
                    print("Локальный кеш курсов пуст. Выполните 'update-rates'.")
                    continue
                
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                pairs = data.get("pairs", {})
                print(f"Rates from cache (updated at {data.get('last_refresh')}):")
                
                # Фильтрация по валюте
                currency_filter = None
                if "--currency" in args:
                    currency_filter = args[args.index("--currency") + 1].upper()
                
                for pair, info in pairs.items():
                    if currency_filter and not pair.startswith(currency_filter):
                        continue
                    print(f"  - {pair}: {info['rate']}")

            else:
                print("Неизвестная команда")
        except InsufficientFundsError as e:
            print(f"Ошибка: {e}")
        except CurrencyNotFoundError as e:
            print(f"Ошибка: {e}. Проверьте код валюты (help get-rate).")
        except Exception as e: #noqa: BLE001
            print(f"Ошибка: {e}")