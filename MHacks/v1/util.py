from rest_framework.permissions import DjangoModelPermissions, IsAuthenticatedOrReadOnly
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import exception_handler


from MHacks.v1.serializers.util import now_as_utc_epoch, parse_date_last_updated


class GenericListCreateModel(CreateAPIView, ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def __init__(self):
        self.date_of_update = None
        super(GenericListCreateModel, self).__init__()

    def get_queryset(self):
        self.date_of_update = now_as_utc_epoch()
        return parse_date_last_updated(self.request)

    def list(self, request, *args, **kwargs):
        response = super(GenericListCreateModel, self).list(request, *args, **kwargs)
        response.data = {'results': response.data, 'date_updated': self.date_of_update}
        return response

    # noinspection PyProtectedMember
    def create(self, request, *args, **kwargs):
        if hasattr(self, 'get_queryset'):
            queryset = self.get_queryset()
        else:
            queryset = getattr(self, 'queryset', None)

        assert queryset is not None, (
            'Cannot have a GenericListModel with no '
            '`.queryset` or not have defined the `.get_queryset()` method.'
        )
        model_class = queryset.model

        request.data['approved'] = request.user.has_perm('%(app_label)s.change_%(model_name)s' %
                                                         {'app_label': model_class._meta.app_label,
                                                          'model_name': model_class._meta.model_name})

        return super(GenericListCreateModel, self).create(request, *args, **kwargs)


class GenericUpdateDestroyModel(RetrieveUpdateDestroyAPIView):
    permission_classes = (DjangoModelPermissions,)
    lookup_field = 'id'


def mhacks_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if not response:
        return response

    if not response.data.get('detail', None):
        if len(response.data) == 0:
            response.data = {'detail': 'Unknown error'}
        elif isinstance(response.data, list):
            response.data = {'detail': response.data[0]}
        elif isinstance(response.data, dict):
            first_key = response.data.keys()[0]
            detail_for_key = response.data[first_key]
            if isinstance(detail_for_key, list):
                detail_for_key = detail_for_key[0]
            if first_key.lower() == 'non_field_errors':
                response.data = {'detail': "{}".format(detail_for_key)}
            else:
                response.data = {'detail': "{}: {}".format(first_key.title(), detail_for_key)}
        else:
            response.data = {'detail': 'Unknown error'}
    return response
