import re


def preprocess_math_text(text):
    """Предварительная обработка математического текста"""
    if not text:
        return ""

    # Основные замены
    replacements = {
        '^': '**',
        '×': '*',
        '÷': '/',
        '–': '-',
        '—': '-',
        'π': 'pi',
        '∞': 'oo',
        '√': 'sqrt',
        '²': '**2',
        '³': '**3'
    }

    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    # Добавляем * между цифрами и переменными
    cleaned = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', cleaned)
    cleaned = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', cleaned)

    # Убираем лишние пробелы вокруг операторов
    cleaned = re.sub(r'\s*([+\-*/=()])\s*', r'\1', cleaned)

    return cleaned.strip()