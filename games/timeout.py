from datetime import datetime, timedelta
from db.dbfunc import set_channel_time, get_channel_time
from utils import datetime2str

class Timeout:
    def __init__(self, numSeconds, channel_id):
        self.numSeconds = numSeconds
        self.channel_id = channel_id
    

    def resetTimer(self):
        set_channel_time(self.channel_id, datetime2str(datetime.now()))
    
    def isTimeUp(self):
        return datetime.now() > get_channel_time(self.channel_id) + timedelta(seconds=self.numSeconds)

