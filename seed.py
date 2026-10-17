import asyncio
from datetime import date
from decimal import Decimal

from app.calculator import to_cents
from app.database import AsyncSessionLocal, engine
from app.models import Credit


async def seed_credits():
    # Список из 5 тестовых кредитов
    # Суммы разные, ставки разные, сроки разные, даты выдачи разные
    test_credits = [
        {"amount": Decimal(1000000), "rate": 20.00, "term": 12, "date": date(2024, 1, 1),
         "title": "Кредит на ремонт"},
        {"amount": Decimal(500000), "rate": 15.50, "term": 24, "date": date(2023, 6, 15),
         "title": "Кредит на обучение"},
        {"amount": Decimal(300000), "rate": 25.00, "term": 6, "date": date(2024, 3, 10), "title": "Экспресс-кредит"},
        {"amount": Decimal(2500000), "rate": 18.00, "term": 36, "date": date(2022, 11, 5),
         "title": "Ипотечный кредит"},
        {"amount": Decimal(150000), "rate": 30.00, "term": 3, "date": date(2024, 5, 20), "title": "Микрозайм"},
    ]

    async with AsyncSessionLocal() as session:
        # Проверяем, нет ли уже данных, чтобы не дублировать
        from sqlalchemy import select
        result = await session.execute(select(Credit))
        if result.scalars().first():
            print("База уже содержит кредиты. Пропускаем наполнение.")
            return

        for item in test_credits:
            credit = Credit(
                title=item["title"],
                amount_cents=to_cents(item["amount"]),
                annual_rate=item["rate"],
                term_months=item["term"],
                issue_date=item["date"],
            )
            session.add(credit)

        await session.commit()
        print(f"Успешно добавлено {len(test_credits)} тестовых кредитов.")

    # Закрываем пул соединений
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_credits())