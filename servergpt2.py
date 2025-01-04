import asyncio
import re
from flask import Flask, request, jsonify
from g4f.client import Client
import requests

app = Flask(__name__)
client = Client()

# Функция для отправки запроса с тайм-аутом
def gpt_request(description, timeout=10):
    try:
        # Создаем запрос с тайм-аутом
        response = client.chat.completions.create(
            model="llama-3.1-70b",
            messages=[{"role": "user", "content": description}],
            web_search=False
        )
        return response
    except requests.exceptions.Timeout:
        raise Exception("Request timed out")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Получаем данные из запроса
        data = request.get_json()
        description = data.get('description', '')

        # Убираем специальные символы и выводим описание в одну строку
        cleaned_description = " ".join(re.sub(r'[^a-zA-Z0-9а-яА-ЯёЁ\s]', '', description).split())
        print("Полученное описание:", cleaned_description)

        # Если описание пустое, возвращаем ошибку
        if not description:
            return jsonify({'error': 'Нет описания для обработки'}), 400

        # Используем запрос с тайм-аутом
        try:
            response = gpt_request(description)
            result = response.choices[0].message.content
            return jsonify({'response': result})

        except Exception as e:
            return jsonify({'error': str(e)}), 504

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9557)
