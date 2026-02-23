import phonenumbers

def validate_phone_number(v: str) -> str:
    try:
        parsed = phonenumbers.parse(v, "RU")
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Неверный номер телефона")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        raise ValueError("Неверный формат номера телефона")
    


def validate_password(v:str)->str:
    if len(v)< 6:
        raise ValueError("Пароль должен быть не менее 6 символов")
    if len(v) > 72:
        raise ValueError("Пароль должен быть не более 72 символов")
    
    return v