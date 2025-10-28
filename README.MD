# Backend payment simulator
### Django server
```shell
poetry run python manage.py runserver 8009
```
### Celery
```shell
set PYTHONPATH=C:\Users\your_user\PycharmProjects\work_backend\backend
cd backend
celery -A celery_config:app worker -l info
```
Или
```shell
celery -A celery_config:app worker -l info -P solo
celery -A celery_config:app worker -l info --pool=solo
```