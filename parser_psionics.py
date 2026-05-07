def enrich_psionic(item, type_map=None):
    """
    Specific parsing and enrichment for Psionics.
    Extracts costs, concentration limits, and nested submodes.
    """
    if not isinstance(item, dict): return item

    # Deep cyan theme for psionics
    item['primary_color'] = "#006064"
    item['bg_color'] = "#E0F7FA"
    item['rarity_badge'] = ""
    
    p_type = item.get('type', '')
    order = item.get('order', '')
    
    meta = "Psionic"
    if p_type == 'D': meta += " Discipline"
    elif p_type == 'T': meta += " Talent"
    if order: meta += f" ({order})"
    item['meta_left'] = meta
    
    stats = []
    if item.get('focus'):
        stats.append({'type': 'item', 'name': 'Psychic Focus', 'entry': item['focus']})
        
    if item.get('modes'):
        for mode in item['modes']:
            mode_name = mode.get('name', 'Mode')
            modifiers = []
            
            # 1. Parse Psi Cost
            cost = mode.get('cost', {})
            if cost:
                min_c = cost.get('min')
                max_c = cost.get('max')
                if min_c == max_c:
                    modifiers.append(f"{min_c} psi")
                else:
                    modifiers.append(f"{min_c}-{max_c} psi")
            
            # 2. Parse Concentration
            conc = mode.get('concentration')
            if conc:
                dur = conc.get('duration')
                unit = conc.get('unit')
                if dur and unit:
                    modifiers.append(f"conc., {dur} {unit}.")
                else:
                    modifiers.append("conc.")
            
            # Build the formatted modifier string (e.g., "(5 psi; conc., 1 hr.)")
            modifier_str = ""
            if modifiers:
                modifier_str = f" ({'; '.join(modifiers)})"
            
            # Safely grab the entries array so we can append to it if needed
            entries = mode.get('entries', [])
            if not isinstance(entries, list):
                entries = [entries]
            
            # 3. Parse Submodes (Used in disciplines like Bestial Form)
            if mode.get('submodes'):
                sub_list = {'type': 'list', 'items': []}
                for sub in mode['submodes']:
                    sub_name = sub.get('name', '')
                    sub_cost = sub.get('cost', {})
                    s_mods = []
                    
                    if sub_cost:
                        s_min = sub_cost.get('min')
                        s_max = sub_cost.get('max')
                        if s_min == s_max: 
                            s_mods.append(f"{s_min} psi")
                        else: 
                            s_mods.append(f"{s_min}-{s_max} psi")
                            
                    s_mod_str = f" ({'; '.join(s_mods)})" if s_mods else ""
                    
                    sub_list['items'].append({
                        'type': 'item', 
                        'name': f"{sub_name}{s_mod_str}", 
                        'entry': sub.get('entries', [])
                    })
                entries.append(sub_list)

            stats.append({
                'type': 'item', 
                'name': f"{mode_name}{modifier_str}", 
                'entry': entries
            })
    
    if stats:
        base_entries = item.get('entries', [])
        if not isinstance(base_entries, list):
            base_entries = [base_entries]
        
        # Append stats after the main descriptive text for Psionics
        item['entries'] = base_entries + stats
            
    return item