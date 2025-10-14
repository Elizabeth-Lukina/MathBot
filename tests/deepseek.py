# tests/deepseek_test.py
import os
import requests

from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')


def test_deepseek_models():
    """Тестируем доступные модели DeepSeek"""

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    # Тестируем разные модели
    models_to_test = [
        "deepseek-chat",
        "deepseek-coder",
        "deepseek-reasoner"  # если доступен
    ]

    for model in models_to_test:
        print(f"\n🔍 Тестируем модель: {model}")

        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Реши математическую задачу: Найди производную f(x) = x² + 3x - 5"}
            ],
            "max_tokens": 500,
            "temperature": 0.1
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            result = response.json()

            if 'choices' in result:
                print(f"✅ {model} работает!")
                print(f"Ответ: {result['choices'][0]['message']['content'][:100]}...")
            else:
                print(f"❌ Ошибка {model}: {result.get('error', {}).get('message', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Ошибка запроса для {model}: {e}")


def get_available_models():
    """Получаем список доступных моделей"""
    url = "https://api.deepseek.com/models"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            models = response.json()
            print("📋 Доступные модели:")
            for model in models.get('data', []):
                print(f"  - {model['id']}")
        else:
            print(f"❌ Не удалось получить модели: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка получения моделей: {e}")


if __name__ == "__main__":
    print("🧪 Тестирование DeepSeek API")
    print(f"🔑 API Key: {DEEPSEEK_API_KEY[:10]}...{DEEPSEEK_API_KEY[-5:] if DEEPSEEK_API_KEY else 'NOT SET'}")

    get_available_models()
    test_deepseek_models()