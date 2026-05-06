# icons.py
import os

# Centralized mapping of _data_type, categories, or types to their respective SVG filenames
ICON_MAP = {
    "action": "action-triangle-glyph",
    "actions": "action-triangle-glyph",
    "bastion": "bastions",
    "bastions": "bastions",
    "facility": "bastions",
    "bestiary": "bestiary",
    "condition": "conditions-diseases",
    "conditions": "conditions-diseases",
    "disease": "conditions-diseases",
    "deck": "decks",
    "deity": "deities",
    "feat": "action-triangle-glyph", # Feats default
    "feats": "action-triangle-glyph",
    "item": "items",
    "items": "items",
    "language": "languages",
    "supernatural gift": "supernatural-gifts",
    "psionic": "psionics",
    "spell": "spells",
    "spells": "spells",
    "vehicle": "vehicles",
    "maneuver": "maneuvers",
    "metamagic": "metamagic",
    "eldritch invocation": "eldritch-invocation",
    "arcane shot": "arcane-shot",
    "renown perk": "renown-perk",
    "elemental discipline": "elemental-discipline",
    "rune": "rune-knight-rune",
    "class": "classes",
    "subclass": "subclasses",
    "skill": "skills",
    "skills": "skills"
}

def resolve_card_icon_name(item, dataset_filename):
    """
    Determines the correct SVG icon name to use based on the item's data type, 
    category, or origin file.
    """
    # 1. Check strict _data_type first (This is what most items will hit)
    dtype = item.get('_data_type', '').lower().strip()
    if dtype in ICON_MAP:
        return ICON_MAP[dtype]
        
    # 2. Check origin dataset filename (Fallback for generic items)
    dataset_key = os.path.basename(dataset_filename).lower()
    if dataset_key.startswith('items') or 'items' in dataset_key:
        return 'items'
        
    # 3. Check specific type/category fields
    cat_value = str(item.get('category') or item.get('type') or '').lower().strip()
    if cat_value in ICON_MAP:
        return ICON_MAP[cat_value]
        
    if '|' in cat_value:
        cat_value_simple = cat_value.split('|')[0]
        if cat_value_simple in ICON_MAP:
            return ICON_MAP[cat_value_simple]
            
    # Universal Fallback
    return 'action-triangle-glyph'