def enrich_deck(item, type_map=None):
    """
    Specific parsing and enrichment for Decks and Cards.
    """
    # Earthy brown theme for cards and decks
    item['primary_color'] = "#5D4037"
    item['bg_color'] = "#EFEBE9"
    item['icon_name'] = "decks"
    item['rarity_badge'] = ""
    
    d_type = str(item.get('_data_type', 'Deck')).title()
    item['meta_left'] = d_type
    
    return item