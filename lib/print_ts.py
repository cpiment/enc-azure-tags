import datetime

def print_ts(*arg, **kwarg):
    timestamp = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S%z]')
    print(timestamp, *arg, **kwarg)