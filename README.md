# FastAPI на Amvera

Простой пример деплоя FastAPI в [Amvera](https://amvera.ru/fastapi). 

Это тестовое приложение показывает работу API, статических файлов и персистентное сохранение SQlite в постоянное хранилище Amvera.

[КАК СОХРАНЯТЬ БД](#как-правильно-сохранять-бд) | [СТАТИЧЕСКИЕ ФАЙЛЫ](#статические-файлы) | [CELERY](CELERY.md) | [КАК ЗАПУСТИТЬ НА AMVERA](#деплой-в-amvera) 

## Демо-приложение

Приложение имеет веб-интерфейс, на котором вы сразу можете выполнить доступные тестовые запросы. 

- `GET /api/health`
- `GET /api/items`
- `POST /api/items`
- `DELETE /api/items/{id}`
- `GET /docs`

Все запросы можно выполнить на главной странице.

<img width="830" height="862" alt="Screenshot_1" src="https://github.com/user-attachments/assets/d3efe808-e917-4dec-a406-ce650221d8ee" />

## Как правильно сохранять БД

В разработке очень важно учитывать, что любые изменяемые в процессе работы приложения файлы (базы данных, списки, которые нужно сохранять, JSON и т.п.) **необходимо сохранять в [постоянное хранилище Amvera](https://docs.amvera.ru/applications/storage.html#data)**.

Здесь нет ничего сложного: вместо сохранения БД в той же папке, что код, ее нужно сохранять по пути `/data` (это значение по умолчанию, его можно сменить во вкладке "Конфигурация" вашего проекта).

Например:
```python
DATA_DIR = Path("/data")
DATABASE_PATH = DATA_DIR / "items.sqlite3"

def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection
```

## Статические файлы

Файлы находятся в директории static. Путь считается от main.py.

Пример:

```python
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
```

## Локальный запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn --host 0.0.0.0 --port 5000 main:app
```

Откройте localhost:5000.

## Деплой в Amvera

Для деплоя конкретно этого приложения вам понадобится:
1. Создать аккаунт в [Amvera](https://cloud.amvera.ru);
2. Создать обычное приложение в любом регионе;
3. Загрузить в него код репозитория;
4. Во вкладке "Конфигурация" нажать кнопку "Собрать".

Когда приложение будет готово к работе и статус сменится на "Запущено", во вкладке "Домены" можно будет создать бесплатное доменное имя от Амвера.

Отдельный пример фоновой задачи и worker описан в [CELERY.md](CELERY.md).
