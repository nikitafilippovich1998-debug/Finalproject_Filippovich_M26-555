import functools
import logging

# ... твои старые импорты ...

# (Оставляем старые handle_errors, log_time, confirm_action)

def log_action(action_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Пытаемся вытащить данные из kwargs или args для лога
            user_id = kwargs.get('user_id', 'unknown')
            currency = kwargs.get('currency_code', '')
            amount = kwargs.get('amount', '')
            
            try:
                result = func(*args, **kwargs)
                logging.getLogger("valutatrade").info(
                    f"{action_name} user='{user_id}' currency='{currency}' amount={amount} result=OK"
                )
                return result
            except Exception as e:
                logging.getLogger("valutatrade").error(
                    f"{action_name} user='{user_id}' currency='{currency}' amount={amount} result=ERROR type={type(e).__name__} msg='{e}'"
                )
                raise
        return wrapper
    return decorator