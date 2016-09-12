from collections import OrderedDict


# TODO documentation
class GroupEnum(object):
    HACKER = 'hacker'
    SPONSOR = 'sponsor'
    APP_READER = 'application_reader'
    STATS = 'stats_team'

groups = GroupEnum()

# map from enum to codenames of permissions that they should have
# codenames should all be in form of [add/delete/change]_[model_name]

_permissions_tuples = (
    (GroupEnum.HACKER, ('add_application',
                        'change_application')),

    (GroupEnum.SPONSOR, ('add_announcement',
                         'add_event')),

    (GroupEnum.APP_READER, ('add_application',
                            'change_application',
                            'delete_application',)),

    (GroupEnum.STATS, ())
)

permissions_map = OrderedDict(_permissions_tuples)
