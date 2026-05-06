def enrich_race(item, type_map=None):
    """
    Specific parsing and enrichment for Races, Subraces, and Lineages.
    """
    if not isinstance(item, dict): return item

    # Teal/Nature theme for Races
    item['primary_color'] = "#004D40"
    item['bg_color'] = "#E0F2F1"
    item['icon_name'] = "bestiary"
    item['rarity_badge'] = ""
    
    # Determine Race Type
    r_type = "Race"
    if item.get('_data_type') == 'subrace':
        r_type = "Subrace"
    elif item.get('lineage'):
        r_type = "Lineage"
    item['meta_left'] = r_type
    
    stats = []
    
    # Parse Size safely
    if isinstance(item.get('size'), list):
        size_map = {"T": "Tiny", "S": "Small", "M": "Medium", "L": "Large", "H": "Huge", "G": "Gargantuan"}
        sizes = [size_map.get(s, s) for s in item['size'] if isinstance(s, str)]
        if sizes:
            stats.append({'type': 'item', 'name': 'Size', 'entry': " or ".join(sizes)})
    elif isinstance(item.get('size'), str):
        size_map = {"T": "Tiny", "S": "Small", "M": "Medium", "L": "Large", "H": "Huge", "G": "Gargantuan"}
        stats.append({'type': 'item', 'name': 'Size', 'entry': size_map.get(item['size'], item['size'])})
            
    # Parse Speed safely
    sp = item.get('speed')
    if isinstance(sp, int):
        stats.append({'type': 'item', 'name': 'Speed', 'entry': f"{sp} ft."})
    elif isinstance(sp, dict):
        sp_strs = []
        for k, v in sp.items():
            if isinstance(v, int):
                sp_strs.append(f"{k} {v} ft.")
            elif isinstance(v, bool) and v:
                sp_strs.append(f"{k} equal to walking speed")
            elif isinstance(v, dict):
                sp_strs.append(f"{k} {v.get('number', 0)} ft.")
        if sp_strs:
            stats.append({'type': 'item', 'name': 'Speed', 'entry': ", ".join(sp_strs).title()})
                
    # Parse Darkvision
    if item.get('darkvision'):
        stats.append({'type': 'item', 'name': 'Darkvision', 'entry': f"{item['darkvision']} ft."})
        
    if stats:
        entries = item.get('entries', [])
        if not isinstance(entries, list):
            entries = [entries]
        item['entries'] = stats + entries
            
    return item