from datetime import datetime, timedelta
from typing import Tuple
import calendar

class PeriodService:
    @staticmethod
    def _start_of_day(dt: datetime) -> datetime:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def _end_of_day(dt: datetime) -> datetime:
        return dt.replace(hour=23, minute=59, second=59, microsecond=0)

    @staticmethod
    def _month_start(year: int, month: int) -> datetime:
        return datetime(year, month, 1, 0, 0, 0)

    @staticmethod
    def _month_end(year: int, month: int) -> datetime:
        last_day = calendar.monthrange(year, month)[1]
        return datetime(year, month, last_day, 23, 59, 59)

    @staticmethod
    def _shift_month(year: int, month: int, delta_months: int) -> Tuple[int, int]:
        total = (year * 12 + (month - 1)) + delta_months
        new_year = total // 12
        new_month = (total % 12) + 1
        return new_year, new_month

    @staticmethod
    def _quarter_start(year: int, quarter: int) -> datetime:
        start_month = 3 * quarter - 2
        return datetime(year, start_month, 1, 0, 0, 0)

    @staticmethod
    def _quarter_end(year: int, quarter: int) -> datetime:
        end_month = 3 * quarter
        return PeriodService._month_end(year, end_month)

    @staticmethod
    def resolve_period(period_str: str) -> Tuple[datetime, datetime, str]:
        today = PeriodService._start_of_day(datetime.now())
        now_end_of_day = PeriodService._end_of_day(datetime.now())
        
        if period_str == "today":
            start = today
            end = now_end_of_day
            label = "today"
        elif period_str == "yesterday":
            start = today - timedelta(days=1)
            end = today - timedelta(seconds=1)
            label = "yesterday"
        elif period_str == "current_month":
            start = today.replace(day=1)
            end = now_end_of_day
            label = "current_month"
        elif period_str == "last_month" or period_str == "previous_month":
            first_day_this_month = today.replace(day=1)
            end = first_day_this_month - timedelta(seconds=1)
            start = (first_day_this_month - timedelta(days=1)).replace(day=1)
            label = period_str
        elif period_str == "current_quarter":
            quarter = (today.month - 1) // 3 + 1
            start = PeriodService._quarter_start(today.year, quarter)
            end = now_end_of_day
            label = "current_quarter"
        elif period_str == "last_quarter":
            quarter = (today.month - 1) // 3 + 1
            if quarter == 1:
                start = datetime(today.year - 1, 10, 1)
                end = datetime(today.year - 1, 12, 31, 23, 59, 59)
            else:
                start = datetime(today.year, 3 * (quarter - 1) - 2, 1)
                end = datetime(today.year, 3 * (quarter - 1), calendar.monthrange(today.year, 3 * (quarter - 1))[1], 23, 59, 59)
            label = "last_quarter"
        elif period_str == "current_year":
            start = datetime(today.year, 1, 1)
            end = now_end_of_day
            label = "current_year"
        elif period_str == "last_year":
            start = datetime(today.year - 1, 1, 1)
            end = datetime(today.year - 1, 12, 31, 23, 59, 59)
            label = "last_year"
        elif period_str == "last_12_months":
            # 12 meses calendário completos anteriores + mês atual até agora
            first_day_current_month = today.replace(day=1)
            start = (first_day_current_month - timedelta(days=365)).replace(day=1)
            end = now_end_of_day
            label = "last_12_months"
        else:
            raise ValueError(f"Invalid period: {period_str}")
            
        return start, end, label

    @staticmethod
    def get_comparison_period(period_str: str, start: datetime, end: datetime) -> Tuple[datetime, datetime, str]:
        duration = end - start

        if period_str == "today":
            comp_start = start - timedelta(days=1)
            comp_end = end - timedelta(days=1)
            label = "yesterday"
            return comp_start, comp_end, label

        if period_str == "yesterday":
            comp_start = start - timedelta(days=1)
            comp_end = end - timedelta(days=1)
            label = "day_before_yesterday"
            return comp_start, comp_end, label

        if period_str in {"current_month", "current_year", "current_quarter"}:
            if period_str == "current_month":
                prev_year, prev_month = PeriodService._shift_month(start.year, start.month, -1)
                comp_start = PeriodService._month_start(prev_year, prev_month)
                comp_end_limit = PeriodService._month_end(prev_year, prev_month)
                label = "previous_month_to_date"
            elif period_str == "current_quarter":
                quarter = (start.month - 1) // 3 + 1
                prev_quarter = quarter - 1
                prev_year = start.year
                if prev_quarter == 0:
                    prev_quarter = 4
                    prev_year -= 1
                comp_start = PeriodService._quarter_start(prev_year, prev_quarter)
                comp_end_limit = PeriodService._quarter_end(prev_year, prev_quarter)
                label = "previous_quarter_to_date"
            else:
                comp_start = datetime(start.year - 1, 1, 1, 0, 0, 0)
                comp_end_limit = datetime(start.year - 1, 12, 31, 23, 59, 59)
                label = "previous_year_to_date"

            candidate_end = comp_start + duration
            comp_end = candidate_end if candidate_end <= comp_end_limit else comp_end_limit
            return comp_start, comp_end, label

        if period_str in {"last_month", "previous_month"}:
            year, month = PeriodService._shift_month(start.year, start.month, -1)
            comp_start = PeriodService._month_start(year, month)
            comp_end = PeriodService._month_end(year, month)
            label = "month_before_last"
            return comp_start, comp_end, label

        if period_str == "last_quarter":
            quarter = (start.month - 1) // 3 + 1
            prev_quarter = quarter - 1
            prev_year = start.year
            if prev_quarter == 0:
                prev_quarter = 4
                prev_year -= 1
            comp_start = PeriodService._quarter_start(prev_year, prev_quarter)
            comp_end = PeriodService._quarter_end(prev_year, prev_quarter)
            label = "quarter_before_last"
            return comp_start, comp_end, label

        if period_str == "last_year":
            comp_start = datetime(start.year - 1, 1, 1, 0, 0, 0)
            comp_end = datetime(start.year - 1, 12, 31, 23, 59, 59)
            label = "year_before_last"
            return comp_start, comp_end, label

        comp_start = start - duration - timedelta(seconds=1)
        comp_end = start - timedelta(seconds=1)
        label = f"previous_{period_str}"
        return comp_start, comp_end, label
