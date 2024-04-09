# Email Auth Remote

Проект для интеграции МС авторизации с другими Django МС.

## Как пользоваться

Добавить проект в INSTALLED_APPS

```python
# File: settings.py

INSTALLED_APPS = [
    ...
    "email_auth_remote",
]
```

Установить переменную AUTH_ENDPOINT_URL

```python
# File: settings.py

AUTH_ENDPOINT_URL = "http://localhost:8000/api/v1/auth/user/"  # Как пример
```

Добавить класс аутентификации

```python
# File: settings.py

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "email_auth_remote.authentication.EndpointAuthentication",
    ],
}
```

**Важная информация:**
При использовании библиотеки модель EmailUser, полученная через request.user не будет сохранена в
БД. На эту модель невозможно ссылаться через ForeignKey и тд. Сохранение в БД также невозможно.

## Сборка

***Необходимо только для сборки, для интеграции не надо.***

Как собрать проект локально

```bash
python3 -m pip install build
python3 -m build 
```

### Проверка собранного пакета

```bash
python3 -m pip install twine
twine check dist/*
```

### Выкладывание проекта в PYPI

```bash
twine upload dist/*
```