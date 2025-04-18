# Hireling System Documentation

The hireling system allows players to hire NPCs of various character classes to assist them in their adventures. Hirelings have loyalty levels that affect their performance and can be managed through payments and rewards.

## Hireling Attributes

- `name`: The hireling's name
- `character_class`: The hireling's class (e.g., "fighter", "cleric", "magic-user")
- `level`: The hireling's level (default: 1)
- `experience`: The hireling's experience points (default: 0)
- `loyalty`: The hireling's loyalty level (0-100, default: 50.0)
- `wage`: Daily wage in gold pieces (default: 10)
- `is_available`: Whether the hireling is available for hire
- `last_payment_date`: Date of last payment
- `days_unpaid`: Number of days since last payment

## API Endpoints

### Create a Hireling
```http
POST /api/hirelings/
```

Request body:
```json
{
    "name": "string",
    "character_class": "string",
    "level": 0,
    "wage": 0
}
```

### List Hirelings
```http
GET /api/hirelings/
```

Query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

### Get Hireling Details
```http
GET /api/hirelings/{hireling_id}
```

### Hire a Hireling
```http
PUT /api/hirelings/{hireling_id}/hire/{character_id}
```

### Dismiss a Hireling
```http
PUT /api/hirelings/{hireling_id}/dismiss
```

### Pay a Hireling
```http
PUT /api/hirelings/{hireling_id}/pay?days={days}
```

Query parameters:
- `days`: Number of days to pay for

### Reward a Hireling
```http
PUT /api/hirelings/{hireling_id}/reward?amount={amount}
```

Query parameters:
- `amount`: Amount of gold to reward

## Loyalty System

- Base loyalty: 50.0
- Increases by 2 points per day paid
- Decreases by 5 points per unpaid day
- Can be increased by rewards (1 point per 10 gold, max 10 points)
- Loyalty affects hireling performance in combat and other activities

## Example Usage

1. Create a hireling:
```bash
curl -X POST "http://localhost:8000/api/hirelings/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Boromir", "character_class": "fighter", "level": 1, "wage": 10}'
```

2. Hire the hireling to a character:
```bash
curl -X PUT "http://localhost:8000/api/hirelings/1/hire/1"
```

3. Pay the hireling for 7 days:
```bash
curl -X PUT "http://localhost:8000/api/hirelings/1/pay?days=7"
```

4. Give a reward:
```bash
curl -X PUT "http://localhost:8000/api/hirelings/1/reward?amount=50"
``` 