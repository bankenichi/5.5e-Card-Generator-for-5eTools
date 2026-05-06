def get_action_color(time_str):
    t = str(time_str).lower()
    if "bonus" in t: return ("#0D47A1", "#E3F2FD")  # Blue
    if "reaction" in t: return ("#B71C1C", "#FFEBEE")  # Red
    if "free" in t: return ("#4A148C", "#F3E5F5")  # Purple
    if "varies" in t: return ("#5D4037", "#EFEBE9")  # Brown
    return ("#1B5E20", "#F1F8E9")  # Green

def enrich_action(item, type_map=None):
    """
    Specific parsing and enrichment for Actions.
    Extracts time properties and delegates the color scheme based on action type.
    """
    tl = item.get('time', [])
    
    # Resolve the category abbreviation if possible
    raw_cat = str(item.get('category') or item.get('type') or '').split('|')[0].replace('$', '').strip().upper()
    if type_map and raw_cat in type_map:
        ts = type_map[raw_cat]
    else:
        ts = raw_cat
        
    # Format the time string
    if tl: 
        ts = f"{tl[0].get('number', '')} {tl[0].get('unit', 'Varies')}".strip().upper() if isinstance(tl[0], dict) else str(tl[0]).upper()
    
    pc, bc = get_action_color(ts)
    item['primary_color'] = pc
    item['bg_color'] = bc
    
    # Set the top-left metadata string
    req_att = item.get('reqAttune')
    if req_att:
        item['meta_left'] = f"{ts}, Req. Attune" if ts else "Req. Attune"
    else:
        item['meta_left'] = ts

    # Actions don't have rarities
    item['rarity_badge'] = ""
    
    # Explicitly set the icon name string
    item['icon_name'] = "action-triangle-glyph"

    return item