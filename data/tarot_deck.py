# --- ДОСТУПНЫЕ КОЛОДЫ ---
DECKS = {
    "waite": {
        "name": "Классическое Таро Уэйта",
        "is_premium": False,
        "description": "Универсальная колода, идеально подходит для любых вопросов."
    }
}

CATEGORIES = {
    "general": "🌌 Общие вопросы",
    "love": "❤️ Любовь и Отношения",
    "career": "💼 Работа и Финансы",
    "health": "🌿 Здоровье и Энергия",
    "timing": "⏳ Вопросы «Когда?»",
    "custom": "✍️ Свой вопрос (Premium)"
}

SPREADS = {
    # Общие
    "day_1": {"category": "general", "name": "Карта дня", "cards_count": 1, "is_premium": False},
    "past_present_future": {"category": "general", "name": "Прошлое/Настоящее/Будущее", "cards_count": 3, "is_premium": False},
    
    # Любовь
    "love_3": {"category": "love", "name": "Мысли/Чувства/Действия", "cards_count": 3, "is_premium": False},
    "relationship_prospects": {"category": "love", "name": "Перспективы союза", "cards_count": 5, "is_premium": True},
    
    # Работа и деньги
    "career_path": {"category": "career", "name": "Развитие карьеры", "cards_count": 3, "is_premium": False},
    "money_flow": {"category": "career", "name": "Денежный поток", "cards_count": 4, "is_premium": True},
    
    # Здоровье
    "health_state": {"category": "health", "name": "Общее состояние", "cards_count": 3, "is_premium": False},

    # ТАЙМИНГ (То, что ты просил)
    "when_it_happens": {
        "category": "timing", 
        "name": "Когда это произойдет?", 
        "cards_count": 1, 
        "is_premium": True,
        "description": "Расклад на одну карту для определения сроков."
    }
}

