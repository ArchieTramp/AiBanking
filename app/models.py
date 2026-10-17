from datetime import date

from sqlalchemy import BigInteger, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Credit(Base):
    __tablename__ = "credits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Основные параметры кредита
    amount_cents: Mapped[int] = mapped_column(BigInteger, comment="Сумма кредита в копейках")
    annual_rate: Mapped[float] = mapped_column(Numeric(5, 2), comment="Годовая ставка в процентах")
    term_months: Mapped[int] = mapped_column(comment="Срок кредита в месяцах")

    # Даты
    issue_date: Mapped[date] = mapped_column(Date, comment="Дата выдачи кредита")

    # (Опционально) Поле для связи с клиентом или названием, если понадобится в будущем
    title: Mapped[str] = mapped_column(String(100), default="Потребительский кредит")