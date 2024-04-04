from datetime import timedelta

def static_path(match, start, end):
    """
    Time independent path. Params can specify a
    subdir

    Example::
         {
           "generate": "static_path",
           "params": { "subdir": "complete"}
         }

    """

    params = match.get('params', {})
    subdir = params.get('subdir', '.')

    return [{ 'timestamp': subdir, 'name': subdir}]

def generate_datetime_daily(match, start, end, params={}):
    """
    Given a start and an end, generate the datetime
    objects corresponding to each run for each day.

    Args:
       match (dict): has 'pattern' and generator function
       start (datetime): Start of the time range
       end (datetime): End of range. If None, default = start
    """

    params = match.get('params', {})
    pattern = match['pattern']

    if end < start:
        start, end = end, start

    names = []
    current = start
    while current <= end:
        if isinstance(pattern, str):
            name = current.strftime(pattern)
        elif callable(pattern):
            name = pattern(current)
        else:
            raise Exception("Unsupported pattern type")

        names.append({"timestamp": current.isoformat(), "name": name})
        current += timedelta(days=1)

    return names

handlers = {
    "static_path": static_path,
    "generate_datetime_daily": generate_datetime_daily,
}