# --- БАЗА КАРТ ---
# Формат ключа должен совпадать с именами файлов в assets/tarot/waite/
CARDS_INFO = {
    # Старшие Арканы (Major Arcana)
    "major_0": {"name_ru": "Шут", "name_en": "The Fool", "is_major": True},
    "major_1": {"name_ru": "Маг", "name_en": "The Magician", "is_major": True},
    "major_2": {"name_ru": "Жрица", "name_en": "The High Priestess", "is_major": True},
    "major_3": {"name_ru": "Императрица", "name_en": "The Empress", "is_major": True},
    "major_4": {"name_ru": "Император", "name_en": "The Emperor", "is_major": True},
    "major_5": {"name_ru": "Иерофант", "name_en": "The Hierophant", "is_major": True},
    "major_6": {"name_ru": "Влюбленные", "name_en": "The Lovers", "is_major": True},
    "major_7": {"name_ru": "Колесница", "name_en": "The Chariot", "is_major": True},
    "major_8": {"name_ru": "Сила", "name_en": "Strength", "is_major": True},
    "major_9": {"name_ru": "Отшельник", "name_en": "The Hermit", "is_major": True},
    "major_10": {"name_ru": "Колесо Фортуны", "name_en": "Wheel of Fortune", "is_major": True},
    "major_11": {"name_ru": "Справедливость", "name_en": "Justice", "is_major": True},
    "major_12": {"name_ru": "Повешенный", "name_en": "The Hanged Man", "is_major": True},
    "major_13": {"name_ru": "Смерть", "name_en": "Death", "is_major": True},
    "major_14": {"name_ru": "Умеренность", "name_en": "Temperance", "is_major": True},
    "major_15": {"name_ru": "Дьявол", "name_en": "The Devil", "is_major": True},
    "major_16": {"name_ru": "Башня", "name_en": "The Tower", "is_major": True},
    "major_17": {"name_ru": "Звезда", "name_en": "The Star", "is_major": True},
    "major_18": {"name_ru": "Луна", "name_en": "The Moon", "is_major": True},
    "major_19": {"name_ru": "Солнце", "name_en": "The Sun", "is_major": True},
    "major_20": {"name_ru": "Суд", "name_en": "Judgement", "is_major": True},
    "major_21": {"name_ru": "Мир", "name_en": "The World", "is_major": True},

    # Жезлы (Wands)
    "wands_1": {"name_ru": "Туз Жезлов", "name_en": "Ace of Wands", "is_major": False},
    "wands_2": {"name_ru": "Двойка Жезлов", "name_en": "Two of Wands", "is_major": False},
    "wands_3": {"name_ru": "Тройка Жезлов", "name_en": "Three of Wands", "is_major": False},
    "wands_4": {"name_ru": "Четверка Жезлов", "name_en": "Four of Wands", "is_major": False},
    "wands_5": {"name_ru": "Пятерка Жезлов", "name_en": "Five of Wands", "is_major": False},
    "wands_6": {"name_ru": "Шестерка Жезлов", "name_en": "Six of Wands", "is_major": False},
    "wands_7": {"name_ru": "Семерка Жезлов", "name_en": "Seven of Wands", "is_major": False},
    "wands_8": {"name_ru": "Восьмерка Жезлов", "name_en": "Eight of Wands", "is_major": False},
    "wands_9": {"name_ru": "Девятка Жезлов", "name_en": "Nine of Wands", "is_major": False},
    "wands_10": {"name_ru": "Десятка Жезлов", "name_en": "Ten of Wands", "is_major": False},
    "wands_page": {"name_ru": "Паж Жезлов", "name_en": "Page of Wands", "is_major": False},
    "wands_knight": {"name_ru": "Рыцарь Жезлов", "name_en": "Knight of Wands", "is_major": False},
    "wands_queen": {"name_ru": "Королева Жезлов", "name_en": "Queen of Wands", "is_major": False},
    "wands_king": {"name_ru": "Король Жезлов", "name_en": "King of Wands", "is_major": False},

    # Кубки (Cups)
    "cups_1": {"name_ru": "Туз Кубков", "name_en": "Ace of Cups", "is_major": False},
    "cups_2": {"name_ru": "Двойка Кубков", "name_en": "Two of Cups", "is_major": False},
    "cups_3": {"name_ru": "Тройка Кубков", "name_en": "Three of Cups", "is_major": False},
    "cups_4": {"name_ru": "Четверка Кубков", "name_en": "Four of Cups", "is_major": False},
    "cups_5": {"name_ru": "Пятерка Кубков", "name_en": "Five of Cups", "is_major": False},
    "cups_6": {"name_ru": "Шестерка Кубков", "name_en": "Six of Cups", "is_major": False},
    "cups_7": {"name_ru": "Семерка Кубков", "name_en": "Seven of Cups", "is_major": False},
    "cups_8": {"name_ru": "Восьмерка Кубков", "name_en": "Eight of Cups", "is_major": False},
    "cups_9": {"name_ru": "Девятка Кубков", "name_en": "Nine of Cups", "is_major": False},
    "cups_10": {"name_ru": "Десятка Кубков", "name_en": "Ten of Cups", "is_major": False},
    "cups_page": {"name_ru": "Паж Кубков", "name_en": "Page of Cups", "is_major": False},
    "cups_knight": {"name_ru": "Рыцарь Кубков", "name_en": "Knight of Cups", "is_major": False},
    "cups_queen": {"name_ru": "Королева Кубков", "name_en": "Queen of Cups", "is_major": False},
    "cups_king": {"name_ru": "Король Кубков", "name_en": "King of Cups", "is_major": False},

    # Мечи (Swords)
    "swords_1": {"name_ru": "Туз Мечей", "name_en": "Ace of Swords", "is_major": False},
    "swords_2": {"name_ru": "Двойка Мечей", "name_en": "Two of Swords", "is_major": False},
    "swords_3": {"name_ru": "Тройка Мечей", "name_en": "Three of Swords", "is_major": False},
    "swords_4": {"name_ru": "Четверка Мечей", "name_en": "Four of Swords", "is_major": False},
    "swords_5": {"name_ru": "Пятерка Мечей", "name_en": "Five of Swords", "is_major": False},
    "swords_6": {"name_ru": "Шестерка Мечей", "name_en": "Six of Swords", "is_major": False},
    "swords_7": {"name_ru": "Семерка Мечей", "name_en": "Seven of Swords", "is_major": False},
    "swords_8": {"name_ru": "Восьмерка Мечей", "name_en": "Eight of Swords", "is_major": False},
    "swords_9": {"name_ru": "Девятка Мечей", "name_en": "Nine of Swords", "is_major": False},
    "swords_10": {"name_ru": "Десятка Мечей", "name_en": "Ten of Swords", "is_major": False},
    "swords_page": {"name_ru": "Паж Мечей", "name_en": "Page of Swords", "is_major": False},
    "swords_knight": {"name_ru": "Рыцарь Мечей", "name_en": "Knight of Swords", "is_major": False},
    "swords_queen": {"name_ru": "Королева Мечей", "name_en": "Queen of Swords", "is_major": False},
    "swords_king": {"name_ru": "Король Мечей", "name_en": "King of Swords", "is_major": False},

    # Пентакли (Pentacles)
    "pents_1": {"name_ru": "Туз Пентаклей", "name_en": "Ace of Pentacles", "is_major": False},
    "pents_2": {"name_ru": "Двойка Пентаклей", "name_en": "Two of Pentacles", "is_major": False},
    "pents_3": {"name_ru": "Тройка Пентаклей", "name_en": "Three of Pentacles", "is_major": False},
    "pents_4": {"name_ru": "Четверка Пентаклей", "name_en": "Four of Pentacles", "is_major": False},
    "pents_5": {"name_ru": "Пятерка Пентаклей", "name_en": "Five of Pentacles", "is_major": False},
    "pents_6": {"name_ru": "Шестерка Пентаклей", "name_en": "Six of Pentacles", "is_major": False},
    "pents_7": {"name_ru": "Семерка Пентаклей", "name_en": "Seven of Pentacles", "is_major": False},
    "pents_8": {"name_ru": "Восьмерка Пентаклей", "name_en": "Eight of Pentacles", "is_major": False},
    "pents_9": {"name_ru": "Девятка Пентаклей", "name_en": "Nine of Pentacles", "is_major": False},
    "pents_10": {"name_ru": "Десятка Пентаклей", "name_en": "Ten of Pentacles", "is_major": False},
    "pents_page": {"name_ru": "Паж Пентаклей", "name_en": "Page of Pentacles", "is_major": False},
    "pents_knight": {"name_ru": "Рыцарь Пентаклей", "name_en": "Knight of Pentacles", "is_major": False},
    "pents_queen": {"name_ru": "Королева Пентаклей", "name_en": "Queen of Pentacles", "is_major": False},
    "pents_king": {"name_ru": "Король Пентаклей", "name_en": "King of Pentacles", "is_major": False},
}