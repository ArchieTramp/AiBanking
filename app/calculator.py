from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict


def to_cents(amount: Decimal | float | int) -> int:
    """Переводит рубли в копейки (целое число)."""
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def from_cents(cents: int) -> Decimal:
    """Переводит копейки обратно в рубли (для вывода)."""
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


def calculate_annuity_payment(principal_cents: int, annual_rate: Decimal, months: int) -> int:
    """
    Рассчитывает ежемесячный аннуитетный платеж в копейках.
    Формула: P = S * (r * (1+r)^n) / ((1+r)^n - 1)
    """
    if months <= 0:
        return 0
    if annual_rate == 0:
        return principal_cents // months

    # Месячная ставка
    monthly_rate = annual_rate / Decimal(12) / Decimal(100)

    # (1+r)^n
    compound = (Decimal(1) + monthly_rate) ** months

    # P = S * (r * compound) / (compound - 1)
    payment = Decimal(principal_cents) * (monthly_rate * compound) / (compound - Decimal(1))

    # Округляем до целых копеек (по правилам математики)
    return int(payment.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def generate_schedule(
        amount_rub: Decimal,
        annual_rate: Decimal,
        months: int,
        issue_date: date,
) -> List[Dict]:
    """
    Генерирует график аннуитетных платежей.
    Возвращает список словарей с полями:
    payment_date, total_payment, principal_part, interest_part, remaining_debt
    (все суммы в копейках).
    """
    principal_cents = to_cents(amount_rub)
    payment_cents = calculate_annuity_payment(principal_cents, annual_rate, months)

    schedule = []
    remaining_debt = principal_cents
    monthly_rate = annual_rate / Decimal(12) / Decimal(100)

    for i in range(1, months + 1):
        # Дата платежа: через i месяцев после выдачи
        payment_date = issue_date + relativedelta(months=i)

        # Проценты на остаток долга
        interest_part = int((Decimal(remaining_debt) * monthly_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        # Тело кредита (в последний платеж корректируем, чтобы закрыть долг ровно в 0)
        if i == months:
            principal_part = remaining_debt
            total_payment = principal_part + interest_part
        else:
            principal_part = payment_cents - interest_part
            total_payment = payment_cents

        remaining_debt -= principal_part

        schedule.append({
            "payment_date": payment_date.isoformat(),
            "total_payment": total_payment,
            "principal_part": principal_part,
            "interest_part": interest_part,
            "remaining_debt": max(0, remaining_debt),
        })

    return schedule


def apply_early_repayment(
        schedule: List[Dict],
        payment_index: int,
        amount_cents: int,
        reduce_term: bool = True,
        annual_rate: Decimal = Decimal("20"),
) -> List[Dict]:
    """
    Применяет досрочное погашение.
    payment_index: номер платежа, ПОСЛЕ которого вносится досрочка (1, 2, ...).
    amount_cents: сумма досрочки в копейках.
    reduce_term: True - уменьшить срок (платеж прежний), False - уменьшить платеж (срок прежний).
    """
    if payment_index <= 0 or payment_index > len(schedule):
        raise ValueError("Некорректный индекс платежа")

    # Берем часть графика до внесения досрочки
    new_schedule = schedule[:payment_index].copy()

    # Остаток долга после payment_index-го платежа
    remaining_debt = schedule[payment_index - 1]["remaining_debt"]

    if amount_cents >= remaining_debt:
        # Полное досрочное погашение
        new_schedule[-1]["remaining_debt"] = 0
        return new_schedule

    new_debt = remaining_debt - amount_cents
    remaining_months = len(schedule) - payment_index
    monthly_rate = annual_rate / Decimal(12) / Decimal(100)

    if reduce_term:
        # Вариант 1: Уменьшаем срок, платеж оставляем прежним
        old_payment = schedule[payment_index]["total_payment"]
        current_date = date.fromisoformat(schedule[payment_index - 1]["payment_date"])

        while new_debt > 0:
            current_date += relativedelta(months=1)
            interest = int((Decimal(new_debt) * monthly_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
            principal = old_payment - interest

            # Если последний платеж меньше обычного
            if principal > new_debt:
                principal = new_debt
                total = principal + interest
            else:
                total = old_payment

            new_debt -= principal

            new_schedule.append({
                "payment_date": current_date.isoformat(),
                "total_payment": total,
                "principal_part": principal,
                "interest_part": interest,
                "remaining_debt": max(0, new_debt),
            })

        return new_schedule

    else:
        # Вариант 2: Уменьшаем платеж, срок оставляем прежним
        new_payment = calculate_annuity_payment(new_debt, annual_rate, remaining_months)
        current_date = date.fromisoformat(schedule[payment_index - 1]["payment_date"])

        for i in range(1, remaining_months + 1):
            current_date += relativedelta(months=1)
            interest = int((Decimal(new_debt) * monthly_rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

            if i == remaining_months:
                principal = new_debt
                total = principal + interest
            else:
                principal = new_payment - interest
                total = new_payment

            new_debt -= principal
            new_schedule.append({
                "payment_date": current_date.isoformat(),
                "total_payment": total,
                "principal_part": principal,
                "interest_part": interest,
                "remaining_debt": max(0, new_debt),
            })

        return new_schedule

def shift_payment_dates(schedule: List[Dict], new_day: int) -> List[Dict]:
    """Меняет день платежа во всем графике."""
    for row in schedule:
        d = date.fromisoformat(row["payment_date"])
        # Если в новом месяце нет такого дня (например, 31-е в феврале), берем последний день
        try:
            new_date = d.replace(day=new_day)
        except ValueError:
            # Берем последний день месяца
            next_month = d.replace(day=1) + relativedelta(months=1)
            new_date = next_month - relativedelta(days=1)
        row["payment_date"] = new_date.isoformat()
    return schedule