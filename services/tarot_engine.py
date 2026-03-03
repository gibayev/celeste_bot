import random
from data.tarot_deck import CARDS_INFO

def draw_cards(count: int, deck_id: str = "waite") -> list[dict]:
    """
    Тянет случайные карты.
    deck_id определяет, из какой папки брать картинки (например, "waite" или "thoth").
    """
    all_card_ids = list(CARDS_INFO.keys())
    
    # Берем случайные ID карт
    drawn_ids = random.sample(all_card_ids, min(count, len(all_card_ids)))
    
    drawn_cards = []
    for card_id in drawn_ids:
        card_data = CARDS_INFO[card_id].copy()
        
        # Определяем перевернутость (30% шанс)
        is_reversed = random.random() < 0.3
        card_data["is_reversed"] = is_reversed
        
        position = " (Перевернутая)" if is_reversed else ""
        card_data["full_name"] = f"{card_data['name_ru']}{position}"
        
        # ГЕНЕРИРУЕМ ПУТЬ К КАРТИНКЕ ДИНАМИЧЕСКИ
        card_data["image_path"] = f"assets/tarot/{deck_id}/{card_id}.jpg"
        
        drawn_cards.append(card_data)
        
    return drawn_cards