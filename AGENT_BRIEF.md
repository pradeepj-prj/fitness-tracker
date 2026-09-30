# Calorie Tracker API - Agent Brief

Base URL: `http://localhost:8000`

## Overview

Profile-aware calorie tracking API. Same backend can track multiple people separately.

### Current profiles
- `vidhi`
- `pradeep`

If profile is omitted, the API defaults to `vidhi` for backward compatibility.

## Endpoints

### Settings

**GET /settings?profile={profile}** - Get daily calorie goal for a profile
```json
{ "profile": "pradeep", "daily_calorie_goal": 2000.0 }
```

**PUT /settings?profile={profile}** - Update daily calorie goal
```json
// Request
{ "daily_calorie_goal": 1800 }
```

---

### Food Search (lookup calories before logging)

**GET /foods/search?q={query}** - Search for food by name
```json
// Response
{
  "query": "banana",
  "results": [
    { "name": "Banana, raw", "calories": 89.0, "protein_g": 1.1, "carbs_g": 23.0, "fat_g": 0.3, "source": "usda" }
  ],
  "total_results": 10
}
```

**GET /foods/barcode/{code}** - Lookup by barcode
```json
// Response
{ "name": "Coca-Cola", "calories": 42.0, "protein_g": 0.0, "carbs_g": 10.6, "fat_g": 0.0, "source": "open_food_facts" }
```

---

### Food Entries (log what was eaten)

**POST /entries** - Log food intake
```json
// Request
{
  "profile": "pradeep",
  "food_name": "Banana",
  "calories": 89,
  "protein_g": 1.1,
  "carbs_g": 23.0,
  "fat_g": 0.3,
  "source": "usda",
  "logged_at": "2026-05-14T12:30:00"
}
```

**GET /entries?profile={profile}** - List logged entries
- Optional query params: `date=YYYY-MM-DD`, `limit=100`, `offset=0`

**GET /entries/{id}?profile={profile}** - Get single entry

**PUT /entries/{id}?profile={profile}** - Update entry
```json
{ "calories": 100 }
```

**DELETE /entries/{id}?profile={profile}** - Delete entry

---

### Deficit Tracking

**GET /deficit/today?profile={profile}** - Get today's calorie status
```json
{
  "date": "2026-05-14",
  "profile": "pradeep",
  "daily_goal": 2000.0,
  "total_consumed": 850.0,
  "remaining": 1150.0,
  "entries_count": 3
}
```

**GET /deficit/{date}?profile={profile}** - Get deficit for specific date (YYYY-MM-DD)

---

## Typical Workflow

1. Identify the profile first (`vidhi` or `pradeep`)
2. User says "I ate a banana" → **search** `/foods/search?q=banana`
3. Pick best match → **log** `POST /entries` with the right `profile`
4. User asks "how many calories left?" → **check** `/deficit/today?profile=...`
5. User wants to change goal → **update** `PUT /settings?profile=...`

## Notes

- All calorie values from the food APIs are per 100g; adjust for actual portion
- Timestamps are UTC
- Source field tracks where calorie data originated
- Dashboard routes on the hub:
  - Vidhi: `/calorie-tracker-dashboard/`
  - Pradeep: `/pradeep-calorie-dashboard/`
