# Postman Request Example для Ozon API

## URL
```
POST https://api-seller.ozon.ru/v1/assembly/fbs/posting/list
```

## Headers
```
Client-Id: 2380987
Api-Key: df31cd3a-5647-49c1-8a98-3c50838b8326
Content-Type: application/json
```

## Request Body (JSON)

### Минимальный запрос (только свежие заказы за последнюю неделю):
```json
{
  "filter": {
    "cutoff_from": "2025-11-22T12:00:00.000Z"
  },
  "limit": 1000,
  "sort_dir": "ASC"
}
```

### Расширенный запрос с периодом:
```json
{
  "filter": {
    "cutoff_from": "2025-11-22T00:00:00.000Z",
    "cutoff_to": "2025-11-29T23:59:59.999Z"
  },
  "limit": 1000,
  "sort_dir": "ASC"
}
```

### Запрос с фильтром по способу доставки:
```json
{
  "filter": {
    "cutoff_from": "2025-11-22T00:00:00.000Z",
    "delivery_method_id": 0
  },
  "limit": 1000,
  "sort_dir": "ASC"
}
```

### Запрос для следующей страницы (с cursor):
```json
{
  "filter": {
    "cutoff_from": "2025-11-22T00:00:00.000Z"
  },
  "limit": 1000,
  "sort_dir": "ASC",
  "cursor": "your_cursor_string_from_previous_response"
}
```

## Пример даты cutoff_from (7 дней назад от текущей даты)

Формат: `YYYY-MM-DDThh:mm:ss.000Z` (UTC время)

Пример для сегодня (2025-11-29):
```json
"cutoff_from": "2025-11-22T00:00:00.000Z"
```

## Текущие значения из вашего склада

- **Client-Id**: `2380987`
- **Api-Key**: `df31cd3a-5647-49c1-8a98-3c50838b8326`

## Как получить актуальную дату cutoff_from

Используйте эту команду в терминале:
```bash
python3 -c "from datetime import datetime, timedelta; print((datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S.000Z'))"
```

Или онлайн калькулятор UTC времени минус 7 дней.

## Ожидаемый Response

```json
{
  "cursor": "string",
  "cutoff": "2019-08-24T14:15:22Z",
  "postings": [
    {
      "assembly_code": "string",
      "posting_number": "string",
      "products": [
        {
          "offer_id": "string",
          "picture_url": "string",
          "product_name": "string",
          "quantity": 0,
          "sku": 0
        }
      ]
    }
  ]
}
```

