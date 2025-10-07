import pytesseract
import logging
from PIL import Image, ImageEnhance, ImageFilter
import io
import re
import os

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self):
        logger.info("Инициализация ImageProcessor...")

        # Проверяем наличие Tesseract
        try:
            # Для Windows путь может быть другим
            if os.name == 'nt':  # Windows
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            # Проверяем что tesseract работает
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract версия: {version}")

        except Exception as e:
            logger.error(f"Tesseract не найден: {e}")
            logger.warning("OCR будет работать в ограниченном режиме")

    def process_image(self, image_data):
        """Обработка изображения"""
        try:
            logger.debug("Начало обработки изображения")

            # Открываем изображение
            image = Image.open(io.BytesIO(image_data))
            logger.debug(f"Размер изображения: {image.size}")

            # Улучшаем качество
            image = self.enhance_image(image)

            # Простая обработка без сложных настроек
            try:
                text = pytesseract.image_to_string(image, lang='rus+eng')
            except:
                # Если не работает с русским, пробуем английский
                text = pytesseract.image_to_string(image, lang='eng')

            if text:
                cleaned_text = self.clean_text(text)
                logger.info(f"Распознанный текст: {cleaned_text}")
                return cleaned_text
            else:
                logger.warning("Текст не распознан")
                return None

        except Exception as e:
            logger.error(f"Ошибка обработки изображения: {e}", exc_info=True)
            return None

    def enhance_image(self, image):
        """Улучшение изображения"""
        try:
            # Конвертируем в grayscale
            if image.mode != 'L':
                image = image.convert('L')

            # Увеличиваем контраст
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)

            # Легкое увеличение резкости
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)

            return image

        except Exception as e:
            logger.error(f"Ошибка улучшения изображения: {e}")
            return image

    def clean_text(self, text):
        """Очистка текста"""
        if not text:
            return ""

        # Убираем лишние пробелы
        text = ' '.join(text.split())

        # Простые замены
        replacements = {
            'О': '0', 'о': '0',
            '|': '1', 'I': '1',
            'х': 'x', 'у': 'y',
            '—': '-', '–': '-',
            '×': '*', '÷': '/'
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text.strip()

    def is_mathematical(self, text):
        """Простая проверка на математику"""
        if not text or len(text) < 2:
            return False

        # Простые признаки
        math_signs = ['+', '-', '*', '/', '=', 'x', 'y', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        return any(sign in text for sign in math_signs)


# Глобальный экземпляр
image_processor = ImageProcessor()