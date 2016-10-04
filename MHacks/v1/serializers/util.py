from rest_framework import serializers


class UnixEpochDateField(serializers.DateTimeField):
    def to_internal_value(self, value):
        from datetime import datetime
        from pytz import utc
        try:
            return datetime.utcfromtimestamp(float(value)).replace(tzinfo=utc)
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


class NonNullPrimaryKeyField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        if not value:
            return None
        return super(NonNullPrimaryKeyField, self).to_representation(value)


def parse_date_last_updated(request):
    date_last_updated_raw = request.query_params.get('since', None)
    if date_last_updated_raw:
        try:
            from pytz import utc
            from datetime import datetime
            return datetime.utcfromtimestamp(float(date_last_updated_raw)).replace(tzinfo=utc)
        except ValueError:
            print('Value error')
            pass
    return None


def now_as_utc_epoch():
    import pytz
    from datetime import datetime
    return to_utc_epoch(datetime.now(pytz.utc))


def to_utc_epoch(date_time):
    from datetime import datetime

    if isinstance(date_time, datetime):
        import pytz
        date_time = date_time.astimezone(pytz.utc)
        from calendar import timegm
        return timegm(date_time.timetuple())
    return None
