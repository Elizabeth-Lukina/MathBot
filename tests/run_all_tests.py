"""
Запуск всех тестов
"""

import sys
import os
import importlib
import time

# Добавляем путь к корневой директории проекта
sys.path.append('..')

def run_test_module(module_name, display_name):
    """Запуск одного тестового модуля"""
    print(f"\n{'='*50}")
    print(f"🧪 {display_name}")
    print(f"{'='*50}")

    try:
        # Импортируем и запускаем тестовый модуль
        module = importlib.import_module(f'tests.{module_name}')

        if hasattr(module, 'test_arithmetic'):
            module.test_arithmetic()
        elif hasattr(module, 'test_equations'):
            module.test_equations()
        elif hasattr(module, 'test_derivatives'):
            module.test_derivatives()
        elif hasattr(module, 'test_integrals'):
            module.test_integrals()
        elif hasattr(module, 'test_trigonometry'):
            module.test_trigonometry()
        elif hasattr(module, 'test_algebra'):
            module.test_algebra()
        else:
            print(f"❌ В модуле {module_name} не найдена тестовая функция")

        return True

    except Exception as e:
        print(f"❌ Ошибка при запуске {module_name}: {e}")
        return False

def run_performance_test():
    """Запуск теста производительности"""
    print(f"\n{'='*50}")
    print("⚡ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print(f"{'='*50}")

    try:
        from tests.test_performance import performance_test
        performance_test()
        return True
    except Exception as e:
        print(f"❌ Ошибка при запуске теста производительности: {e}")
        return False

def run_all_tests():
    """Запуск всех тестовых наборов"""
    print("🚀 ЗАПУСК ВСЕХ ТЕСТОВ")
    print("=" * 60)

    # Список тестовых модулей
    test_modules = [
        ('test_arithmetic', 'ТЕСТЫ АРИФМЕТИКИ'),
        ('test_equations', 'ТЕСТЫ УРАВНЕНИЙ'),
        ('test_derivatives', 'ТЕСТЫ ПРОИЗВОДНЫХ'),
        ('test_integrals', 'ТЕСТЫ ИНТЕГРАЛОВ'),
        ('test_trigonometry', 'ТЕСТЫ ТРИГОНОМЕТРИИ'),
        ('test_algebra', 'ТЕСТЫ АЛГЕБРЫ'),
    ]

    results = {
        'passed': 0,
        'failed': 0,
        'modules': []
    }

    start_time = time.time()

    # Запускаем все тестовые модули
    for module_name, display_name in test_modules:
        module_start = time.time()
        success = run_test_module(module_name, display_name)
        module_time = time.time() - module_start

        if success:
            results['passed'] += 1
            status = "✅"
        else:
            results['failed'] += 1
            status = "❌"

        results['modules'].append({
            'name': display_name,
            'status': status,
            'time': module_time
        })

    # Запускаем тест производительности
    performance_success = run_performance_test()
    if performance_success:
        results['passed'] += 1
    else:
        results['failed'] += 1

    total_time = time.time() - start_time

    # Выводим итоги
    print(f"\n{'='*60}")
    print("🎯 ИТОГИ ТЕСТИРОВАНИЯ")
    print(f"{'='*60}")

    print(f"\n📊 СТАТУС МОДУЛЕЙ:")
    for module in results['modules']:
        print(f"   {module['status']} {module['name']:<25} {module['time']:.2f}с")

    print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
    print(f"   ✅ Успешных модулей: {results['passed']}")
    print(f"   ❌ Неудачных модулей: {results['failed']}")
    print(f"   ⏱ Общее время: {total_time:.2f}с")

    if results['failed'] == 0:
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return True
    else:
        print(f"\n⚠️ ЕСТЬ НЕУДАВШИЕСЯ ТЕСТЫ")
        return False

def run_specific_tests(test_names):
    """Запуск конкретных тестов"""
    print("🚀 ЗАПУСК ВЫБРАННЫХ ТЕСТОВ")
    print("=" * 50)

    test_map = {
        'arithmetic': ('test_arithmetic', 'ТЕСТЫ АРИФМЕТИКИ'),
        'equations': ('test_equations', 'ТЕСТЫ УРАВНЕНИЙ'),
        'derivatives': ('test_derivatives', 'ТЕСТЫ ПРОИЗВОДНЫХ'),
        'integrals': ('test_integrals', 'ТЕСТЫ ИНТЕГРАЛОВ'),
        'trigonometry': ('test_trigonometry', 'ТЕСТЫ ТРИГОНОМЕТРИИ'),
        'algebra': ('test_algebra', 'ТЕСТЫ АЛГЕБРЫ'),
        'performance': ('performance', 'ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ'),
    }

    for test_name in test_names:
        if test_name in test_map:
            if test_name == 'performance':
                run_performance_test()
            else:
                module_name, display_name = test_map[test_name]
                run_test_module(module_name, display_name)
        else:
            print(f"❌ Тест '{test_name}' не найден")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Запуск конкретных тестов
        test_names = sys.argv[1:]
        run_specific_tests(test_names)
    else:
        # Запуск всех тестов
        success = run_all_tests()
        exit(0 if success else 1)