import os
import subprocess
import sys


def setup_tesseract():
    """Автоматическая настройка Tesseract для Windows"""

    # Возможные пути установки Tesseract
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME'))
    ]

    print("🔍 Ищем Tesseract...")

    tesseract_path = None
    for path in possible_paths:
        if os.path.exists(path):
            tesseract_path = path
            print(f"✅ Найден Tesseract: {path}")
            break

    if not tesseract_path:
        print("❌ Tesseract не найден!")
        return False

    # Настраиваем pytesseract
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print("✅ pytesseract настроен")

        # Проверяем работу
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract версия: {version}")

        return True

    except Exception as e:
        print(f"❌ Ошибка настройки: {e}")
        return False


def test_tesseract():
    """Тест работы Tesseract"""
    try:
        import pytesseract
        from PIL import Image, ImageDraw, ImageFont

        # Создаем тестовое изображение
        img = Image.new('RGB', (400, 100), color='white')
        d = ImageDraw.Draw(img)

        # Пробуем разные шрифты
        fonts_to_try = [
            "arial.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            None  # Использовать default
        ]

        font = None
        for font_path in fonts_to_try:
            try:
                if font_path and os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 24)
                    break
                elif font_path is None:
                    font = ImageFont.load_default()
                    break
            except:
                continue

        d.text((10, 10), "2x + 5 = 13", fill='black', font=font)

        # Распознаем текст
        text = pytesseract.image_to_string(img, lang='rus+eng')
        print(f"✅ Тест распознавания: '{text.strip()}'")

        return True

    except Exception as e:
        print(f"❌ Тест не пройден: {e}")
        return False


if __name__ == "__main__":
    print("🛠 Настройка Tesseract OCR\n")

    if setup_tesseract():
        print("\n🧪 Запускаем тест...")
        test_tesseract()
    else:
        print("\n⚠️ Установите Tesseract вручную")