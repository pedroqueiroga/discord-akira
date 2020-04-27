import datetime


def is_int(s):
    try:
        int(s)
        return True
    except Exception:
        return False


def seconds_human_friendly(seconds):
    if seconds < 60:
        plural = 's' if seconds > 1 else ''
        return f'{seconds} segundo{plural}'

    readable = str(datetime.timedelta(seconds=seconds))

    if readable.startswith('0:'):
        return readable[2:]
    if 'day' in readable:
        return readable.replace('day', 'dia')

    return readable
