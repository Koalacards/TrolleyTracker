from datetime import datetime, timedelta

class Timeout:
    def __init__(self, numSeconds):
        self.numSeconds = numSeconds
        self.datetime = datetime.now()
    

    def resetTimer(self):
        self.datetime = datetime.now()
    
    def isTimeUp(self):
        return datetime.now() > self.datetime + timedelta(seconds=self.numSeconds)

