def split_on_plus_minus(string):
    parts = string.split('-')
    if  len(parts) == 1:
        flow = parts[0]
        mods = []
    else:
        flow = parts.pop(0)
        mods = parts 
    return flow, mods