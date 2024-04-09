from datetime import datetime, date as datetimedate, time as datetimetime


class Dater:
    __timezone__ = "UTC"

    def get_new_date(self, _datetime=None):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        import pendulum

        if not _datetime:
            return pendulum.now(tz=self.__timezone__)
        elif isinstance(_datetime, str):
            return pendulum.parse(_datetime, tz=self.__timezone__)
        elif isinstance(_datetime, datetime):
            return pendulum.instance(_datetime, tz=self.__timezone__)
        elif isinstance(_datetime, datetimedate):
            return pendulum.datetime(
                _datetime.year, _datetime.month, _datetime.day, tz=self.__timezone__
            )
        elif isinstance(_datetime, datetimetime):
            return pendulum.parse(
                f"{_datetime.hour}:{_datetime.minute}:{_datetime.second}",
                tz=self.__timezone__,
            )

        return pendulum.instance(_datetime, tz=self.__timezone__)

    def get_new_datetime_string(self, _datetime=None):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        return self.get_new_date(_datetime).to_datetime_string()
