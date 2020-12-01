# coding=utf-8

from datetime import datetime, timedelta
from weixin.cache import weather_cache
from weixin.utils.httpclient import HttpClient
from weixin.utils.constants import LunarConfig, WEEKDAY_MAP


class LunarDate(object):

    API_URL = 'http://v.juhe.cn/calendar/day'
    API_KEY = '53fb358b92abe89bf5c4edb3db993829'
    _HTTP_CLIENT = None

    def __init__(self):
        self._HTTP_CLIENT = HttpClient()

    def get_lunar(self, date_str):
        lunar_info = weather_cache.get_lunar_date(date_str)
        if lunar_info:
            return lunar_info
        # resp_data = self.get_lunar_api(date_str)
        # lunar_data = resp_data.get("data")
        # lunar_year = lunar_data.get("lunarYear")
        # lunar_date = lunar_data.get("lunar")
        # weekday = lunar_data.get("weekday")
        # lunar_info = "\n".join([lunar_year, lunar_date, weekday])
        date_list = date_str.split('-')
        lunar_info = lunar_converter.get_lunar_info(
            date_list[0], date_list[1], date_list[2])
        weather_cache.cache_lunar_date(date_str, lunar_info)
        return lunar_info

    def get_lunar_api(self, date_str):
        params = {
            'date': date_str,
            'key': self.API_KEY}
        resp = self._HTTP_CLIENT.get(
            url=self.API_URL,
            params=params)
        return resp.get("result")


