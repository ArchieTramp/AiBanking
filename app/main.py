import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.calculator import from_cents, generate_schedule
from app.database import engine, get_pool_status, get_session
from app.models import Credit
from app.schemas import PaymentRow, ScheduleResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: движок уже создан при импорте.
    # Здесь можно, например, проверить подключение к БД (опционально).
    yield
    # Shutdown: корректно закрываем все соединения пула.
    await engine.dispose()


app = FastAPI(title="Hexlet Credits API", lifespan=lifespan)


@app.get("/live")
async def live():
    """Liveness: процесс жив. Внешние зависимости не проверяем."""
    return {"status": "ok"}


@app.get("/ready")
async def ready(session: AsyncSession = Depends(get_session)):
    """Readiness: приложение готово принимать трафик (БД доступна)."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"db not ready: {exc}")
    return {"status": "ready", "pool": get_pool_status()}

@app.get("/credits/{credit_id}/schedule", response_model=ScheduleResponse)
async def get_credit_schedule(
    credit_id: int,
    session: AsyncSession = Depends(get_session)
):
    # 1. Ищем кредит в базе
    result = await session.execute(select(Credit).where(Credit.id == credit_id))
    credit = result.scalar_one_or_none()

    if not credit:
        raise HTTPException(status_code=404, detail="Кредит не найден")

    # 2. Генерируем график
    # Переводим сумму из копеек обратно в рубли для калькулятора
    amount_rub = Decimal(credit.amount_cents) / 100
    rate = Decimal(str(credit.annual_rate))

    raw_schedule = generate_schedule(
        amount_rub=amount_rub,
        annual_rate=rate,
        months=credit.term_months,
        issue_date=credit.issue_date,
    )

    # 3. Форматируем ответ (переводим копейки в рубли для вывода)
    formatted_schedule = []
    for row in raw_schedule:
        formatted_schedule.append(
            PaymentRow(
                payment_date=row["payment_date"],
                total_payment=float(from_cents(row["total_payment"])),
                principal_part=float(from_cents(row["principal_part"])),
                interest_part=float(from_cents(row["interest_part"])),
                remaining_debt=float(from_cents(row["remaining_debt"])),
            )
        )

    return ScheduleResponse(
        credit_id=credit.id,
        title=credit.title,
        amount=float(amount_rub),
        annual_rate=float(credit.annual_rate),
        term_months=credit.term_months,
        issue_date=credit.issue_date,
        schedule=formatted_schedule,
    )