from MHacks.models import Ticket as TicketModel
from MHacks.v1.serializers import TicketSerializer
from MHacks.v1.util import GenericListCreateModel, GenericUpdateDestroyModel


class Tickets(GenericListCreateModel):
    """
    Tickets are used to facilitate the mentorship process.
    """
    serializer_class = TicketSerializer
    query_set = TicketModel.objects.none()

    #TODO allow for parameters like get all tickets by a certain user
    def get_queryset(self):
        date_last_updated = super(Tickets, self).get_queryset()
        if date_last_updated:
            return TicketModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            return TicketModel.objects.all().filter(deleted=False)


class Ticket(GenericUpdateDestroyModel):
    serializer_class = TicketSerializer
    queryset = TicketModel.objects.all()
