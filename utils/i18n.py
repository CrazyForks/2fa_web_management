from flask import session
from translations import translations

def get_translation(key):
    """获取当前语言的翻译"""
    lang = session.get('lang', 'en')
    keys = key.split('.')
    
    # 从翻译字典中获取对应的翻译
    result = translations.get(lang, translations['en'])
    for k in keys:
        result = result.get(k, k)
    
    return result
