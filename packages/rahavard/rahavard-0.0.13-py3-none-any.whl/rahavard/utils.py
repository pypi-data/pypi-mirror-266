from django.http import HttpResponse

from math import floor, log as math_log, pow as math_pow
from os import path, listdir, getenv
from re import match, sub
from uuid import uuid4

from convert_numbers import english_to_persian
from jdatetime import datetime as jdt
from natsort import natsorted

import jdatetime


JALALI_FORMAT = '%A %H %M %S %d %m %Y'


def calculate_offset(page_number, limit_to_show):
    return (page_number - 1) * limit_to_show  ## 0/25/etc.


def comes_from_htmx(request):
    return 'HX-Request' in request.headers

## https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
def convert_byte(size_in_bytes, to_persian=False):
    if (size_in_bytes == 0):
        if to_persian:
            return '. بایت'
        return '0B'

    if to_persian:
        suff = [
            'بایت', 'کیلوبایت', 'مگابایت', 'گیگابایت', 'ترابایت',
            'پتابایت', 'اگزابایت', 'زتابایت', 'یوتابایت',
        ]
    else:
        suff = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    i = int(floor(math_log(size_in_bytes, 1024)))
    p = math_pow(1024, i)
    conv = f'{float(size_in_bytes / p):.1f}'

    ## remove trailing .0 or .00
    reg = '^[0-9]+\.0+$'
    if match(reg, conv):
        conv = sub('\.0+$', '', conv)

    if to_persian:
        return f'{persianize(conv)} {suff[i]}'

    return f'{conv}{suff[i]}'


def convert_millisecond(ms, verbose=True):
    ## the input is in milliseconds
    ## so, first it should be converted to seconds (by /1000)
    second = ms / 1000

    return convert_second(second, verbose=verbose)


def convert_second(seconds, verbose=True):
    seconds = int(seconds)

    if seconds == 0:
        if verbose:
            return '0'
        else:
            return '0:00'

    if seconds < 1:
        if verbose:
            return '~0'
        else:
            return '~0:00'

    ss = f'{int(seconds % 60):02}'
    mi = f'{int(seconds / 60 % 60):02}'
    hh = f'{int(seconds / 3600 % 24):02}'
    dd = f'{int(seconds / 3600 / 24 % 30):02}'
    mo = f'{int(seconds / 3600 / 24 / 30 % 12):02}'
    yy = f'{int(seconds / 3600 / 24 / 30 / 12):02}'

    if yy == '00' and mo == '00' and dd == '00':
        if verbose: result = f'{hh} hrs, {mi} mins and {ss} secs'
        else:       result = f'{hh}:{mi}:{ss}'
    elif yy == '00' and mo == '00':
        if verbose: result = f'{dd} days, {hh} hrs and {mi} mins'
        else:       result = f'{dd}:{hh}:{mi}:{ss}'
    elif yy == '00':
        if verbose: result = f'{mo} months, {dd} days and {hh} hrs'
        else:       result = f'{mo}:{dd}:{hh}:{mi}:{ss}'
    else:
        if verbose: result = f'{yy} years, {mo} months and {dd} days'
        else:       result = f'{yy}:{mo}:{dd}:{hh}:{mi}:{ss}'

    if verbose:
        ## remove items whose values are 00, and adjust comma and 'and'
        result = sub(r'00 [a-z]+s, ', r'', result)
        result = sub(r'00 [a-z]+s and ', r'', result)
        result = sub(r'00 [a-z]+s$', r'', result)
        result = sub(r', ([0-9][0-9] [a-z]+s )', r' and \1', result)
        result = sub(r'and 00 [a-z]+s ', r'', result)
        result = sub(r' and $', r'', result)
        result = sub(r', ([0-9][0-9] [a-z]+)$', r' and \1', result)
        result = sub(r' and ([0-9][0-9] [a-z]+) and', r', \1 and', result)
        result = sub(r', +$', r'', result)
        result = sub(r', ([0-9][0-9] [a-z]+s)$', r' and \1', result)

        ## remove plural s when value is 01
        result = sub(r'(01 [a-z]+)s ', r'\1 ', result)
        result = sub(r'(01 [a-z]+)s, ', r'\1, ', result)
        result = sub(r'(01 [a-z]+)s$', r'\1', result)

        result = sub(r'^0([0-9])', r'\1', result)         ## 02 days, ...       -> 2 days, ...
        result = sub(r', 0([0-9])', r', \1', result)      ## ..., 01 hour, ...  -> ..., 1 hour, ...
        result = sub(r'and 0([0-9])', r'and \1', result)  ## ... and 05 hrs ... -> ... and 5 hrs ... (this seems to be a bug in the original function)

    else:
        result = sub(r'^0+:0([0-9]):', r'\1:', result)          ## 0:00:12 -> 0:12
                                                                ## 0:08:12 -> 8:12
        result = sub(r'^0+:([1-9])([0-9]):', r'\1\2:', result)  ## 0:10:12 -> 10:12

    return result


