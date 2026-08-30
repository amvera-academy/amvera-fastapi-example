# Celery на Amvera

Celery нужен тогда, когда какую-либо долгую или повторяющуюся работу необходимо выполнять отдельно от веб-приложения. 

Это самый простой пример: веб-приложение отправляет строку через Redis, общий worker переводит ее в верхний регистр, а результат сохраняется в Redis.

## Какие проекты нужны

Для проверки создайте три проекта в **одном регионе**:

1. Любое Python приложение, которое отправляет задачу;
2. Redis из преднастроенных сервисов Amvera;
3. Отдельное приложение с общим worker из репозитория [`amvera-fastapi-celery-worker-example`](https://github.com/latuk993/amvera-fastapi-celery-worker-example).

Worker не зависит от FastAPI, Flask или Django. Его можно использовать с любым Python приложением.

## Переменная REDIS_URL

В веб приложении и worker задайте переменную `REDIS_URL` с внутренним доменом Redis:

```text
REDIS_URL=redis://:<пароль>@<внутренений-домен-redis>:6379/0
```

## Отправка задачи

Добавьте Celery в зависимости:

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

`result.id`, который мы получили по итогу можно вернуть через API. Статус и результат читаются через `AsyncResult`:

```python
from celery.result import AsyncResult


def get_task(task_id):
    task = AsyncResult(task_id, app=celery_app)
    return {"status": task.status, "result": task.result if task.successful() else None}
```