class LunarDateV2(object):

    def __init__(self):
        self.lunar_constants = LunarConfig.LUNAR_CONSTANTS
        self.solar_lunar_map = LunarConfig.LUNAR_SOLAR_MAP

    def get_lunar_info(self, year, month, day):
        '''
        获取阴历日期

        Parameters:
            year    --- 年份
            month   --- 月份
            day     --- 日期
        Return:
            阴历年份, 如 甲申年\n十月初三\n星期三
        '''
        year = int(year)
        month = int(month)
        day = int(day)
        lunar_date, is_leap = self.solar2lunar(year, month, day)
        date_list = lunar_date.split('-')
        lunar_year = date_list[0]
        diff = int(lunar_year) - LunarConfig.LUNAR_FIRST
        tian = LunarConfig.LUNAR_TIAN[diff % 10]
        di = LunarConfig.LUNAR_DIZHI[diff % 12]
        year_str = tian + di + u'年'
        date_str = self.get_lunar_date(year, month, day)
        date_time = datetime(year, month, day)
        day_str = u'星期' + WEEKDAY_MAP[date_time.weekday()]
        return '\n'.join([year_str, date_str, day_str])

    def get_term_date(self, year, times):
        '''
        获取节气日期

        Parameters:
            year  -- 哪一年。如， 2019
            times -- 一年中第几个节气，从小寒开始， 如1， 2
        Return:
            节气的日期， 如 06-12
        '''
        if year - LunarConfig.YEAR_STAR_TERM < 0 or \
                year - LunarConfig.YEAR_STAR_TERM > 200:
            return ''
        if times > 24 or times <= 0:
            return ''
        term_info = LunarConfig.TERMS_YEAR[
            year - LunarConfig.YEAR_STAR_TERM]
        term_list = []
        for i in range(6):
            term_list.append(term_info[i * 5: (i + 1) * 5])
        term_table = []
        for term in term_list:
            tmp = self._split_term(term)
            term_table.extend(tmp)
        day = str(term_table[times - 1])
        month = times / 2 if times % 2 == 0 else (times + 1) / 2
        month = str(month)
        month = '0' + month if len(month) == 1 else month
        day = '0' + day if len(day) == 1 else day
        return '{}-{}'.format(month, day)

    def _split_term(self, sterm_info):
        sterm_info = '0x' + sterm_info
        sterm_info = str(int(sterm_info, 16))
        return [
            int(sterm_info[0: 1]), int(sterm_info[1: 3]),
            int(sterm_info[3: 4]), int(sterm_info[4: 6])]

    def solar2lunar(self, year, month, day):
        '''
        solar date str to lunar date str

        Parameters:
            year  --- 年
            month --- 月
            day   --- 日
        Return:
            return the lunar date str if ok
            such as, 2019-06-12(阴历)
            else return ''
        '''
        year = int(year)
        if year - LunarConfig.YEAR_START < 0 or \
                year - LunarConfig.YEAR_START > 198:
            return ''
        date_datetime = datetime(int(year), int(month), int(day))
        lunar_map = self.solar_lunar_map[year - LunarConfig.YEAR_START]
        lunar_start_day = lunar_map & 0x1F
        lunar_start_month = (lunar_map >> 5) & 0x3
        solar_datetime = datetime(year, lunar_start_month, lunar_start_day)
        diff = (date_datetime - solar_datetime).days
        lunar_year = year
        lunar_month = 1
        lunar_day = 1
        is_leap = 0
        if diff >= 0:
            leap_days, month_days = self._lunar_month_days(
                lunar_year, lunar_month)
            while diff >= month_days:
                if not leap_days:
                    is_leap = 0
                else:
                    is_leap = 1
                    diff -= leap_days
                lunar_month += 1
                diff -= month_days
                leap_days, month_days = self._lunar_month_days(
                    year, lunar_month)
            lunar_day += diff
        else:
            lunar_year -= 1
            lunar_month = 12
            leap_days, month_days = self._lunar_month_days(
                lunar_year, lunar_month)
            while abs(diff) >= month_days:
                if not leap_days:
                    is_leap = 0
                else:
                    is_leap = 1
                    diff += leap_days
                lunar_month -= 1
                diff += month_days
                leap_days, month_days = self._lunar_month_days(
                    lunar_year, lunar_month)
            lunar_day += diff + month_days
        return "{}-{}-{}".format(lunar_year, lunar_month, lunar_day), is_leap

    def get_lunar_date(self, year, month, day):
        '''
        get lunar date today

        Return:
            return the lunar date
            if is holiday lunar/solar/节气 return holiday name
        '''
        lunar_date, is_leap = self.solar2lunar(year, month, day)
        holiday_name = is_holiday(lunar_date, LunarConfig.LUNAR_HOLIDAY)
        if holiday_name:
            return holiday_name
        date_time = datetime(year, month, day)
        solar_date_str = date_time.strftime('%Y-%m-%d')
        holiday_name = is_holiday(solar_date_str, LunarConfig.SOLAR_HOLIDAY)
        if holiday_name:
            return holiday_name
        dest_date_str = date_time.strftime('%m-%d')
        date_str = self.get_term_date(year, 2 * month)
        if dest_date_str == date_str:
            return LunarConfig.TERMS_LIST[2 * month - 1]
        date_str = self.get_term_date(year, 2 * month - 1)
        if dest_date_str == date_str:
            return LunarConfig.TERMS_LIST[2 * month - 2]
        lunar_date_str = ''
        lunar_month = int(lunar_date.split('-')[1])
        lunar_day = int(lunar_date.split('-')[2])
        lunar_date_str += LunarConfig.LUNAR_MONTH[lunar_month - 1] + u'月'
        left = lunar_day % 10
        left = left if left != 0 else 10
        if lunar_day <= 10:
            lunar_date_str += u'初'
        elif lunar_day > 10 and lunar_day < 20:
            lunar_date_str += u'十'
        elif lunar_day == 20:
            pass
        elif lunar_day > 20 and lunar_day < 30:
            lunar_date_str += u'廿'
        else:
            lunar_date_str += u'三'
        if lunar_day != 20:
            lunar_date_str += LunarConfig.LUNAR_DAY[left - 1]
        else:
            lunar_date_str += u'二十'
        return lunar_date_str

    def lunar2solar(self, year, month, day, is_leap=0):
        '''
        lunar date str to solar date str

        Parameters:
            year  --- 年
            month --- 月
            day   --- 日
        Return:
            return the solar date str
            such as, 2019-06-12
        '''
        year = int(year)
        month = int(month)
        day = int(day)
        if is_leap:
            leap_month_days, month_days = self._lunar_month_days(year, month)
            if not leap_month_days:
                return ''
        # 下一年元旦的阴历日期
        solar_start, leap = self.solar2lunar(year + 1, 1, 1)
        lunar_date_list = solar_start.split('-')
        solar_lunar_month = int(lunar_date_list[1])
        solar_lunar_day = int(lunar_date_list[2])
        start_date = datetime(year + 1, 1, 1)
        if solar_lunar_month == month and solar_lunar_day == day:
            if is_leap and leap or (not is_leap and not leap):
                return '{}-{}-{}'.format(year + 1, '01', '01')
        leap_month_days, month_days = self._lunar_month_days(year, month)
        diff = (month_days - solar_lunar_day + 1) + day - 1
        if is_leap:
            start_date += timedelta(diff)
            return start_date.strftime('%Y-%m-%d')
        elif not is_leap:
            start_date -= timedelta(diff)
            return start_date.strftime('%Y-%m-%d')
        first = 1
        diff = 0
        # 阴历日期在当年
        if solar_lunar_month > month or \
                (solar_lunar_month == month and solar_lunar_day > day):
            while solar_lunar_month >= month:
                if first:
                    diff += (solar_lunar_day)
                    solar_lunar_month -= 1
                    first = 0
                    continue
                leap_month_days, month_days = self._lunar_month_days(
                    year, solar_lunar_month)
                if leap_month_days:
                    diff += leap_month_days
                diff += month_days
                solar_lunar_month -= 1
            diff -= (day)
            result = (start_date - timedelta(diff)).strftime('%Y-%m-%d')
        # 阴历日期在下一年
        elif solar_lunar_month < month or \
                (solar_lunar_month == month and solar_lunar_day < day):
            month_days = 0
            while solar_lunar_month <= month:
                if first:
                    leap_month_days, month_days = self._lunar_month_days(
                        year, solar_lunar_month)
                    diff += (month_days - solar_lunar_day + 1)
                    if leap_month_days:
                        diff += leap_month_days
                    first = 0
                    solar_lunar_month += 1
                    continue
                leap_month_days, month_days = self._lunar_month_days(
                    year, solar_lunar_month)
                diff += month_days
                if leap_month_days:
                    diff += leap_month_days
                solar_lunar_month += 1
                diff -= (month_days - day + 1)
            result = (start_date + timedelta(diff)).strftime('%Y-%m-%d')
        return result

    def _lunar_month_days(self, year, month):
        '''
        lunar month days

        Parameters:
            year     -- 阴历年
            month.   -- 阴历月

        Return:
            tuple of leap month days and the days of this month
        '''
        lunar_info = self.lunar_constants[year - LunarConfig.YEAR_START]
        leap_month = (lunar_info >> 13) & 0xF
        leap_days = (lunar_info >> 12) & 0x1
        leap_days = 29 if leap_days == 0 else 30
        month_days = 30 if lunar_info >> (month - 1) & 1 else 29
        if leap_month == month:
            return leap_days, month_days
        return 0, month_days


def is_holiday(date_str, date_dict):
    holiday_name = ''
    year = int(date_str.split('-')[0])
    date_str = '-'.join(date_str.split('-')[1:])
    for holiday_date_str, name in date_dict.items():
        start_year = 0
        if len(holiday_date_str.split('-')) == 3:
            start_year = int(holiday_date_str.split('-')[0])
            holiday_date_str = '-'.join(holiday_date_str.split('-')[1:])
        if holiday_date_str == date_str:
            holiday_name = name
            if start_year:
                holiday_name += u' {}周年'.format(year - start_year)
            break
    return holiday_name


lunar_converter = LunarDateV2()
OPEN_API_CLIENT = LunarDate()


if __name__ == '__main__':
    # lunar_obj = LunarDate()
    # print lunar_obj.get_lunar_api('2018-9-12')
    print lunar_converter.lunar2solar(2019, 1, 10)
