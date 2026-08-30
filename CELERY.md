# Celery на Amvera

Celery нужен, когда долгую или периодическую работу необходимо выполнять отдельно от веб-приложения. Это отдельный пример: FastAPI, Flask и Django из основных репозиториев не зависят от Celery и работают без Redis.

В примере веб-приложение отправляет строку через Redis, общий worker переводит ее в верхний регистр, а результат сохраняется в Redis.

## Какие проекты нужны

Для проверки создайте три проекта в одном регионе:

1. Любое Python-приложение, которое отправляет задачу.
2. Redis из преднастроенных сервисов Amvera.
3. Отдельное приложение с общим worker из репозитория [`amvera-fastapi-celery-worker-example`](https://github.com/amvera-academy/amvera-fastapi-celery-worker-example).

Worker не зависит от FastAPI, Flask или Django. Его можно использовать с любым Python-приложением.

## Переменная REDIS_URL

В веб-приложении и worker задайте одинаковую переменную `REDIS_URL` с внутренним адресом Redis:

```text
REDIS_URL=redis://:<password>@<internal-redis-host>:6379/0
```

Внутренний адрес и пароль находятся в настройках созданного Redis.

## Отправка задачи

Добавьте Celery в зависимости веб-приложения:

```text
celery[redis]==5.6.3
```

Создайте клиент и отправьте задачу с именем `process_text`:

```python
import os

from celery import Celery


REDIS_URL = os.environ["REDIS_URL"]
celery_app = Celery("web", broker=REDIS_URL, backend=REDIS_URL)


def start_task(text):
    return celery_app.send_task("process_text", args=[text])
```

Полученный `result.id` можно сохранить или вернуть из API. Статус и результат читаются через `AsyncResult`:

```python
from celery.result import AsyncResult


def get_task(task_id):
    task = AsyncResult(task_id, app=celery_app)
    return {"status": task.status, "result": task.result if task.successful() else None}
```

## Деплой

1. Создайте Redis.
2. Создайте отдельное приложение для worker.
3. Загрузите общий worker-репозиторий.
4. Добавьте одинаковый `REDIS_URL` в worker и веб-приложение.
5. Запустите сборку worker и веб-приложения.

Команда запуска worker уже указана в его `amvera.yml`.

## Проверка

Отправьте задачу `process_text` со строкой `Hello, Amvera!`, затем запросите результат по идентификатору задачи.

Рабочий результат имеет статус `SUCCESS` и содержит строку `HELLO, AMVERA!`.

## Локальный запуск worker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export REDIS_URL=redis://localhost:6379/0
celery --app worker worker --loglevel=INFO --concurrency=1
```
