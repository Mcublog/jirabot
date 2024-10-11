
def issue_filter(text:str) -> bool:
    if text.count('-') != 1:
        return False
    prefix, number = text.split('-')
    if not prefix or not number:
        return False
    if not prefix.isascii() or not prefix.isupper():
        return False
    if not number.isdecimal():
        return False
    return True

def worktime_filter(text:str) -> bool:
    return text in  ('1d', '4h', '1h')
