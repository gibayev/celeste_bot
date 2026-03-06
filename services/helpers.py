from datetime import datetime

def calculate_dynamic_age(birth_date_str: str) -> int | None:
    """
    Рассчитывает точный возраст на сегодняшний день.
    Автоматически прибавляет год в день рождения.
    """
    if not birth_date_str:
        return None
    try:
        birth_date = datetime.strptime(birth_date_str, "%d.%m.%Y")
        today = datetime.now()
        
        # Считаем разницу лет. Вычитаем 1, если в этом году день рождения еще не наступил
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except ValueError:
        return None

def get_zodiac_sign(birth_date_str: str) -> str | None:
    """
    Определяет знак зодиака по дате рождения.
    """
    if not birth_date_str:
        return None
    try:
        birth_date = datetime.strptime(birth_date_str, "%d.%m.%Y")
        d = birth_date.day
        m = birth_date.month
        
        if (m == 3 and d >= 21) or (m == 4 and d <= 19): return "Овен ♈️"
        elif (m == 4 and d >= 20) or (m == 5 and d <= 20): return "Телец ♉️"
        elif (m == 5 and d >= 21) or (m == 6 and d <= 20): return "Близнецы ♊️"
        elif (m == 6 and d >= 21) or (m == 7 and d <= 22): return "Рак ♋️"
        elif (m == 7 and d >= 23) or (m == 8 and d <= 22): return "Лев ♌️"
        elif (m == 8 and d >= 23) or (m == 9 and d <= 22): return "Дева ♍️"
        elif (m == 9 and d >= 23) or (m == 10 and d <= 22): return "Весы ♎️"
        elif (m == 10 and d >= 23) or (m == 11 and d <= 21): return "Скорпион ♏️"
        elif (m == 11 and d >= 22) or (m == 12 and d <= 21): return "Стрелец ♐️"
        elif (m == 12 and d >= 22) or (m == 1 and d <= 19): return "Козерог ♑️"
        elif (m == 1 and d >= 20) or (m == 2 and d <= 18): return "Водолей ♒️"
        elif (m == 2 and d >= 19) or (m == 3 and d <= 20): return "Рыбы ♓️"
    except ValueError:
        return None