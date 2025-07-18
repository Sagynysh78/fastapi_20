# Кеширование данных с Redis

Этот проект демонстрирует реализацию кеширования данных с использованием Redis для FastAPI приложения.

## Особенности

- ✅ Асинхронное кеширование с aioredis
- ✅ Кеширование GET /notes эндпоинта
- ✅ Автоматическая инвалидация кеша при изменении данных
- ✅ Настраиваемое время жизни кеша (TTL)
- ✅ Логирование операций кеширования

## Архитектура кеширования

### Ключи кеша
Ключи кеша формируются по шаблону: `notes:{user_id}:{skip}:{limit}:{search}`

Примеры:
- `notes:1:0:10:none` - первые 10 заметок пользователя 1
- `notes:1:10:10:none` - заметки 11-20 пользователя 1
- `notes:1:0:10:test` - первые 10 заметок пользователя 1 с поиском "test"

### Инвалидация кеша
При создании, обновлении или удалении заметок удаляются все ключи кеша для данного пользователя по паттерну: `notes:{user_id}:*`

## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Запуск с Docker Compose
```bash
docker-compose up --build
```

Это запустит:
- FastAPI приложение на порту 8000
- PostgreSQL базу данных
- Redis сервер на порту 6379
- Celery worker

### 3. Переменные окружения
- `REDIS_URL` - URL подключения к Redis (по умолчанию: redis://localhost:6379)
- `CACHE_TTL` - время жизни кеша в секундах (по умолчанию: 300)

## Тестирование кеширования

### Автоматический тест
```bash
python test_cache.py
```

Этот тест:
1. Выполняет первый GET запрос (cache MISS)
2. Выполняет второй GET запрос (cache HIT)
3. Создает новую заметку (инвалидирует кеш)
4. Выполняет GET запрос после создания (cache MISS)
5. Выполняет второй GET запрос (cache HIT)

### Ручное тестирование с Postman

1. **Регистрация/Вход**
   ```
   POST /login
   Content-Type: application/x-www-form-urlencoded
   
   username=admin&password=admin123
   ```

2. **Первый запрос заметок (cache MISS)**
   ```
   GET /notes/
   Authorization: Bearer {token}
   ```

3. **Второй запрос заметок (cache HIT)**
   ```
   GET /notes/
   Authorization: Bearer {token}
   ```

4. **Создание заметки (инвалидирует кеш)**
   ```
   POST /notes/
   Authorization: Bearer {token}
   Content-Type: application/json
   
   {"text": "Test note"}
   ```

5. **Запрос заметок после создания (cache MISS)**
   ```
   GET /notes/
   Authorization: Bearer {token}
   ```

## Логирование

В консоли приложения вы увидите сообщения:
- `Cache MISS for key: notes:1:0:10:none` - данные не найдены в кеше
- `Cache HIT for key: notes:1:0:10:none` - данные найдены в кеше
- `Cache invalidated for user 1 after creating note` - кеш инвалидирован

## Структура файлов

```
├── redis_cache.py          # Модуль для работы с Redis
├── notes/routes.py         # Обновленные маршруты с кешированием
├── main.py                 # Основное приложение
├── docker-compose.yml      # Конфигурация Docker с Redis
├── test_cache.py          # Тест кеширования
└── README_CACHE.md        # Этот файл
```

## Производительность

Кеширование значительно ускоряет повторные запросы:
- Первый запрос: ~50-100ms (запрос к БД)
- Последующие запросы: ~5-10ms (из кеша)
- Ускорение: 5-10x

## Мониторинг Redis

Для мониторинга Redis можно использовать:
```bash
# Подключение к Redis CLI
docker exec -it <redis_container> redis-cli

# Просмотр всех ключей
KEYS *

# Просмотр информации о ключе
TTL notes:1:0:10:none

# Очистка всех ключей
FLUSHALL
``` 