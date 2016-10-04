from django.db.models.query import QuerySet


class MHacksQuerySet(QuerySet):
    def delete(self):
        """
        Marks as deleted in the current QuerySet instead of actually deleting the items.
        """
        assert self.query.can_filter(), "Cannot use 'limit' or 'offset' with delete."

        if self._fields is not None:
            raise TypeError("Cannot call delete() after .values() or .values_list()")
        from datetime import datetime
        from pytz import utc
        return self.update(deleted=True, last_updated=datetime.now(tz=utc))
