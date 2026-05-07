import copy
import re

RARITY_COLORS = {
    "common": ("#000000", "#F5F5F5"),      # Black
    "uncommon": ("#1B5E20", "#F1F8E9"),    # Green
    "rare": ("#0D47A1", "#E3F2FD"),        # Blue
    "very rare": ("#4A148C", "#F3E5F5"),   # Purple
    "legendary": ("#E65100", "#FFF3E0"),   # Orange
    "artifact": ("#B71C1C", "#FFEBEE")     # Red
}

RARITY_ABBR = {
    "common": "C",
    "uncommon": "U",
    "rare": "R",
    "very rare": "VR",
    "legendary": "L",
    "artifact": "A"
}

RARITY_VALUE_MAP = {
    "common": 10000,
    "uncommon": 40000,
    "rare": 400000,
    "very rare": 4000000,
    "legendary": 20000000
}

def get_source_priority(source):
    src = str(source).upper()
    priorities = {'XPHB': 1, 'XDMG': 2, 'XMM': 3, 'TCE': 20, 'XGE': 21, 'MPMM': 22}
    return priorities.get(src, 99)

def extract_bonus_name(name):
    name = name.strip()
    m = re.match(r'^\s*(\+\s*\d+)\s+(.+)$', name)
    if m: return m.group(2).strip(), m.group(1).replace(" ", "")
    m = re.match(r'^(.+?)(?:,\s*|\s+)(\+\s*\d+)\s*$', name)
    if m: return m.group(1).strip(), m.group(2).replace(" ", "")
    m = re.match(r'^(.+?)\s*\(\s*(\+\s*\d+)\s*\)$', name)
    if m: return m.group(1).strip(), m.group(2).replace(" ", "")
    m = re.search(r'^(.*?)\s*(\+\s*\d+)\s+(.*)$', name)
    if m:
        base = (m.group(1) + " " + m.group(3)).strip()
        return base, m.group(2).replace(" ", "")
    return name, None

def extract_variant_name(name):
    name = name.strip()
    
    if 'enspelled' in name.lower():
        return name, None, None
        
    base_name, bonus = extract_bonus_name(name)
    if bonus: return base_name, bonus, 'bonus'
    
    m = re.search(r'^(.*?)\s*\((Level\s*\d+|Cantrip)\)\s*$', name, re.IGNORECASE)
    if m: return m.group(1).strip(), m.group(2).capitalize(), 'level'

    prefixes = r'(acid|air|cold|earth|fire|force|lightning|necrotic|poison|psychic|radiant|thunder|water)'
    
    m = re.match(r'^\s*' + prefixes + r'\s+(.+)$', name, re.IGNORECASE)
    if m: return m.group(2).strip(), m.group(1).capitalize(), 'element'
    
    m2 = re.match(r'^(.+?)\s+of\s+' + prefixes + r'\s*(.*)$', name, re.IGNORECASE)
    if m2:
        base = f"{m2.group(1)} of {m2.group(3)}".strip()
        if base.endswith(" of"): base = base[:-3].strip()
        return base, m2.group(2).capitalize(), 'element'
        
    m3 = re.search(r'^(.*?)\s*\(' + prefixes + r'\)\s*$', name, re.IGNORECASE)
    if m3: return m3.group(1).strip(), m3.group(2).capitalize(), 'element'
        
    return name, None, None

def replace_bonus_text(entry, old_bonus, new_bonus_str):
    if isinstance(entry, str):
        return re.sub(re.escape(old_bonus) + r'(?!\d)', new_bonus_str, entry, flags=re.IGNORECASE)
    elif isinstance(entry, list):
        return [replace_bonus_text(e, old_bonus, new_bonus_str) for e in entry]
    elif isinstance(entry, dict):
        return {k: replace_bonus_text(v, old_bonus, new_bonus_str) for k, v in entry.items()}
    return entry

def entry_is_placeholder(entry):
    if isinstance(entry, str): return '#itemEntry' in entry
    if isinstance(entry, list):
        return all(entry_is_placeholder(e) for e in entry) if entry else False
    if isinstance(entry, dict):
        return entry_is_placeholder(entry.get('entries', []))
    return False

