from datetime import datetime, timedelta
from dateutil.parser import parse
import pytz
from microservices_common.exceptions import IncorrectParameterFormat


class DateTimeUtil:

    @classmethod
    def to_date_tz(cls, s):
        format = '%Y-%m-%dT%H:%M:%S%z'
        return datetime.strptime(s, format)

    @classmethod
    def to_date_utc(cls, s):
        format = '%Y-%m-%dT%H:%M:%S'
        return datetime.strptime(s, format)

    @classmethod
    def to_date_utc_db(cls, s):
        splitted = s.split('.')
        format = '%Y-%m-%dT%H:%M:%S'
        return datetime.strptime(splitted[0], format)

    @classmethod
    def to_date(cls, s):
        try:
            return cls.to_date_tz(s)
        except:
            try:
                return cls.to_date_utc(s)
            except:
                return cls.to_date_utc_db(s)

    @classmethod
    def to_date_isoformat(cls, s):
        return cls.to_date(s).isoformat()

    @classmethod
    def parse_datetime(cls, iso_str):
        if iso_str and (' ' in iso_str):
            raise IncorrectParameterFormat(
                'Incorrect format of datetime: "%s". '
                'Whitespace was found, which means an error exists. '
                'Be sure that you properly url-encode character "+", '
                'by replacing it with "%%2B"' % iso_str)
        try:
            return (iso_str and parse(iso_str)) or None
        except ValueError:
            raise IncorrectParameterFormat(
                'Unable to parse datetime: "%s". Expected format is ISO-8601' % iso_str)

    @classmethod
    def convert_to_utc(cls, datetime_with_tzinfo):
        if not datetime_with_tzinfo:
            return None, None

        utcoffset = datetime_with_tzinfo.utcoffset() or timedelta(0)
        dt_in_utc = datetime_with_tzinfo - utcoffset
        dt_in_utc = dt_in_utc.replace(tzinfo=None)
        return dt_in_utc, utcoffset

    @classmethod
    def convert_to_local_iso_str(cls, datetime, timezone):
        return datetime.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))

    @classmethod
    def convert_validation_datetime_to_utc(cls, _datetime):
        parsed_datetime = cls.parse_datetime(_datetime.isoformat())
        dt_in_utc, utcoffset = cls.convert_to_utc(parsed_datetime)

        return parsed_datetime, dt_in_utc, utcoffset

    @classmethod
    def convert_validation_datetime_to_utc_iso_str(cls, _datetime):
        parsed_datetime, dt_in_utc, utcoffset = cls.convert_validation_datetime_to_utc(
            _datetime)
        return dt_in_utc.isoformat()

    @classmethod
    def convert_str_to_utc(cls, _datetime):
        parsed_datetime = cls.parse_datetime(_datetime)
        dt_in_utc, utcoffset = cls.convert_to_utc(parsed_datetime)

        return dt_in_utc
