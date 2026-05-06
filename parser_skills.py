import copy

def enrich_skill(item, type_map=None):
    result = copy.deepcopy(item)
    ability = result.get('ability', '').upper()
    
    result['meta_left'] = f"Skill ({ability})" if ability else "Skill"
    result['_data_type'] = "skill"
    
    return result