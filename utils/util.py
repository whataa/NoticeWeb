import datetime


# 格式化时间戳
def stamp_format(stamp):
    return datetime.datetime.fromtimestamp(
        int(stamp)).strftime('%Y-%m-%d %H:%M:%S')


# 字符串格式化
def str_to_time(str):
    return datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')


# 日期转化为完整时间
def date_to_time(str):
    str += ' 00:00:00'
    return str_to_time(str)


# 从附件url中得到类型
def get_filetype(url):
    return url.split('.')[-1]

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    return obj

def get_cur_time():
    import time
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

print(get_cur_time())