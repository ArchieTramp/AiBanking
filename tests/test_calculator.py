from datetime import date
from decimal import Decimal

import pytest

from app.calculator import (
    apply_early_repayment,
    calculate_annuity_payment,
    from_cents,
    generate_schedule,
    shift_payment_dates,
    to_cents,
)

# ==========================================
# БАЗОВЫЕ ТЕСТЫ АРИФМЕТИКИ (проверяем сами функции)
# ==========================================

def test_to_cents():
    """Проверяем перевод рублей в копейки."""
    assert to_cents(Decimal("100.50")) == 10050
    assert to_cents(Decimal("0.01")) == 1
    assert to_cents(100) == 10000


def test_from_cents():
    """Проверяем перевод копеек в рубли."""
    assert from_cents(10050) == Decimal("100.50")
    assert from_cents(1) == Decimal("0.01")


def test_calculate_annuity_payment():
    """Проверяем формулу аннуитетного платежа."""
    # 1 000 000 руб, 20% годовых, 12 месяцев
    # Ожидаемый платеж: 92 634.51 руб (или 9263451 копеек)
    payment = calculate_annuity_payment(
        principal_cents=100_000_000,
        annual_rate=Decimal(20),
        months=12
    )
    assert payment == 9_263_451


# ==========================================
# ТЕСТЫ НА ЭТАЛОННЫХ ЦИФРАХ (Параметризованные)
# ==========================================
# Здесь вы сможете заменить цифры на те, которые выдаст преподаватель.
# Формат: (сумма_руб, ставка_%, срок_мес, ожидаемый_первый_платеж_руб, ожидаемый_общий_долг_руб)

@pytest.mark.parametrize("amount, rate, months, expected_total_payment", [
    # Пример 1: 1 млн, 20%, 12 мес.
    (Decimal(1000000), Decimal(20), 12, Decimal("1111614.09")),

    # Пример 2: 500 000, 15.5%, 24 мес.
    (Decimal(500000), Decimal("15.5"), 24, Decimal("585435.00")),  # <-- Замените на эталон, когда получите

    # Пример 3: 300 000, 25%, 6 мес.
    (Decimal(300000), Decimal(25), 6, Decimal("322500.00")),  # <-- Замените на эталон
])
def test_schedule_total_payment(amount, rate, months, expected_total_payment):
    """
    Проверяет, что сумма всех платежей в графике равна эталонной.
    Это главный тест для домашки.
    """
    schedule = generate_schedule(
        amount_rub=amount,
        annual_rate=rate,
        months=months,
        issue_date=date(2024, 1, 1)
    )

    # Считаем общую сумму всех платежей
    total_cents = sum(row["total_payment"] for row in schedule)
    total_rub = from_cents(total_cents)

    # Сравниваем с эталоном (используем quantize для избежания ошибок float)
    assert total_rub.quantize(Decimal("0.01")) == expected_total_payment.quantize(Decimal("0.01"))


# ==========================================
# ТЕСТЫ ДОСРОЧНОГО ПОГАШЕНИЯ
# ==========================================

def test_early_repayment_reduce_term():
    """При досрочке с уменьшением срока график должен стать короче, а платеж — прежним."""
    base_schedule = generate_schedule(Decimal(1000000), Decimal(20), 12, date(2024, 1, 1))
    new_schedule = apply_early_repayment(
        base_schedule,
        payment_index=3,
        amount_cents=10_000_000,  # 100 000 руб
        reduce_term=True
    )

    # Платежей должно стать меньше (было 12, часть погашена)
    assert len(new_schedule) < 12
    # Платеж после досрочки должен остаться примерно таким же (92634.51)
    assert from_cents(new_schedule[3]["total_payment"]) == Decimal("92634.51")


def test_early_repayment_reduce_payment():
    """При досрочке с уменьшением платежа срок не меняется, а платеж падает."""
    base_schedule = generate_schedule(Decimal(1000000), Decimal(20), 12, date(2024, 1, 1))
    new_schedule = apply_early_repayment(
        base_schedule,
        payment_index=3,
        amount_cents=10_000_000,
        reduce_term=False
    )

    # Платежей осталось столько же (12)
    assert len(new_schedule) == 12
    # Платеж после досрочки должен быть меньше, чем до нее
    assert from_cents(new_schedule[3]["total_payment"]) < Decimal("92634.51")


# ==========================================
# ТЕСТЫ СМЕНЫ ДАТЫ
# ==========================================

def test_shift_payment_dates():
    """Меняем день платежа на 15-е число."""
    schedule = generate_schedule(Decimal(1000000), Decimal(20), 12, date(2024, 1, 1))
    shifted = shift_payment_dates(schedule, new_day=15)

    for row in shifted:
        d = date.fromisoformat(row["payment_date"])
        assert d.day == 15


def test_teacher_example():
    """Эталонный пример из задания."""
    # Предположим, параметры: 500 000 руб, 15%, 10 месяцев (вы узнаете точные)
    schedule = generate_schedule(
        amount_rub=Decimal(500000),
        annual_rate=Decimal(15),
        months=10,
        issue_date=date(2024, 1, 1)
    )
    # Проверяем первый платеж (или общую сумму, в зависимости от формулировки)
    first_payment_cents = schedule[0]["total_payment"]
    assert first_payment_cents == 5505431