def convert_timestamp_to_jalali(tmstmp=None):
    '''
    takes timestamp, e.g. 1682598113
    and converts it to jalali in this format: چهارشنبه ۰۷:۰۶:۳۳ ۳۰-/۰۱/۱۴۰۲
    '''

    if not tmstmp:
        return ''

    jdatetime.set_locale('fa_IR')

    jalali_object = jdt.fromtimestamp(int(tmstmp))
    w, h, mi, s, d, mo, y = jalali_object.strftime(JALALI_FORMAT).split()

    return f'{w} {english_to_persian(h)}:{english_to_persian(mi)}:{english_to_persian(s)} {english_to_persian(y)}/{english_to_persian(mo)}/{english_to_persian(d)}'


def convert_to_jalali(gregorian_object=None):
    '''
    takes gregorian object, like self.created
    and converts it to jalali in this format: چهارشنبه ۰۷:۰۶:۳۳ ۳۰-/۰۱/۱۴۰۲
    '''

    if not gregorian_object:
        return ''

    jdatetime.set_locale('fa_IR')

    timestamp = convert_to_second(gregorian_object)

    jalali_object = jdt.fromtimestamp(timestamp)
    w, h, mi, s, d, mo, y = jalali_object.strftime(JALALI_FORMAT).split()

    return f'{w} {english_to_persian(h)}:{english_to_persian(mi)}:{english_to_persian(s)} {english_to_persian(y)}/{english_to_persian(mo)}/{english_to_persian(d)}'


def convert_to_second(date_obj):
    return int(date_obj.timestamp())  ## 1698381096


def get_list_of_files(directory, extension):
    if not path.exists(directory):
        return []
    return natsorted([
        path.abspath(path.join(directory, _))
        for _ in listdir(directory)
        if all([
            _.endswith((f'.{extension}')),  ## NOTE do NOT replace .{extension} with {extension}
            path.isfile(f'{directory}/{_}'),
        ])
    ])


def get_max_id(conn, table_name):
    return conn.execute(f'''
        SELECT MAX(id) FROM "{table_name}";
    ''').fetchone()[0] \
    or 0  ## added 'or 0' because max id may sometimes be None


def get_percent(smaller_number, total_number, to_persian=False):
    if smaller_number == 0 or total_number == 0:
        if to_persian:
            return '۰'
        return '0'

    _perc = (smaller_number * 100) / total_number

    if int(_perc) == 0:
        if to_persian:
            return '~۰'
        return '~0'

    _perc = int(_perc * 10) / 10  ## 99.95232355216523 -> 99.9
    ## NOTE we didn't use f'{_perc:.1f}'
    ##      because it turns 99.95232355216523 to 100.0

    _perc = sub('\.0+$', '', str(_perc))  ## 97.0 -> 97

    if to_persian:
        return persianize(_perc)

    return _perc


def persianize(number):
    number = str(number)
    if match('^[0-9]+\.[0-9]+$', number):
        _left, _right = number.split('.')
        if match('^0+$', _right):
            return english_to_persian(_left)
        return f'{english_to_persian(_left)}.{english_to_persian(_right[:2])}'

    return english_to_persian(int(number))


def short_uuid():
    _sample = uuid4()
    return hex(int(_sample.time_low))[2:]


def sort_dict(dictionary, based_on, reverse):
    if based_on == 'key':
        return dict(natsorted(dictionary.items(), reverse=reverse))

    if based_on == 'value':
        return dict(natsorted(dictionary.items(), key=lambda item: item[1], reverse=reverse))

    return dictionary


def to_tilda(text):
    '''/home/USERNAME/... -> ~/...'''
    return sub(getenv('HOME'), '~', text)



def get_date_time_live():
    jdatetime.set_locale('fa_IR')

    jdt_now = jdt.now()

    _year  = english_to_persian(jdt_now.strftime('%Y'))  ## ۱۴۰۱
    _day   = english_to_persian(jdt_now.strftime('%d'))  ## ۱۷
    _month = english_to_persian(jdt_now.strftime('%m'))  ## ۰۱

    _hour = english_to_persian(jdt_now.strftime('%H'))
    _min  = english_to_persian(jdt_now.strftime('%M'))
    # _sec  = english_to_persian(jdt_now.strftime('%S'))

    # _weekday = jdt_now.strftime('%A')  ## چهارشنبه

    return HttpResponse(f'{_year}/{_month}/{_day} {_hour}:{_min}')
