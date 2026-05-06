def enrich_condition(item, type_map=None):
    """
    Specific parsing and enrichment for Conditions, Diseases, and Status effects.
    """
    # Standard purple theme for afflictions and statuses
    item['primary_color'] = "#4A148C"
    item['bg_color'] = "#F3E5F5"
    item['icon_name'] = "conditions-diseases"
    item['rarity_badge'] = ""
    
    # Capitalize the specific data type (Condition, Disease, or Status)
    c_type = str(item.get('_data_type', 'Condition')).title()
    item['meta_left'] = c_type
    
    return item