def enrich_background(item, type_map=None):
    """
    Specific parsing and enrichment for Backgrounds.
    """
    if not isinstance(item, dict): return item

    meta = "Background"
    pc = "#455A64"  # Blue Grey
    bc = "#ECEFF1"

    # Apply theme and meta tags
    item['primary_color'] = pc
    item['bg_color'] = bc
    item['rarity_badge'] = ""
    item['meta_left'] = meta

    stats = []

    skill_profs = item.get('skillProficiencies', [])
    if skill_profs:
        profs = []
        for sp in skill_profs:
            if isinstance(sp, dict):
                for k in sp.keys():
                    if k != 'choose':
                        profs.append(k.title())
                if 'choose' in sp:
                    profs.append("Choose")
        if profs:
            stats.append({'type': 'item', 'name': 'Skill Proficiencies', 'entry': ", ".join(profs)})

    if stats:
        entries = item.get('entries', [])
        if not isinstance(entries, list):
            entries = [entries]
        item['entries'] = stats + entries

    return item