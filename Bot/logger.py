import datetime

def log(text:str):
    now = datetime.datetime.now()
    print(str(now) + ': ' + text)