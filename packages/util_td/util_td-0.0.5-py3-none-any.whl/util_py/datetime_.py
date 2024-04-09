from datetime import datetime
import string
from dateutil.parser import parse
import pytz

DATETIME_TPL = '%Y-%m-%d %H:%M:%S'
DATE_TPL = '%Y-%m-%d 00:00:00'
LOG_TPL = '%Y%m%d_%H%M%S' # 日志字符串模板

def dt_to_str(time, tpl=DATETIME_TPL):
    if isinstance(time, datetime):
        return time.strftime(tpl)
    elif isinstance(time, str):
        return parse(time).strftime(tpl)
    else:
        return time

#dt_str = dt_to_mq(datetime.now())
#dt_str = dt_to_mq('2022-04-14')

def get_date_str(time):
    return dt_to_str(time, DATE_TPL)

def get_tz(tz_str=''):
    return pytz.timezone(tz_str or 'PRC')

def now(tz=None):
    if not tz:
        tz = get_tz()
    return datetime.now(tz)

def get_utcoffset(dt=None, tz=None):
    if not dt:
        dt = now()
    if tz:
        dt = dt.astimezone(tz)
    zstr = dt.strftime('%z')
    return int(zstr[:3])

# 获取时间对应的取整时间戳
def get_ts_int(dt=None, internal=60):
    if not dt:
        dt = now()
    
    ts = dt.timestamp()

    
    ts_int = int(ts / internal) * internal 

    # 由于时间戳是针对utc时间，所以跨日取整需要调整为相应时区的时间戳，即减去offset的秒数
    if internal >= 86400:
        offset = get_utcoffset(dt)
        ts_int -= offset * 3600
    
    return ts_int
