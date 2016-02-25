import datetime

#格式化时间戳
def stamp_format(stamp):
    return datetime.datetime.fromtimestamp(
        int(stamp)).strftime('%Y-%m-%d %H:%M:%S')

def str_to_time(str):
    return datetime.datetime.strptime(str,'%Y-%m-%d %H:%M:%S')
