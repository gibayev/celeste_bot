import os
import json
from google import genai
from dotenv import load_dotenv

# Загружаем настройки
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("🚨 СТОП! Переменная GEMINI_API_KEY пустая. Проверь файл .env!")

# Инициализируем клиента
client = genai.Client(api_key=GEMINI_API_KEY)

async def generate_tarot_reading(spread_name: str, deck_name: str, cards: list, category_name: str, user_gender: str = "neutral") -> str:
    """
    Генерирует профессиональную трактовку расклада с упором на комбинации и конкретику.
    """
    # Подготовка описания карт
    cards_text = ""
    for i, card in enumerate(cards, 1):
        status = "Перевернутая" if card.get("is_reversed") else "Прямая"
        cards_text += f"Карта {i}: {card['full_name']} ({status})\n"

    # Маппинг пола для корректных окончаний
    gender_map = {
        "male": "мужчина (используй мужской род: ты пришел, ты почувствовал)",
        "female": "женщина (используй женский род: ты пришла, ты почувствовала)",
        "neutral": "личность (используй нейтральные формулировки)"
    }
    target_gender = gender_map.get(user_gender, "личность")

    prompt = f"""
Ты — Селеста, профессиональный таролог с 20-летним стажем. Твой стиль: мистический, лаконичный, лишенный "воды" и общих фраз.
Твой клиент: {target_gender}.
Тема: {category_name} | Расклад: {spread_name} | Колода: {deck_name}

Выпавшие карты:
{cards_text}

### ТВОИ ЗАДАЧИ:
1. **СЮЖЕТ И КОМБИНАЦИИ**: Категорически запрещено трактовать карты по отдельности. Описывай их как единую историю. Как одна карта усиливает или подавляет другую? (Например: "Рыцарь Мечей вносит хаос в стабильность 4 Пентаклей, что означает внезапную трату накоплений").
2. **КОНКРЕТИКА И ВРЕМЯ**: Если вопрос подразумевает "Когда?", используй масти: 
   - Жезлы: дни/весна. 
   - Мечи: недели/осень. 
   - Кубки: месяцы/лето. 
   - Пентакли: годы/зима. 
   Давай примерный срок, основываясь на доминирующей масти.
3. **БЕЗ ВОДЫ**: Никаких "карты лишь советуют", "все в твоих руках". Пиши так, будто ты видишь судьбу насквозь.
4. **ВЕРДИКТ**: В конце выдели блок "<b>🔮 Вердикт Селесты:</b>". Дай максимально четкий ответ: Да/Нет, Срок, или Конкретное действие. Сделай выбор за пользователя на основе энергии карт.

### ТЕХНИЧЕСКИЕ ПРАВИЛА:
- Только HTML: <b>текст</b>, <i>текст</i>.
- НИКАКИХ тегов <br>, <p>, <div>, <ul>. Для абзацев используй двойной перенос строки.
- НИКАКИХ звездочек (*) для выделения.
- Максимум 1200 символов. Будь емкой.
"""

    try:
        response = await client.aio.models.generate_content(
            model='gemini-3.0-flash', # Оптимально для скорости и логики
            contents=prompt
        )
        
        # Финальная чистка текста
        cleaned_text = response.text.replace("<br>", "\n").replace("<br/>", "\n").replace("```html", "").replace("```", "").strip()
        return cleaned_text
    except Exception as e:
        return f"Звезды сегодня слишком туманны... Попробуй позже. 🌌\n(Ошибка: {e})"

async def analyze_custom_question(question: str) -> dict:
    """
    Интеллектуальный анализатор сложности вопроса. 
    Подбирает оптимальную колоду и количество карт, объясняя причину.
    """
    prompt = f"""
Проанализируй запрос пользователя к Оракулу: "{question}"

Твоя задача — выбрать инструменты для расклада:
1. **Колода (deck)**: 
   - "waite" — для бытовых, материальных вопросов и будущего.
   - "thoth" — для психологических разборов, духовных поисков и кармы.
   - "manara" — строго для любви, секса, измен и чувств.
2. **Количество карт (count)**: 1, 3, 5 или 10 (10 только для супер-сложных жизненных драм).
3. **Объяснение (explanation)**: Краткая мистическая фраза, почему ты выбрала именно это.

Ответи СТРОГО в формате JSON:
{{
  "deck": "id",
  "count": number,
  "explanation": "твое объяснение на русском"
}}
"""

    try:
        response = await client.aio.models.generate_content(
            model='gemini-3.0-flash',
            contents=prompt
        )
        # Убираем возможный markdown
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        
        # Валидация
        if result.get("deck") not in ["waite", "thoth", "manara"]: result["deck"] = "waite"
        if result.get("count") not in [1, 3, 5, 10]: result["count"] = 3
        
        return result
    except Exception as e:
        print(f"Ошибка анализатора: {e}")
        return {
            "deck": "waite", 
            "count": 3, 
            "explanation": "Для твоего вопроса лучше всего подойдет классика."
        }