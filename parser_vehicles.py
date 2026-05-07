def enrich_vehicle(item, type_map=None):
    """
    Specific parsing and enrichment for Vehicles and Vehicle Upgrades.
    Extracts traits, action stations, immunities, and complex stat blocks.
    """
    if not isinstance(item, dict): return item
    
    # Steel/Iron theme
    item['primary_color'] = "#37474F" 
    item['bg_color'] = "#ECEFF1"
    item['rarity_badge'] = ""
    
    v_type = str(item.get('vehicleType', 'Vehicle')).replace('_', ' ').title()
    if item.get('_data_type') == 'vehicleUpgrade':
        v_type += " Upgrade"
    item['meta_left'] = v_type
    
    stats = []
    
    # Size & Dimensions
    if item.get('size'):
        size_map = {"T": "Tiny", "S": "Small", "M": "Medium", "L": "Large", "H": "Huge", "G": "Gargantuan"}
        size_val = item['size'][0] if isinstance(item['size'], list) else item['size']
        stats.append({'type': 'item', 'name': 'Size', 'entry': size_map.get(size_val, size_val)})
        
    if item.get('dimensions'):
        stats.append({'type': 'item', 'name': 'Dimensions', 'entry': " by ".join(item['dimensions'])})
        
    if item.get('terrain'):
        stats.append({'type': 'item', 'name': 'Terrain', 'entry': ", ".join(item['terrain']).title()})
        
    # Capacities
    capacities = []
    if item.get('capCrew'): capacities.append(f"Crew: {item['capCrew']}")
    if item.get('capPassenger'): capacities.append(f"Passengers: {item['capPassenger']}")
    if item.get('capCreature'): capacities.append(f"Creatures: {item['capCreature']}")
    if item.get('capCargo'): capacities.append(f"Cargo: {item['capCargo']}")
    if capacities:
        stats.append({'type': 'item', 'name': 'Capacity', 'entry': ", ".join(capacities)})

    # Armor Class
    ac = None
    if item.get('ac'):
        ac = item['ac']
        if isinstance(ac, list):
            ac = ac[0].get('ac', ac[0]) if isinstance(ac[0], dict) else ac[0]
    elif item.get('hull') and item['hull'].get('ac'):
        ac = item['hull']['ac']
    
    if ac is not None:
        stats.append({'type': 'item', 'name': 'Armor Class', 'entry': str(ac)})

    # Hit Points & Thresholds
    hp_str = ""
    hp_data = item.get('hp') or item.get('hull', {})
    if hp_data:
        if isinstance(hp_data, dict):
            hp_val = hp_data.get('hp', hp_data.get('average', '--'))
            dt = hp_data.get('dt')
            mt = hp_data.get('mt')
            extras = []
            if dt: extras.append(f"damage threshold {dt}")
            if mt: extras.append(f"mishap threshold {mt}")
            if extras:
                hp_str = f"{hp_val} ({', '.join(extras)})"
            else:
                hp_str = str(hp_val)
        else:
            hp_str = str(hp_data)
        
        if hp_str and hp_str != "{}":
            stats.append({'type': 'item', 'name': 'Hit Points', 'entry': hp_str})

    # Pace & Speed
    speed_data = item.get('speed')
    speed_val = 0
    speed_str = ""
    if isinstance(speed_data, int):
        speed_val = speed_data
        speed_str = f"{speed_val} ft."
    elif isinstance(speed_data, dict):
        sp_strs = []
        for k, v in speed_data.items():
            if k == 'canHover': continue
            if isinstance(v, int):
                sp_strs.append(f"{k} {v} ft.")
                if speed_val == 0: speed_val = v
            elif isinstance(v, bool) and v:
                sp_strs.append(f"{k} equal to walking speed")
            elif isinstance(v, dict):
                num = v.get('number', 0)
                cond = v.get('condition', '')
                sp_strs.append(f"{k} {num} ft. {cond}".strip())
                if speed_val == 0: speed_val = num
        speed_str = ", ".join(sp_strs).title()
    
    if speed_str:
        mph = item.get('pace')
        if isinstance(mph, dict):
            val = list(mph.values())[0]
            if isinstance(val, (int, float)):
                mph = val
            elif isinstance(val, str):
                if '½' in val: mph = float(val.replace('½', '.5'))
                else:
                    try: mph = float(val)
                    except: mph = 0
                    
        if not mph and speed_val > 0:
            mph = speed_val / 10
            if isinstance(mph, float) and mph.is_integer():
                mph = int(mph)
                
        if mph:
            try:
                mph_float = float(mph)
                mpd = int(mph_float * 24)
                mph_disp = str(int(mph_float)) if mph_float.is_integer() else str(mph_float)
                pace_str = f"[Travel Pace {mph_disp} miles per hour ({mpd} miles per day)]"
                stats.append({'type': 'item', 'name': 'Speed', 'entry': [speed_str, pace_str]})
            except:
                stats.append({'type': 'item', 'name': 'Speed', 'entry': speed_str})
        else:
            stats.append({'type': 'item', 'name': 'Speed', 'entry': speed_str})

    # Ability Scores
    has_stats = any(k in item for k in ['str', 'dex', 'con', 'int', 'wis', 'cha'])
    if has_stats:
        def get_modifier(score):
            mod = (score - 10) // 2
            return f"+{mod}" if mod >= 0 else str(mod)

        s_str = item.get('str', 0)
        s_dex = item.get('dex', 0)
        s_con = item.get('con', 0)
        s_int = item.get('int', 0)
        s_wis = item.get('wis', 0)
        s_cha = item.get('cha', 0)
        
        stats.append({
            'type': 'table',
            'colLabels': ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'],
            'colStyles': [
                'col-2 text-center', 'col-2 text-center', 'col-2 text-center',
                'col-2 text-center', 'col-2 text-center', 'col-2 text-center'
            ],
            'rows': [
                [
                    f"{s_str} ({get_modifier(s_str)})",
                    f"{s_dex} ({get_modifier(s_dex)})",
                    f"{s_con} ({get_modifier(s_con)})",
                    f"{s_int} ({get_modifier(s_int)})",
                    f"{s_wis} ({get_modifier(s_wis)})",
                    f"{s_cha} ({get_modifier(s_cha)})"
                ]
            ]
        })

    # Immunities
    if item.get('immune'):
        stats.append({'type': 'item', 'name': 'Damage Immunities', 'entry': ", ".join(item['immune']).title()})
    if item.get('conditionImmune'):
        stats.append({'type': 'item', 'name': 'Condition Immunities', 'entry': ", ".join(item['conditionImmune']).title()})

    # --- Complex Sub-blocks (Traits, Weapons, Action Stations) ---
    components_to_add = []
    
    def parse_component_list(comp_list, title):
        if not comp_list: return []
        res = [{'type': 'nested_header', 'name': title}]
        for comp in comp_list:
            if isinstance(comp, str):
                res.append(comp)
            elif isinstance(comp, dict):
                name = comp.get('name', '').strip()
                while name.endswith(':'): name = name[:-1].strip()
                
                # Check for weapon/station counts
                count_val = comp.get('count')
                if count_val:
                    name = f"{name} ({count_val})"
                    
                c_entries = list(comp.get('entries', []))
                
                # Pull nested actions up into the entries flow
                if comp.get('action'):
                    c_entries.extend(comp['action'])
                
                # Movement elements tuck their descriptive strings into the 'speed' object
                if comp.get('speed') and isinstance(comp['speed'], list):
                    for sp in comp['speed']:
                        if isinstance(sp, dict) and 'entries' in sp:
                            c_entries.extend(sp['entries'])
                            
                c_ac = comp.get('ac')
                c_hp = comp.get('hp')
                c_hp_note = comp.get('hpNote', '')
                
                # Render components with HP/AC as distinct layout blocks
                if c_ac or c_hp:
                    if name:
                        res.append(f'<strong class="card-strong">{name}</strong>')
                    if c_ac:
                        res.append(f'<strong class="card-strong">Armor Class:</strong> {c_ac}')
                    if c_hp:
                        hp_str = f'<strong class="card-strong">Hit Points:</strong> {c_hp}'
                        if c_hp_note: hp_str += f" {c_hp_note}"
                        res.append(hp_str)
                    
                    # Unpack each text node as an independent entry so the engine can split them
                    for r in c_entries:
                        res.append(r)
                else:
                    # Render standard components as inline bold elements, unpacked for the splitter
                    if not c_entries:
                        if name:
                            res.append(f'<strong class="card-strong">{name}:</strong>')
                        continue
                        
                    first = c_entries[0]
                    rest = c_entries[1:]
                    
                    if isinstance(first, str):
                        name_str = f'<strong class="card-strong">{name}:</strong> ' if name else ''
                        res.append(f"{name_str}{first}")
                    else:
                        if name:
                            res.append(f'<strong class="card-strong">{name}:</strong>')
                        res.append(first)
                        
                    for r in rest:
                        res.append(r)
        return res

    if item.get('trait'): components_to_add.extend(parse_component_list(item['trait'], "Traits"))
    if item.get('control'): components_to_add.extend(parse_component_list(item['control'], "Control"))
    if item.get('movement'): components_to_add.extend(parse_component_list(item['movement'], "Movement Components"))
    if item.get('weapon'): components_to_add.extend(parse_component_list(item['weapon'], "Weapons"))
    if item.get('station'): components_to_add.extend(parse_component_list(item['station'], "Stations"))
    if item.get('actionStation'): components_to_add.extend(parse_component_list(item['actionStation'], "Action Stations"))
    
    # Standard Actions
    if item.get('action'):
        act_list = item['action']
        if isinstance(act_list, list) and len(act_list) > 0 and isinstance(act_list[0], str):
            components_to_add.append({'type': 'nested_header', 'name': 'Actions'})
            components_to_add.extend(act_list)
        else:
            components_to_add.extend(parse_component_list(act_list, "Actions"))
            
    if item.get('reaction'): components_to_add.extend(parse_component_list(item['reaction'], "Reactions"))

    # Consolidate all entries
    entries = []
    if stats:
        entries.extend(stats)
        
    original_entries = item.get('entries', [])
    if not isinstance(original_entries, list):
        original_entries = [original_entries]
    entries.extend(original_entries)
    
    entries.extend(components_to_add)
    
    item['entries'] = entries
    
    return item