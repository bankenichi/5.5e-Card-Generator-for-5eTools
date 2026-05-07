import copy

def enrich_skill(item, type_map=None):
    result = copy.deepcopy(item)
    ability = result.get('ability', '').upper()

    # Warm amber theme for skills
    result['primary_color'] = "#E65100"
    result['bg_color'] = "#FFF3E0"
    result['rarity_badge'] = ""

    result['meta_left'] = f"Skill ({ability})" if ability else "Skill"
    result['_data_type'] = "skill"

    return result