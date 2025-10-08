"""
Гибридный модуль для обработки изображений
Использует Tesseract как основной метод, OpenAI Vision как fallback
"""

import pytesseract
from PIL import Image, ImageEnhance
import io
import logging
import base64
import re
from typing import Optional
from openai import OpenAI
from config import OCR_LANGUAGE, OCR_CONFIG, MAX_IMAGE_SIZE, OPENAI_API_KEY

logger = logging.getLogger(__name__)

class HybridImageProcessor:
    """Гибридный процессор изображений с Tesseract + OpenAI fallback"""

    def __init__(self):
        self.ocr_config = OCR_CONFIG
        self.ocr_language = OCR_LANGUAGE
        self.openai_client = None
        self._initialize_services()

    def _initialize_services(self):
        """Инициализация сервисов распознавания"""
        # Проверяем Tesseract
        try:
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
            logger.info("✅ Tesseract OCR доступен")
        except Exception as e:
            self.tesseract_available = False
            logger.warning(f"❌ Tesseract недоступен: {e}")

        # Проверяем OpenAI
        if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY":
            try:
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
                self.openai_available = True
                logger.info("✅ OpenAI Vision доступен")
            except Exception as e:
                self.openai_available = False
                logger.error(f"❌ OpenAI ошибка: {e}")
        else:
            self.openai_available = False
            logger.warning("❌ OpenAI API ключ не установлен")

    def process_image(self, image_data: bytes) -> Optional[str]:
        """Гибридное распознавание изображения"""
        try:
            if len(image_data) > MAX_IMAGE_SIZE:
                logger.warning("Изображение слишком большое")
                return None

            image = Image.open(io.BytesIO(image_data))

            # Шаг 1: Пробуем Tesseract
            if self.tesseract_available:
                logger.info("🔍 Пробуем распознать через Tesseract...")
                processed_image = self._preprocess_image(image)
                tesseract_text = self._extract_text_tesseract(processed_image)

                if self._is_good_quality_text(tesseract_text):
                    logger.info("✅ Tesseract распознал хорошо")
                    cleaned_text = self._clean_text(tesseract_text)
                    return cleaned_text
                else:
                    logger.warning("❌ Tesseract распознал плохо")

            # Шаг 2: Fallback на OpenAI Vision
            if self.openai_available:
                logger.info("🔍 Пробуем распознать через OpenAI Vision...")
                openai_text = self._extract_text_openai_vision(image_data)

                if openai_text and self._is_good_quality_text(openai_text):
                    logger.info("✅ OpenAI Vision распознал хорошо")
                    cleaned_text = self._clean_text(openai_text)
                    return cleaned_text
                else:
                    logger.warning("❌ OpenAI Vision не смог распознать")

            logger.error("❌ Все методы распознавания не сработали")
            return None

        except Exception as e:
            logger.error(f"❌ Ошибка обработки изображения: {e}")
            return None

    def _is_good_quality_text(self, text: str) -> bool:
        """Проверяет качество распознанного текста"""
        if not text or len(text.strip()) < 5:
            return False

        # Просто проверяем, что есть хоть какая-то математика
        math_indicators = ['+', '-', '*', '/', '=', 'x', 'y', '(', ')', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        return any(indicator in text for indicator in math_indicators)

    def _extract_text_tesseract(self, image: Image.Image) -> str:
        """Распознавание через Tesseract"""
        try:
            # Пробуем разные конфигурации
            configs = [
                '--psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/=()[]{}<>,.π∞∫∑ ',
                '--psm 8',
                '--psm 11',
                '--psm 13'
            ]

            for config in configs:
                try:
                    text = pytesseract.image_to_string(image, lang='rus+eng', config=config)
                    if text and len(text.strip()) > 5:
                        return text
                except:
                    continue

            # Базовое распознавание
            return pytesseract.image_to_string(image, lang='rus+eng')

        except Exception as e:
            logger.error(f"Ошибка Tesseract: {e}")
            return ""

    def _extract_text_openai_vision(self, image_data: bytes) -> Optional[str]:
        """Распознавание через OpenAI Vision"""
        if not self.openai_client:
            return None

        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "РАСПОЗНАЙ МАТЕМАТИЧЕСКУЮ ЗАДАЧУ. Верни ТОЛЬКО текст задачи без пояснений."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )

            extracted_text = response.choices[0].message.content
            if extracted_text:
                # Очищаем ответ
                lines = extracted_text.split('\n')
                clean_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith(('Примечание', 'Задача', 'Комментарий')):
                        clean_lines.append(line)

                return ' '.join(clean_lines[:3])

            return None

        except Exception as e:
            logger.error(f"Ошибка OpenAI Vision: {e}")
            return None

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Улучшенная предобработка для математических формул"""
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Увеличиваем размер
            width, height = image.size
            if max(width, height) < 1500:
                scale_factor = 1500 / max(width, height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Увеличиваем контраст и резкость
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(3.0)

            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(3.0)

            # Конвертируем в grayscale и бинаризуем
            image = image.convert('L')
            image = image.point(lambda x: 0 if x < 200 else 255)

            return image

        except Exception as e:
            logger.error(f"Ошибка предобработки: {e}")
            return image

    def _clean_text(self, text: str) -> str:
        """Очистка распознанного текста"""
        if not text:
            return ""

        try:
            # Заменяем ошибки OCR
            replacements = {
                '0': '0', 'О': '0', 'о': '0',
                '1': '1', 'l': '1', 'I': '1', '|': '1',
                'х': 'x', 'Х': 'X', 'у': 'y',
                'а': 'a', 'с': 'c', 'е': 'e',
                '—': '-', '–': '-', '×': '*', '÷': '/',
                '∞': 'inf', 'π': 'pi', '∫': 'integral',
                'з': '3', 'ч': '4', 'б': '6'
            }

            for wrong, correct in replacements.items():
                text = text.replace(wrong, correct)

            # Убираем лишние пробелы
            text = re.sub(r'\s+', ' ', text).strip()
            text = re.sub(r'\s*([+\-*/=])\s*', r' \1 ', text)

            return text

        except Exception as e:
            logger.error(f"Ошибка очистки текста: {e}")
            return text

    def validate_mathematical_content(self, text: str) -> bool:
        """Проверяет математическое содержание"""
        if not text or len(text.strip()) < 5:
            return False

        math_indicators = [
            '+', '-', '*', '/', '=', '<', '>', '≈', '≠', '≤', '≥',
            'решить', 'найти', 'вычислить', 'упростить',
            'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt',
            'x', 'y', 'z', 'π', 'e', 'i',
            '∫', '∑', '∞', 'dx', 'dy', 'dz'
        ]

        text_lower = text.lower()
        math_score = 0

        for indicator in math_indicators:
            if indicator in text_lower:
                math_score += 1
        
        logger.debug(f"Математический рейтинг: {math_score}")
        return math_score >= 2

# Создаем глобальный экземпляр процессора
image_processor = HybridImageProcessor()