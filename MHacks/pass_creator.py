from config.settings import APPLE_WALLET_PASSPHRASE, STATICFILES_DIRS
from passbook.models import Pass, Barcode, EventTicket, BarcodeFormat, Alignment, Field
from models import Application, Registration


def create_apple_pass(user):
    card_info = EventTicket()
    header_field = Field('date', 'Oct 7-9', 'MASONIC TEMPLE')
    header_field.textAlignment = Alignment.RIGHT
    card_info.headerFields.append(header_field)
    card_info.addPrimaryField('name', user.get_full_name(), 'HACKER')
    card_info.addBackField('name', user.get_full_name(), 'NAME')
    card_info.addBackField('email', user.email, 'EMAIL')

    try:
        app = Application.objects.get(user=user, deleted=False)
        school_name = app.school
        from datetime import date
        if app.user_is_minor():
            card_info.addAuxiliaryField('minor', 'YES', 'MINOR')
            card_info.addBackField('minor', 'YES', 'MINOR')
    except Application.DoesNotExist:
        school_name = 'Unknown'

    card_info.addSecondaryField('school', school_name, 'SCHOOL')
    card_info.addBackField('school', school_name, 'SCHOOL')

    try:
        registration = Registration.objects.get(user=user, deleted=False)
        card_info.addBackField('tshirt', registration.t_shirt_size, 'T-SHIRT SIZE')
        card_info.addBackField('dietary', registration.dietary_restrictions if registration.dietary_restrictions else 'None', 'DIETARY RESTRICTIONS')
    except Registration.DoesNotExist:
        pass

    pass_file = Pass(card_info, passTypeIdentifier='pass.com.MPowered.MHacks.UserPass',
                     organizationName='MHacks', teamIdentifier='478C74MJ7T')
    pass_file.description = 'MHacks Ticket'
    pass_file.serialNumber = str(user.pk)
    pass_file.barcode = Barcode(message=user.email, format=BarcodeFormat.QR)
    pass_file.backgroundColor = 'rgb(0, 188, 212)'
    pass_file.foregroundColor = 'rgb(250, 250, 250)'
    pass_file.labelColor = 'rgba(0, 0, 0, 0.6)'
    pass_file.associatedStoreIdentifiers = [955659359]

    pass_file.relevantDate = "2016-10-07T17:00:00-04:00"
    pass_file.locations = [{'longitude': 42.3415958, 'latitude': -83.0606906}]

    # Including the icon is necessary for the passbook to be valid.
    pass_file.addFile('icon.png', open(STATICFILES_DIRS[0] + '/assets/app_icon.png', 'r'))
    pass_file.addFile('logo.png', open(STATICFILES_DIRS[0] + '/assets/apple_pass_logo.png', 'r'))

    # Create and return the Passbook file (.pkpass)
    return pass_file.create('config/apple_wallet_certificate.pem',
                            'config/apple_wallet_key.pem',
                            'config/apple_wallet_wwdr.pem',
                            APPLE_WALLET_PASSPHRASE)
