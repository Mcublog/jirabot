from scanf import scanf


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


def worktime_filter(text: str) -> bool:
    if scanf("%dd%dh%dm", text):
        return True

    if scanf("%dd%dh", text):
        return True
    if scanf("%dd%dm", text):
        return True

    if scanf("%dh%dm", text):
        return True

    if scanf("%dd", text):
        return True
    if scanf("%dh", text):
        return True
    if scanf("%dm", text):
        return True

    return False
