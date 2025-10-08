# -*- coding: utf-8 -*-
"""
Модуль для обработки изображений и распознавания текста
Использует Pytesseract для OCR распознавания математических задач с фотографий
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import logging
import tempfile
import os
from typing import Optional, Tuple
from config import OCR_LANGUAGE, OCR_CONFIG, MAX_IMAGE_SIZE

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Класс для обработки изображений и извлечения текста"""
    
    def __init__(self):
        self.ocr_config = OCR_CONFIG
        self.ocr_language = OCR_LANGUAGE
    
    def process_image(self, image_data: bytes) -> Optional[str]:
        """
        Основная функция обработки изображения
        
        Args:
            image_data: Данные изображения в байтах
            
        Returns:
            Распознанный текст или None в случае ошибки
        """
        try:
            # Проверяем размер изображения
            if len(image_data) > MAX_IMAGE_SIZE:
                logger.warning("Изображение слишком большое")
                return None
            
            # Открываем изображение
            image = Image.open(io.BytesIO(image_data))
            
            # Предварительная обработка изображения
            processed_image = self._preprocess_image(image)
            
            # Распознаем текст
            text = self._extract_text(processed_image)
            
            # Постобработка текста
            cleaned_text = self._clean_text(text)
            
            logger.info(f"Успешно распознан текст длиной {len(cleaned_text)} символов")
            return cleaned_text if cleaned_text.strip() else None
            
        except Exception as e:
            logger.error(f"Ошибка обработки изображения: {e}")
            return None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Предварительная обработка изображения для улучшения OCR
        
        Args:
            image: Исходное изображение
            
        Returns:
            Обработанное изображение
        """
        try:
            # Конвертируем в RGB если нужно
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Увеличиваем контрастность
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Увеличиваем резкость
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Конвертируем в оттенки серого
            image = image.convert('L')
            
            # Применяем фильтр для удаления шума
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Увеличиваем изображение для лучшего распознавания мелкого текста
            width, height = image.size
            if width < 1000 or height < 1000:
                scale_factor = max(1000 / width, 1000 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            logger.debug("Предварительная обработка изображения завершена")
            return image
            
        except Exception as e:
            logger.error(f"Ошибка предварительной обработки изображения: {e}")
            return image
    
    def _extract_text(self, image: Image.Image) -> str:
        """
        Извлечение текста из изображения с помощью Tesseract OCR
        
        Args:
            image: Обработанное изображение
            
        Returns:
            Распознанный текст
        """
        try:
            # Сохраняем изображение во временный файл
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                image.save(tmp_file.name, 'PNG')
                tmp_path = tmp_file.name
            
            try:
                # Попробуем несколько режимов page segmentation
                psm_modes = [6, 7, 8, 3]  # Различные режимы для разных типов текста
                best_text = ""
                best_confidence = 0
                
                for psm in psm_modes:
                    try:
                        config = f'--psm {psm} -l {self.ocr_language}'
                        
                        # Получаем текст с информацией о доверии
                        data = pytesseract.image_to_data(
                            image, 
                            config=config, 
                            output_type=pytesseract.Output.DICT
                        )
                        
                        # Вычисляем среднюю уверенность
                        confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                        if confidences:
                            avg_confidence = sum(confidences) / len(confidences)
                            
                            if avg_confidence > best_confidence:
                                best_confidence = avg_confidence
                                best_text = pytesseract.image_to_string(image, config=config)
                    
                    except Exception as e:
                        logger.debug(f"Ошибка в режиме PSM {psm}: {e}")
                        continue
                
                # Если не удалось получить хороший результат, используем базовый режим
                if not best_text.strip() or best_confidence < 30:
                    best_text = pytesseract.image_to_string(
                        image, 
                        config=f'-l {self.ocr_language}'
                    )
                
                logger.debug(f"Распознан текст с уверенностью {best_confidence}%")
                return best_text
                
            finally:
                # Удаляем временный файл
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Ошибка извлечения текста: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """
        Очистка и нормализация распознанного текста
        
        Args:
            text: Сырой текст из OCR
            
        Returns:
            Очищенный текст
        """
        if not text:
            return ""
        
        try:
            # Удаляем лишние пробелы и переносы строк
            text = ' '.join(text.split())
            
            # Исправляем распространенные ошибки OCR для математических символов
            replacements = {
                '0': '0',   # Иногда буква O распознается как цифра
                'О': '0',   # Русская О
                'о': '0',   # Русская о
                'l': '1',   # Буква l как единица
                'I': '1',   # Заглавная I как единица
                '|': '1',   # Вертикальная черта как единица
                'х': 'x',   # Русская х как переменная x
                'Х': 'X',   # Русская Х
                'у': 'y',   # Русская у как переменная y
                'а': 'a',   # Русская а
                'с': 'c',   # Русская с
                'е': 'e',   # Русская е
                'р': 'p',   # Русская р
                'п': 'p',   # Русская п тоже может быть p
                '—': '-',   # Длинное тире как минус
                '–': '-',   # Среднее тире как минус
                '×': '*',   # Знак умножения
                '÷': '/',   # Знак деления
                '∞': 'infinity',  # Бесконечность
                '≈': '≈',   # Приближенно равно
                '≠': '!=',  # Не равно
                '≤': '<=',  # Меньше или равно
                '≥': '>=',  # Больше или равно
            }
            
            for old, new in replacements.items():
                text = text.replace(old, new)
            
            # Исправляем пробелы вокруг математических операторов
            import re
            
            # Убираем пробелы перед и после основных операторов
            text = re.sub(r'\s*([+\-*/=<>!≈≠≤≥])\s*', r'\1', text)
            
            # Восстанавливаем пробелы там, где они нужны для читаемости
            text = re.sub(r'([+\-*/=<>!≈≠≤≥])', r' \1 ', text)
            
            # Очищаем множественные пробелы
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Удаляем очевидно некорректные символы
            text = re.sub(r'[^\w\s+\-*/=<>!()[\]{}.,;:πΣ∫∞≈≠≤≥αβγδθλμσφψω]', '', text)
            
            logger.debug(f"Текст после очистки: {text[:100]}...")
            return text
            
        except Exception as e:
            logger.error(f"Ошибка очистки текста: {e}")
            return text
    
    def validate_mathematical_content(self, text: str) -> bool:
        """
        Проверка, содержит ли текст математическое содержание
        
        Args:
            text: Текст для проверки
            
        Returns:
            True если текст содержит математику
        """
        if not text or len(text.strip()) < 2:
            return False
        
        # Математические индикаторы
        math_indicators = [
            # Операторы
            '+', '-', '*', '/', '=', '<', '>', '≈', '≠', '≤', '≥',
            # Функции
            'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt',
            # Переменные и константы
            'x', 'y', 'z', 'π', 'e', 'i',
            # Специальные символы
            '∫', '∑', '∞', 'dx', 'dy', 'dz',
            # Числа с десятичной точкой
            r'\d+\.\d+',
            # Степени и индексы
            '^', '_',
            # Скобки с числами/переменными
            r'\(\s*[xy\d]', r'[xy\d]\s*\)'
        ]
        
        import re
        text_lower = text.lower()
        
        # Считаем количество математических индикаторов
        math_score = 0
        for indicator in math_indicators:
            if indicator.startswith('\\') or indicator.startswith(r'\d'):
                # Это регексы
                if re.search(indicator, text_lower):
                    math_score += 1
            else:
                if indicator in text_lower:
                    math_score += 1
        
        # Также проверяем наличие цифр
        if re.search(r'\d', text):
            math_score += 1
        
        logger.debug(f"Математический рейтинг текста: {math_score}")
        return math_score >= 2  # Нужно минимум 2 математических индикатора

# Создаем глобальный экземпляр процессора изображений
image_processor = ImageProcessor()