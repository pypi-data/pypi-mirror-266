from datetime import datetime, timedelta


def to_periodic_format(period):
    if period == 'Day':
        return 'daily'
    elif period == 'Week':
        return 'weekly'
    elif period == 'Month':
        return 'monthly'
    elif period == 'Year':
        return 'yearly'
    elif period == 'AllTime':
        return 'all time'


def today_as_start_and_enddate_str(pattern='%Y-%m-%d'):
    today = datetime.now().date()
    start_date = today
    end_date = today + timedelta(days=1)
    start_date_str = start_date.strftime(pattern)
    end_date_str = end_date.strftime(pattern)

    return start_date_str, end_date_str
