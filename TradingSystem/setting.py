

SETTINGS = {
    "font.family": "Arial",
    "font.size": 12,

    'remove_num':30
}



def get_settings(prefix: str = ""):
    prefix_length = len(prefix)
    return {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
