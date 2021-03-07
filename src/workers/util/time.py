from datetime import tzinfo, timedelta, datetime
import time as _time

ZERO = timedelta(0)
STDOFFSET = timedelta(seconds=-_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds=-_time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):
    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0

def RFC3339(delta=timedelta()):
    Local = LocalTimezone()
    d = datetime.now(Local) + delta
    return d.isoformat('T')

def now():
    return RFC3339()

def offset(seconds: int=0, minutes: int=0, hours: int=0):
    delta = timedelta(seconds=seconds, minutes=minutes, hours=hours)
    return RFC3339(delta)