from rest_framework import serializers

from MHacks.v1.util import to_utc_epoch


class UnixEpochDateField(serializers.DateTimeField):
    def to_internal_value(self, value):
        from datetime import datetime

        try:
            val = float(value)
            if val < 0:
                raise ValueError
            date = datetime.fromtimestamp(val)
            from pytz import utc

            date = date.replace(tzinfo=utc)
            return date
        except ValueError:
            self.fail('invalid', format='Unix Epoch Timestamp')

    def to_representation(self, value):
        import datetime

        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            self.fail('date')
        dt = to_utc_epoch(value)
        if not dt:
            self.fail('invalid', format='Unix Epoch Timestamp')
        return dt


class DurationInSecondsField(serializers.Field):
    error_messages = {'invalid': 'Invalid format expected duration in seconds'}

    def to_internal_value(self, data):
        from datetime import timedelta

        try:
            return timedelta(seconds=int(data))
        except ValueError:
            self.fail('invalid')

    def to_representation(self, value):
        return value.total_seconds()
