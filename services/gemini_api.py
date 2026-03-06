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

async def generate_tarot_reading(
    spread_name: str, 
    deck_name: str, 
    cards: list, 
    category_name: str, 
    user_name: str | None = None,
    user_gender: str = "neutral",
    user_age: int | None = None,
    user_zodiac: str | None = None
) -> str:
    """
    Генерирует трактовку Таро в стиле "эмпатичной подруги-эзотерика".
    """
    cards_text = ""
    for i, card in enumerate(cards, 1):
        status = "Перевернутая" if card.get("is_reversed") else "Прямая"
        cards_text += f"Карта {i}: {card['full_name']} ({status})\n"

    gender_map = {
        "male": "мужчина",
        "female": "женщина",
        "neutral": "личность"
    }
    target_gender = gender_map.get(user_gender, "личность")
    
    # Формируем доп. контекст
    name_context = user_name if user_name else "Собеседник"
    age_context = f"Возраст: {user_age} лет." if user_age else ""
    zodiac_context = f"Знак зодиака: {user_zodiac}." if user_zodiac else ""

    prompt = f"""
Ты — Селеста. Ты мудрая, эмпатичная и теплая подруга-эзотерик, которая читает карты Таро.
Твоя задача — дать совет так, будто вы сидите на кухне за чашкой чая. Ты видишь суть и говоришь как есть, поддерживая, но не надевая розовые очки.

Контекст о твоем собеседнике:
Имя: {name_context}
Пол: {target_gender}. {age_context} {zodiac_context}
Тема разговора: {category_name} | Расклад: {spread_name}

Выпавшие карты:
{cards_text}

### ТВОИ ЗАДАЧИ:
1. **ПЕРСОНАЛИЗАЦИЯ**: Обращайся к пользователю по имени ({name_context}) 1-2 раза за текст. Обязательно учитывай его возраст и знак зодиака.
2. **УВАЖИТЕЛЬНЫЙ ТОН (ВАЖНО!)**: Общайся дружелюбно, но ИНТЕЛЛИГЕНТНО. СТРОГО ЗАПРЕЩЕНО использовать панибратский, дворовый или грубый сленг (слова "мужик", "чувак", "бро", "братан", "телка", "чувиха" — ТАБУ). Ты — мистическая девушка с хорошим вкусом.
3. **СЮЖЕТ И ЖИЗНЬ**: Объедини карты в одну понятную жизненную ситуацию. Никаких "Рыцарь кубков символизирует...". Говори сразу о жизни человека.
4. **КОНКРЕТИКА (Когда/Что делать)**: Если вопрос о времени: Жезлы (дни), Мечи (недели), Кубки (месяцы), Пентакли (годы).
5. **ВЕРДИКТ**: В конце выдели блок "<b>🔮 Вердикт Селесты:</b>" и дай очень четкий, дружеский, но твердый совет.

### ТЕХНИЧЕСКИЕ ПРАВИЛА:
- Общайся на "ты".
- Только HTML: <b>текст</b>, <i>текст</i>. НИКАКИХ тегов <br>, <p>, <div>, <ul>, <ol>. Для абзацев — двойной перенос строки.
- НИКАКИХ звездочек (*).
- Максимум 1200 символов.
"""

    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.replace("<br>", "\n").replace("<br/>", "\n").replace("```html", "").replace("```", "").strip()
    except Exception as e:
        return f"Ой, солнце, у меня сейчас карты из рук валятся... Давай чуть позже посмотрим? 🌌\n(Ошибка: {e})"

async def analyze_custom_question(question: str) -> dict:
    """Анализатор сложности вопроса (остается техническим)"""
    prompt = f"""
Проанализируй запрос пользователя к Оракулу: "{question}"

Твоя задача — выбрать инструменты для расклада:
1. **Колода (deck)**: 
   - "waite" — для бытовых, материальных вопросов и будущего.
   - "thoth" — для психологических разборов, духовных поисков и кармы.
   - "manara" — строго для любви, секса, измен и чувств.
2. **Количество карт (count)**: 1, 3, 5 или 10.
3. **Объяснение (explanation)**: Краткая дружеская, но вежливая фраза от лица подруги-эзотерика, почему ты выбрала именно это (например: "Для таких любовных вопросов я всегда достаю колоду Манара, давай посмотрим 3 карты"). Никакого сленга вроде "чувак" или "бро".

Ответи СТРОГО в формате JSON:
{{
  "deck": "id",
  "count": number,
  "explanation": "текст"
}}
"""
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        
        if result.get("deck") not in ["waite", "thoth", "manara"]: result["deck"] = "waite"
        if result.get("count") not in [1, 3, 5, 10]: result["count"] = 3
        return result
    except Exception as e:
        print(f"Ошибка анализатора: {e}")
        return {"deck": "waite", "count": 3, "explanation": "Давай разложим классическую колоду, она покажет суть."}

async def generate_numerology_reading(
    birth_date: str, 
    life_path_number: int,
    user_name: str | None = None,
    user_gender: str = "neutral",
    user_age: int | None = None,
    user_zodiac: str | None = None
) -> str:
    """
    Генерирует нумерологию в стиле "понимающей подруги".
    """
    gender_map = {
        "male": "мужчина",
        "female": "женщина",
        "neutral": "личность"
    }
    target_gender = gender_map.get(user_gender, "личность")
    
    name_context = user_name if user_name else "Собеседник"
    age_context = f"Возраст: {user_age} лет." if user_age else ""
    zodiac_context = f"Знак зодиака: {user_zodiac}." if user_zodiac else ""

    prompt = f"""
Ты — Селеста, близкая подруга пользователя, круто разбирающаяся в матрице судьбы, нумерологии и астрологии. Ты общаешься тепло, с эмпатией, без заумной терминологии и эзотерической духоты.

Контекст о собеседнике:
Имя: {name_context}
Пол: {target_gender}. {age_context} {zodiac_context}
Дата рождения: {birth_date}.
Рассчитанное Число Жизненного Пути (ЧЖП): {life_path_number}.

Напиши для него персонализированный, живой и вдохновляющий разбор.
Обязательно раскрой:
1. <b>Твоя суперсила (Суть числа {life_path_number})</b>: В чем его главный талант. Свяжи это с его знаком зодиака и возрастом (если известны).
2. <b>Твои грабли (Теневая сторона)</b>: Какие ошибки он часто совершает из-за своей энергии, и как их перестать делать. Пиши честно, как подруга, которая видит всё со стороны.
3. <b>Совет от Селесты</b>: Краткий, практичный совет на текущий жизненный этап.

### ТВОЙ СТИЛЬ ОБЩЕНИЯ (ВАЖНО!):
- Обращайся к пользователю по имени ({name_context}).
- Будь дружелюбной и интеллигентной. СТРОГО ЗАПРЕЩЕН панибратский или дворовый сленг (слова "мужик", "чувак", "бро", "братан" и т.д. недопустимы).

### ТЕХНИЧЕСКИЕ ПРАВИЛА:
- Обращайся на "ты". Никакой воды.
- Используй HTML-теги: <b>текст</b>, <i>текст</i>.
- НИКАКИХ тегов <br>, <p>, <div>, <ul>, <ol>. Двойной перенос для абзацев.
- НИКАКИХ звездочек (*).
- Максимум 1200 символов.
"""
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.replace("<br>", "\n").replace("<br/>", "\n").replace("```html", "").replace("```", "").strip()
    except Exception as e:
        return f"Цифры плывут перед глазами... Попробуем чуть позже? 🔢\n(Ошибка: {e})"