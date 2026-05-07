BASTION_COLORS = {
    5: ("#1B5E20", "#F1F8E9"),    # Level 5: Uncommon (Green)
    9: ("#0D47A1", "#E3F2FD"),    # Level 9: Rare (Blue)
    13: ("#4A148C", "#F3E5F5"),   # Level 13: Very Rare (Purple)
    17: ("#E65100", "#FFF3E0")    # Level 17: Legendary (Orange)
}

def enrich_bastion(item, type_map=None):
    """
    Specific parsing and enrichment for Bastions / Facilities.
    Extracts level, space, hirelings, orders, and assigns color based on facility level.
    """
    stats = []
    
    # 1. Handle Colors based on Level
    lvl = item.get('level')
    color_lvl = 5
    if lvl:
        lvl_int = int(lvl)
        if lvl_int >= 17: color_lvl = 17
        elif lvl_int >= 13: color_lvl = 13
        elif lvl_int >= 9: color_lvl = 9
        
    pc, bc = BASTION_COLORS.get(color_lvl, ("#1B5E20", "#F1F8E9"))
    item['primary_color'] = pc
    item['bg_color'] = bc

    # 2. Set Meta Details
    fac_type = str(item.get('category', '')).title()
    fac_str = f"{fac_type} Facility" if fac_type else "Facility"
    item['meta_left'] = f"Level {lvl} {fac_str}" if lvl else fac_str
    item['rarity_badge'] = "" # Bastions don't use the top-right rarity letter

    # 3. Parse specific Bastion stats for the card body
    if item.get('prerequisite'):
        prereqs = []
        for p in item['prerequisite']:
            if 'membership' in p: prereqs.append(f"Membership ({', '.join(p['membership']).title()})")
            if 'spellcastingFocus' in p: prereqs.append("Spellcasting Focus")
            if 'expertise' in p: prereqs.append("Expertise")
            if 'otherSummary' in p: prereqs.append(p['otherSummary'].get('entrySummary', 'Special'))
        if prereqs:
            stats.append({'type': 'item', 'name': 'Prerequisite', 'entry': ', '.join(prereqs)})

    if item.get('space'):
        stats.append({'type': 'item', 'name': 'Space', 'entry': ', '.join(item['space']).title()})
        
    if item.get('hirelings'):
        h_count = sum(h.get('exact', h.get('min', 0)) for h in item['hirelings'])
        stats.append({'type': 'item', 'name': 'Hirelings', 'entry': str(h_count)})

    if item.get('orders'):
        stats.append({'type': 'item', 'name': 'Orders', 'entry': ', '.join(item['orders']).title()})

    if stats:
        if not item.get('entries'):
            item['entries'] = stats
        else:
            item['entries'] = stats + item['entries']

    return item