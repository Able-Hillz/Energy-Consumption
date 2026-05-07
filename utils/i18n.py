translations = {
    'en': {
        'welcome': 'Welcome',
        'consumption': 'Energy Consumption'
    },
    'bem': {  # Bemba
        'welcome': 'Mwaiseni',
        'consumption': 'Ukusebenzisa Amandla'
    },
    'ny': {   # Nyanja
        'welcome': 'Takulandilani',
        'consumption': 'Kugwiritsa Mphamvu'
    }
}

def translate(key, language='en'):
    return translations.get(language, {}).get(key, key)