def enrich_item_data(item, base_data_list, type_map, prop_map, raw_dict):
    stats = []
    
    # We DO NOT strip '$' here, so that $C, $G, and $A map correctly to Treasures
    raw_type = str(item.get('type') or item.get('category') or '').split('|')[0].strip().upper()
    
    # --- Resolve Item Colors & Badges ---
    rarity_val = str(item.get('rarity', '')).lower()
    pc, bc = RARITY_COLORS.get(rarity_val, ("#000000", "#F5F5F5")) # Default to Common Black
    item['primary_color'] = pc
    item['bg_color'] = bc

    # Build the rarity string
    abbr = RARITY_ABBR.get(rarity_val, rarity_val.capitalize() if rarity_val not in ('none', 'unknown', 'unknown (magic)', '') else '')
    if abbr:
        item['rarity_badge'] = f'<span style="color: {pc}; font-weight: 900;">{abbr}</span>'
    else:
        item['rarity_badge'] = ''

    item['icon_name'] = None

    # --- Build Stat Blocks ---
    if item.get('ac'):
        ac_str = str(item['ac'])
        if raw_type == 'LA': ac_str += " + Dex modifier"
        elif raw_type == 'MA': ac_str += " + Dex modifier (max 2)"
        stats.append({'type': 'item', 'name': 'Armor Class', 'entry': ac_str})
    if item.get('strength'):
        stats.append({'type': 'item', 'name': 'Strength', 'entry': str(item['strength'])})
    if item.get('stealth'):
        stats.append({'type': 'item', 'name': 'Stealth', 'entry': 'Disadvantage'})
        
    if item.get('dmg1'):
        dmg_t = item.get('dmgType', '')
        dmg_map = {'B': 'Bludgeoning', 'P': 'Piercing', 'S': 'Slashing', 'N': 'Necrotic', 'R': 'Radiant', 'F': 'Fire', 'C': 'Cold', 'L': 'Lightning', 'T': 'Thunder', 'A': 'Acid', 'O': 'Force', 'Y': 'Psychic'}
        d_name = dmg_map.get(dmg_t, dmg_t)
        stats.append({'type': 'item', 'name': 'Damage', 'entry': f"{item['dmg1']} {d_name}"})
    if item.get('dmg2'):
        stats.append({'type': 'item', 'name': 'Versatile', 'entry': str(item['dmg2'])})
        
    if item.get('property'):
        prop_abbrs = []
        for p in item['property']:
            if isinstance(p, str): prop_abbrs.append(p.split('|')[0].upper())
            elif isinstance(p, dict):
                uid = p.get('uid') or p.get('name') or ''
                prop_abbrs.append(uid.split('|')[0].upper())
        
        prop_names = []
        for p in prop_abbrs:
            if not p: continue
            name = prop_map.get(p, p)
            if p in ('T', 'THROWN') and item.get('range'):
                name = f"{name} ({item['range']} ft.)"
            prop_names.append(name)
            
        if prop_names: stats.append({'type': 'item', 'name': 'Properties', 'entry': ', '.join(prop_names)})
        
    if item.get('mastery'):
        m_abbrs = []
        for m in item['mastery']:
            if isinstance(m, str): m_abbrs.append(m.split('|')[0])
            elif isinstance(m, dict):
                uid = m.get('uid') or m.get('name') or ''
                m_abbrs.append(uid.split('|')[0])
        m_abbrs = [m for m in m_abbrs if m]
        if m_abbrs: stats.append({'type': 'item', 'name': 'Mastery', 'entry': ', '.join(m_abbrs)})

    if item.get('vehAc'):
        stats.append({'type': 'item', 'name': 'Armor Class', 'entry': str(item['vehAc'])})
    if item.get('vehHp'):
        stats.append({'type': 'item', 'name': 'Hit Points', 'entry': str(item['vehHp'])})
    if item.get('vehDmgThresh'):
        stats.append({'type': 'item', 'name': 'Damage Threshold', 'entry': str(item['vehDmgThresh'])})
        
    if raw_type == 'MNT':
        if item.get('speed'):
            sp = item['speed']
            stats.append({'type': 'item', 'name': 'Speed', 'entry': f"{sp} ft." if str(sp).replace('.', '').isdigit() else str(sp)})
        if item.get('carryingCapacity'):
            cc = item['carryingCapacity']
            stats.append({'type': 'item', 'name': 'Carrying Capacity', 'entry': f"{cc} lb." if str(cc).replace('.', '').isdigit() else str(cc)})
    else:
        if item.get('vehSpeed'):
            vs = item['vehSpeed']
            stats.append({'type': 'item', 'name': 'Speed', 'entry': f"{vs} mph" if str(vs).replace('.','').isdigit() else str(vs)})
        elif item.get('speed'):
            sp = item['speed']
            stats.append({'type': 'item', 'name': 'Speed', 'entry': f"{sp} ft." if str(sp).replace('.','').isdigit() else str(sp)})
            
        if item.get('capPassenger'):
            stats.append({'type': 'item', 'name': 'Passengers', 'entry': str(item['capPassenger'])})
        if item.get('carryingCapacity'):
            cc = item['carryingCapacity']
            stats.append({'type': 'item', 'name': 'Carrying Capacity', 'entry': f"{cc} lb." if str(cc).replace('.','').isdigit() else str(cc)})
        if item.get('capCargo'):
            cc = item['capCargo']
            stats.append({'type': 'item', 'name': 'Cargo', 'entry': f"{cc} tons" if str(cc).replace('.','').isdigit() else str(cc)})

    # --- Base Inheritance Resolution ---
    inherited_entries = []
    orig_item = raw_dict.get(item.get('name', '').lower().strip(), {})
    base_item_str = str(orig_item.get('baseItem', '')).split('|')[0].lower().strip()
    
    best_base = None
    best_prio = 999
    for base in base_data_list:
        if base.get('_data_type') == 'baseitem':
            b_name = str(base.get('name', '')).lower().strip()
            
            # Prevent items from inheriting from themselves
            if item.get('name', '').lower().strip() == b_name:
                continue
                
            b_abbr = str(base.get('abbreviation', '')).upper().strip()
            if base_item_str == b_name or (raw_type and raw_type == b_abbr and len(b_abbr) > 0):
                prio = get_source_priority(base.get('source', ''))
                if prio < best_prio:
                    best_prio = prio
                    best_base = base
                    
    if best_base and 'entries' in best_base:
        inherited_entries.extend(copy.deepcopy(best_base['entries']))

    # Extrapolate fallback values from best_base
    if item.get('weight') in (None, "") and best_base: item['weight'] = best_base.get('weight')
    if item.get('value') in (None, "") and best_base: item['value'] = best_base.get('value', best_base.get('cost'))
    
    # --- Deep Property Extraction (Curse, Attunement, Wondrous, Weapon Category) ---
    req_att = item.get('reqAttune')
    if req_att is None and isinstance(item.get('inherits'), dict):
        req_att = item['inherits'].get('reqAttune')
    if req_att is None and best_base:
        req_att = best_base.get('reqAttune')
        
    is_cursed = item.get('curse', False)
    if not is_cursed and isinstance(item.get('inherits'), dict):
        is_cursed = item['inherits'].get('curse', False)
    if not is_cursed and best_base:
        is_cursed = best_base.get('curse', False)

    is_wondrous = item.get('wondrous')
    if is_wondrous is None and isinstance(item.get('inherits'), dict):
        is_wondrous = item['inherits'].get('wondrous')
    if is_wondrous is None and best_base:
        is_wondrous = best_base.get('wondrous')

    weapon_cat = item.get('weaponCategory')
    if weapon_cat is None and isinstance(item.get('inherits'), dict):
        weapon_cat = item['inherits'].get('weaponCategory')
    if weapon_cat is None and best_base:
        weapon_cat = best_base.get('weaponCategory')

    is_staff = item.get('staff')
    if is_staff is None and isinstance(item.get('inherits'), dict):
        is_staff = item['inherits'].get('staff')
    if is_staff is None and best_base:
        is_staff = best_base.get('staff')

    is_wand = item.get('wand')
    if is_wand is None and isinstance(item.get('inherits'), dict):
        is_wand = item['inherits'].get('wand')
    if is_wand is None and best_base:
        is_wand = best_base.get('wand')

    is_rod = item.get('rod')
    if is_rod is None and isinstance(item.get('inherits'), dict):
        is_rod = item['inherits'].get('rod')
    if is_rod is None and best_base:
        is_rod = best_base.get('rod')

    specific_attune = ""
    if req_att:
        if isinstance(req_att, str) and str(req_att).lower() not in ('true', 'false', '1', '0', 'yes', 'no', ''):
            specific_attune = f"Requires Attunement {req_att}"
        else:
            specific_attune = "Requires Attunement"
            
    item['custom_footer_left'] = specific_attune
    item['custom_footer_right'] = "Cursed" if is_cursed else ""

    # --- ADVANCED META TYPE RESOLVER ---
    actual_type = raw_type
    if actual_type in ('GV', 'VARIES', '') and best_base:
        actual_type = str(best_base.get('type', '')).split('|')[0].strip().upper()

    ts = type_map.get(actual_type, actual_type) if actual_type else ""

    if ts == "Generic Variant" or actual_type == "GV":
        if is_wondrous: ts = "Wondrous Item"
        elif actual_type == 'M': ts = "Melee Weapon"
        elif actual_type == 'R': ts = "Ranged Weapon"

    if is_wondrous and (not ts or ts in ('Adventuring Gear', 'Other', 'Generic Variant', 'Item')):
        ts = "Wondrous Item"

    if weapon_cat:
        wc_str = str(weapon_cat).title()
        if "Weapon" in ts:
            if wc_str not in ts:
                ts = ts.replace("Weapon", f"{wc_str} Weapon")
        elif not ts or ts in ("Item", "Generic Variant", "GV"):
            if actual_type == 'M': ts = f"Melee {wc_str} Weapon"
            elif actual_type == 'R': ts = f"Ranged {wc_str} Weapon"
            else: ts = f"{wc_str} Weapon"

    is_focus = item.get('scfType') is not None or bool(item.get('focus')) or (best_base and bool(best_base.get('focus')))
    if is_focus and "Focus" not in ts:
        if ts and ts != "Spellcasting Focus": 
            ts += " (Spellcasting Focus)"
        else: 
            ts = "Spellcasting Focus"

    if is_staff:
        if ts == 'Spellcasting Focus': ts = 'Staff'
        elif ts == 'Melee Simple Weapon': ts = 'Melee Simple Weapon (Staff)'
        elif ts and 'Staff' not in ts: ts = f"{ts} (Staff)"
        
    if is_wand:
        if ts == 'Spellcasting Focus': ts = 'Wand'
        elif ts and 'Wand' not in ts: ts = f"{ts} (Wand)"
        
    if is_rod:
        if ts == 'Spellcasting Focus': ts = 'Rod'
        elif ts and 'Rod' not in ts: ts = f"{ts} (Rod)"

    if actual_type == 'RG': ts = 'Ring'
    if actual_type == 'P': ts = 'Potion'
    if actual_type == 'SC': ts = 'Scroll'
    if actual_type == 'RD': ts = 'Rod'
    if actual_type == 'WD': ts = 'Wand'
            
    if not ts:
        ts = "Item"

    item['meta_left'] = ts

    # --- Value Fallback Calculation ---
    value = item.get('value')
    if value in (None, "") and rarity_val in RARITY_VALUE_MAP:
        base_val = RARITY_VALUE_MAP[rarity_val]
        is_consumable = item.get('consumable', False)
        if raw_type in ['P', 'A', 'EXP', 'FD']: 
            is_consumable = True
        if is_consumable and raw_type != 'SC':
            value = base_val // 2
        else:
            value = base_val
        item['value'] = value

    # --- Extended Inheritance (ItemType & Added Entries) ---
    best_type = None
    best_type_prio = 999
    for t in base_data_list:
        if t.get('_data_type') == 'itemType' and str(t.get('abbreviation', '')).upper().strip() == raw_type:
            prio = get_source_priority(t.get('source', ''))
            if prio < best_type_prio:
                best_type_prio = prio
                best_type = t
    if best_type:
        resolved_type = best_type
        for _ in range(5): 
            if 'entries' in resolved_type:
                break
            copy_ref = resolved_type.get('_copy')
            if not isinstance(copy_ref, dict):
                break
            ref_abbr = copy_ref.get('abbreviation', '').upper().strip()
            ref_src  = copy_ref.get('source', '').lower().strip()
            target = None
            for t in base_data_list:
                if (t.get('_data_type') == 'itemType'
                        and str(t.get('abbreviation', '')).upper().strip() == ref_abbr
                        and (not ref_src or str(t.get('source', '')).lower().strip() == ref_src)):
                    target = t
                    break
            if target is None:
                break
            resolved_type = target
        if 'entries' in resolved_type:
            inherited_entries.extend(copy.deepcopy(resolved_type['entries']))
        
    best_add = None
    best_add_prio = 999
    for t in base_data_list:
        if t.get('_data_type') == 'itemTypeAdditionalEntries':
            applies = str(t.get('appliesTo', '')).upper().split('|')[0].strip()
            if applies == raw_type:
                prio = get_source_priority(t.get('source', ''))
                if prio < best_add_prio:
                    best_add_prio = prio
                    best_add = t
    if best_add and 'entries' in best_add:
        inherited_entries.extend(copy.deepcopy(best_add['entries']))

    final_entries = stats
    if not item.get('entries') or entry_is_placeholder(item.get('entries', [])):
        final_entries.extend(inherited_entries)
    else:
        final_entries.extend(inherited_entries)
        final_entries.extend(item['entries'])
            
    item['entries'] = final_entries
    return item