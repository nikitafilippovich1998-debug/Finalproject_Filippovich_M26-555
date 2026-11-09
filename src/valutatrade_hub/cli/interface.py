import shlex
import prompt
from valutatrade_hub.core.usecases import register_user, login_user, get_rate
from valutatrade_hub.storage import load_json, save_json

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
                # register --username alice --password 1234
                if "--username" in args and "--password" in args:
                    u_idx = args.index("--username") + 1
                    p_idx = args.index("--password") + 1
                    print(register_user(args[u_idx], args[p_idx]))
            elif command == "login":
                if "--username" in args and "--password" in args:
                    u_idx = args.index("--username") + 1
                    p_idx = args.index("--password") + 1
                    res = login_user(args[u_idx], args[p_idx])
                    if isinstance(res, str): print(res)
                    else:
                        current_user = res
                        print(f"Вы вошли как '{current_user.username}'")
            elif command == "get-rate":
                if "--from" in args and "--to" in args:
                    f_idx = args.index("--from") + 1
                    t_idx = args.index("--to") + 1
                    rate = get_rate(args[f_idx], args[t_idx])
                    print(f"Курс {args[f_idx].upper()}->{args[t_idx].upper()}: {rate:.6f}")
            
            # Добавь сюда команды show-portfolio, buy, sell по аналогии...
            elif command == "show-portfolio":
                if not current_user: print("Сначала выполните login")
                else: print(f"Портфель {current_user.username} (тут будет логика вывода)")
            else:
                print("Неизвестная команда")
        except Exception as e:
            print(f"Ошибка: {e}")