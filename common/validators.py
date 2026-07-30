from datetime import date, datetime
from rest_framework.exceptions import ValidationError

def validate_product_creator_age(request):
    token_payload = request.auth
    if not token_payload:
        raise ValidationError("Пользователь не авторизован.")

    birthdate_str = token_payload.get('birthdate')
    if not birthdate_str:
        raise ValidationError("Укажите дату рождения, чтобы создать продукт.")

    try:
        birthday = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        raise ValidationError("Некорректный формат даты рождения в токене.")

    today = date.today()
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")