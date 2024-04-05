import inspect
import re
from datetime import datetime, date, timedelta, time 

DEBUG_LEVEL=2

# now = datetime.datetime.now(timezone.utc)
# nowiso = now.isoformat(timespec='milliseconds')
# UTCNOW = re.sub('\+.+','', nowiso) + 'Z' # remove the tz suffix 

class UtilsTrc:
    def __init__ (self):
        pass

    def trace(self, lev, msg):
        caller = inspect.stack()[1][3]
        if ( DEBUG_LEVEL >= lev ):
            print(f"{caller}: {msg}")

def is_email_format(id):
    m = re.search(".+@.+[.].+$", id)
    if (m) :
        return (True)
    else:
        return(False)
    
def midnight_iso_ms(days):
    pastday = date.today() - timedelta(days)
    dts = pastday.isoformat() + 'T00:00:00'
    return(datetime_to_iso_ms(dts))

# date time format required for Wbx 
def datetime_to_iso_ms(dts):
    dts=re.sub('Z$','',dts)
    dt=datetime.fromisoformat(dts)
    iso_ms = dt.isoformat(timespec='milliseconds')
    return (re.sub('\+.+','', iso_ms) + 'Z')

