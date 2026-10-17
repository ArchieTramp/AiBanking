from datetime import date
from decimal import Decimal

from app.calculator import from_cents, generate_schedule

# Пример: 1 млн рублей, 20% годовых, 12 месяцев, выдан 1 января 2024
schedule = generate_schedule(
    amount_rub=Decimal(1000000),
    annual_rate=Decimal(20),
    months=12,
    issue_date=date(2024, 1, 1),
)

total_paid = 0
for row in schedule:
    total_paid += row["total_payment"]
    print(
        f"{row['payment_date']} | "
        f"Платеж: {from_cents(row['total_payment'])} | "
        f"Тело: {from_cents(row['principal_part'])} | "
        f"Проценты: {from_cents(row['interest_part'])} | "
        f"Остаток: {from_cents(row['remaining_debt'])}"
    )

print(f"Всего выплачено: {from_cents(total_paid)}")