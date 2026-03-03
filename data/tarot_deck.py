# --- ДОСТУПНЫЕ КОЛОДЫ ---
DECKS = {
    "waite": {
        "name": "Классическое Таро Уэйта",
        "is_premium": False,
        "description": "Универсальная колода, идеально подходит для любых вопросов."
    },
    "thoth": {
        "name": "Таро Тота (Кроули)",
        "is_premium": True,
        "description": "Глубокая, эзотерическая колода для сложных психологических разборов."
    },
    "manara": {
        "name": "Таро Манара",
        "is_premium": True,
        "description": "Лучший выбор для вопросов любви, страсти и скрытых желаний."
    }
}

# --- КАТЕГОРИИ РАСКЛАДОВ ---
CATEGORIES = {
    "general": "🌌 Общие вопросы",
    "love": "❤️ Любовь и Отношения",
    "career": "💼 Работа и Финансы",
    "custom": "✍️ Свой вопрос (Premium)"
}

# --- ВИДЫ РАСКЛАДОВ ---
SPREADS = {
    # Общие
    "day_1": {
        "category": "general",
        "name": "Карта дня",
        "cards_count": 1,
        "is_premium": False,
        "recommended_deck": "waite"
    },
    "past_present_future": {
        "category": "general",
        "name": "Прошлое, Настоящее, Будущее",
        "cards_count": 3,
        "is_premium": False,
        "recommended_deck": "waite"
    },
    "celtic_cross": {
        "category": "general",
        "name": "Кельтский крест (10 карт)",
        "cards_count": 10,
        "is_premium": True,
        "recommended_deck": "thoth"
    },
    # Любовь
    "love_3": {
        "category": "love",
        "name": "Мысли, Чувства, Действия",
        "cards_count": 3,
        "is_premium": False,
        "recommended_deck": "manara"
    },
    "new_love_5": {
        "category": "love",
        "name": "Перспективы новых отношений",
        "cards_count": 5,
        "is_premium": True,
        "recommended_deck": "manara"
    },
    # Работа
    "career_path": {
        "category": "career",
        "name": "Выбор пути",
        "cards_count": 3,
        "is_premium": False,
        "recommended_deck": "waite"
    }
}

# --- БАЗА КАРТ ---
# Мы храним только логику. Картинки бот будет искать по ключу (например: assets/tarot/waite/major_0.jpg)
# Тебе нужно будет переименовать твои файлы картинок под эти ключи!
CARDS_INFO = {
    "major_0": {"name_ru": "Шут", "name_en": "The Fool", "is_major": True},
    "major_1": {"name_ru": "Маг", "name_en": "The Magician", "is_major": True},
    "major_2": {"name_ru": "Жрица", "name_en": "The High Priestess", "is_major": True},
    # Сюда продолжишь добавлять major_3, cups_1, swords_king и т.д.
}