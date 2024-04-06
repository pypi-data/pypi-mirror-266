from calendar import monthrange
from datetime import date, datetime, timedelta

DEFAULT_DATE_FORMAT = '%Y-%m-%d'


def to_edate(date: date | datetime):
    return EDate(date.year, date.month, date.day)


class EDate(date):
    def datetime(self):
        return datetime(self.year, self.month, self.day)

    def tomorrow(self):
        return to_edate(self.datetime() + timedelta(days=1))

    def yesterday(self):
        return to_edate(self.datetime() - timedelta(days=1))

    def first_day_of_month(self):
        return self.replace(day=1)

    def first_day_of_year(self):
        return self.replace(day=1, month=1)

    def last_day_of_month(self):
        day1, ndays = monthrange(self.year, self.month)
        return self.replace(day=ndays)

    def last_day_of_year(self):
        return self.replace(day=31, month=12)

    def first_day_of_last_month(self):
        return self.replace(day=1).yesterday().replace(day=1)

    def first_day_of_last_year(self):
        return self.replace(day=1, month=1, year=self.year - 1)

    def last_day_of_last_month(self):
        return self.replace(day=1).yesterday()

    def last_day_of_last_year(self):
        return self.replace(day=31, month=12, year=self.year - 1)

    def strftime(self, __format=DEFAULT_DATE_FORMAT):
        return super().strftime(__format)

    @staticmethod
    def strptime(__date_string: str, __format=DEFAULT_DATE_FORMAT):
        return to_edate(datetime.strptime(__date_string, __format))

    def __str__(self):
        return self.strftime()
