import random
from data.tarot_deck import STANDARD_DECK

def draw_cards(count: int) -> list[dict]:
    """
    Тянет случайные карты из колоды.
    Возвращает список словарей с информацией о вытянутых картах.
    """
    # Берем все ключи карт (major_0, major_1 и т.д.)
    all_card_ids = list(STANDARD_DECK.keys())
    
    # Выбираем случайные уникальные карты (чтобы одна карта не выпала дважды)
    drawn_ids = random.sample(all_card_ids, min(count, len(all_card_ids)))
    
    drawn_cards = []
    for card_id in drawn_ids:
        # Копируем данные карты из справочника
        card_data = STANDARD_DECK[card_id].copy()
        
        # Случайно определяем: прямая или перевернутая (например, шанс 30% на перевернутую)
        is_reversed = random.random() < 0.3
        
        card_data["is_reversed"] = is_reversed
        # Формируем читаемое название для промпта ИИ
        position = " (Перевернутая)" if is_reversed else ""
        card_data["full_name"] = f"{card_data['name_ru']}{position}"
        
        drawn_cards.append(card_data)
        
    return drawn_cards