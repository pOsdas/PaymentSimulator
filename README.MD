# Backend payment simulator
### Django server
```shell
poetry run python manage.py runserver 8009
```
### Проверить базу данных
```shell
poetry run python ensure_db.py
```
### Celery
```shell
set PYTHONPATH=C:\Users\your_user\PycharmProjects\PaymentSimulator
celery -A celery_config:app worker -l info
```
Или
```shell
celery -A celery_config:app worker -l info -P solo
celery -A celery_config:app worker -l info --pool=solo
```