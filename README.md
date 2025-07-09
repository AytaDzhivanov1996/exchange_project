# Django Exchange App

Веб-приложение для обмена вещами между пользователями.

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd exchange_project
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Примените миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустите сервер:
```bash
python manage.py runserver
```

## Использование

- Откройте браузер и перейдите на http://127.0.0.1:8000/
- Зарегистрируйтесь или войдите в систему
- Создавайте объявления и предлагайте обмены

## Тестирование

Запустите тесты:
```bash
python -m pytest
```

## API Endpoints

- GET /api/ads/ - список объявлений
- POST /api/ads/ - создание объявления
- GET /api/ads/{id}/ - детали объявления
- POST /api/ads/{id}/exchange_proposal/ - создание предложения обмена
- GET /api/proposals/ - список предложений