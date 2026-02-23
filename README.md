# CRM FastAPI с AI-анализом лидов

## Контекст
Сервис управляет лидами из Telegram и партнерских каналов.  
Лиды проходят **холодную обработку**, затем могут быть **переданы в продажи**.  
AI-ассистент анализирует активность и рекомендует менеджеру следующий шаг.

---

## Функционал
- Создание лидов (`source`, `business_domain`)  
- Продвижение лидов по стадиям: `new → contacted → qualified → transferred → lost`  
- AI-анализ: возвращает `score` и `recommendation`  
- Передача в продажи только если: `score ≥ 0.6` и указан `business_domain`  
- Управление сделками: `new → kyc → agreement → paid → lost`

---

## Архитектура
- **Backend:** Python + FastAPI  
- **DB:** PostgreSQL + SQLAlchemy  
- **Templates:** Jinja2 (тестовый UI)  
- **AI:** встроенный сервис-симулятор  

Структура:

.
├─ main.py
├─ templates/index.html
├─ .env
├─ requirements.txt
└─ README.md


---

## AI
- Получает: источник, этап, бизнес-домен, активность  
- Возвращает: вероятность сделки (`score`), рекомендацию (`recommendation`)  
- Решение: человек решает, передавать лида в продажи или нет

---

## Запуск
```bash
# установка зависимости
pip install -r requirements.txt

# создать .env
DATABASE_URL=postgresql://postgres:<PASSWORD>@localhost:5432/crm

# запустить
uvicorn main:app --reload

Улучшения:
Реальный ML для AI
Аутентификация менеджеров
Логи, мониторинг, приоритизация лидов
