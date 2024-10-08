def summary(timetrack: int) -> tuple[int, int, int]:
    hours, remainder = divmod(timetrack, 3600)
    minutes, seconds = divmod(remainder, 60)
    result = (int(hours), int(minutes), int(seconds))
    return result
