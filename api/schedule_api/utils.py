from django.utils.dateparse import parse_datetime
from datetime import timedelta

def get_dates_between(start_str, end_str):
    start_dt = parse_datetime(start_str)
    end_dt = parse_datetime(end_str)
    
    if not start_dt or not end_dt:
        raise ValueError("Некорректный формат даты")
    
    start_date = start_dt.date()
    end_date = end_dt.date()
    
    if start_date > end_date:
        return [start_date.isoformat()]
    
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.isoformat())
        current_date += timedelta(days=1)
    
    return dates