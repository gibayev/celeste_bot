# services/numerology_engine.py

def calculate_life_path_number(date_str: str) -> int:
    """
    Рассчитывает Число Жизненного Пути по дате рождения.
    Формат ожидаемой даты: 'DD.MM.YYYY' (например, '15.04.1995')
    """
    # Оставляем только цифры из строки
    digits = [int(char) for char in date_str if char.isdigit()]
    
    if not digits:
        raise ValueError("В дате нет цифр")

    total = sum(digits)
    
    # Сводим к однозначному числу, учитывая мастер-числа 11, 22, 33
    while total > 9 and total not in (11, 22, 33):
        total = sum(int(d) for d in str(total))
        
    return total

# Можешь протестировать прямо в этом файле:
# print(calculate_life_path_number("29.02.2000")) # Выведет 6