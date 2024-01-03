from datetime import date, datetime


def first_day_of_month() -> date:
    return datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()


def first_day_of_prev_month() -> date:
    prev_month = datetime.now().month.numerator - 1
    if prev_month < 1:
        prev_month = 12
    return datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0, month=prev_month).date()


def tomorrow() -> date:
    return datetime.now().date().replace(day=date.today().day.numerator + 1)
