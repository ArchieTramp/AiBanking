from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import List

class PaymentRow(BaseModel):
    payment_date: str
    total_payment: float
    principal_part: float
    interest_part: float
    remaining_debt: float

class ScheduleResponse(BaseModel):
    credit_id: int
    title: str
    amount: float
    annual_rate: float
    term_months: int
    issue_date: date
    schedule: List[PaymentRow]