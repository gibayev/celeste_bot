# Базовый справочник карт Таро (для примера добавим Старшие Арканы)
# В будущем ты сможешь расширить этот список до 78 карт.

STANDARD_DECK = {
    "major_0": {
        "name_ru": "Шут",
        "name_en": "The Fool",
        "image_path": "assets/tarot/standard/0_fool.jpg",
        "is_major": True
    },
    "major_1": {
        "name_ru": "Маг",
        "name_en": "The Magician",
        "image_path": "assets/tarot/standard/1_magician.jpg",
        "is_major": True
    },
    "major_2": {
        "name_ru": "Жрица",
        "name_en": "The High Priestess",
        "image_path": "assets/tarot/standard/2_priestess.jpg",
        "is_major": True
    },
    # Сюда потом добавишь остальные карты (Мечи, Кубки, Пентакли, Жезлы)
}

# Виды раскладов
SPREADS = {
    "card_1": {
        "name": "Карта дня",
        "cards_count": 1,
        "is_premium": False,
        "description": "Один ответ на волнующий вопрос или совет на день."
    },
    "cards_3": {
        "name": "Прошлое, Настоящее, Будущее",
        "cards_count": 3,
        "is_premium": False,
        "description": "Классический расклад для анализа ситуации."
    },
    "cards_5_celtic": {
        "name": "Кельтский крест (Мини)",
        "cards_count": 5,
        "is_premium": True,
        "description": "Глубокий анализ скрытых мотивов и итогов (Premium)."
    }
}