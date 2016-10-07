from config.settings import APPLE_WALLET_PASSPHRASE, STATICFILES_DIRS
from passbook.models import Pass, Barcode, EventTicket, BarcodeFormat, Alignment, Field, IBeacon
import qrcode


def create_apple_pass(user):
    card_info = EventTicket()
    header_field = Field('date', 'Oct 7-9', 'MASONIC TEMPLE')
    header_field.textAlignment = Alignment.RIGHT
    card_info.headerFields.append(header_field)
    card_info.addPrimaryField('name', user.get_full_name(), 'HACKER')
    card_info.addBackField('name', user.get_full_name(), 'NAME')
    card_info.addBackField('email', user.email, 'EMAIL')

    app = user.application_or_none()

    school_name = user.cleaned_school_name(app)
    card_info.addSecondaryField('school', school_name, 'SCHOOL')
    card_info.addBackField('school', school_name, 'SCHOOL')

    if app:
        if app.user_is_minor():
            card_info.addAuxiliaryField('minor', 'YES', 'MINOR')
            card_info.addBackField('minor', 'YES', 'MINOR')

    registration = user.registration_or_none()
    if registration:
        card_info.addBackField('tshirt', registration.t_shirt_size, 'T-SHIRT SIZE')
        card_info.addBackField('dietary', registration.dietary_restrictions if registration.dietary_restrictions else 'None', 'DIETARY RESTRICTIONS')

    pass_file = Pass(card_info, passTypeIdentifier='pass.com.MPowered.MHacks.UserPass',
                     organizationName='MHacks', teamIdentifier='478C74MJ7T')
    pass_file.description = 'MHacks Ticket'
    pass_file.serialNumber = str(user.pk)
    pass_file.barcode = Barcode(message=user.email, format=BarcodeFormat.QR)
    pass_file.backgroundColor = 'rgb(0, 188, 212)'
    pass_file.foregroundColor = 'rgb(250, 250, 250)'
    pass_file.labelColor = 'rgba(0, 0, 0, 0.6)'
    pass_file.associatedStoreIdentifiers = [955659359]

    pass_file.locations = [{'longitude': 42.3415958, 'latitude': -83.0606906},
                           {'longitude': 42.3420320, 'latitude': -83.0596780},
                           {'longitude': 42.3415800, 'latitude': -83.0607620}]
    i_beacon = IBeacon('5759985C-B037-43B4-939D-D6286CE9C941', 0, 0)
    i_beacon.relevantText = 'You are near a scanner.'
    pass_file.ibeacons = [i_beacon]

    # Including the icon is necessary for the passbook to be valid.
    pass_file.addFile('icon.png', open(STATICFILES_DIRS[0] + '/assets/app_icon.png', 'r'))
    pass_file.addFile('icon@2x.png', open(STATICFILES_DIRS[0] + '/assets/app_icon.png', 'r'))
    pass_file.addFile('icon@3x.png', open(STATICFILES_DIRS[0] + '/assets/app_icon.png', 'r'))
    pass_file.addFile('logo.png', open(STATICFILES_DIRS[0] + '/assets/apple_pass_logo.png', 'r'))
    pass_file.addFile('logo@2x.png', open(STATICFILES_DIRS[0] + '/assets/apple_pass_logo.png', 'r'))
    pass_file.addFile('logo@3x.png', open(STATICFILES_DIRS[0] + '/assets/apple_pass_logo.png', 'r'))

    # Create and return the Passbook file (.pkpass)
    return pass_file.create('config/apple_wallet_certificate.pem',
                            'config/apple_wallet_key.pem',
                            'config/apple_wallet_wwdr.pem',
                            APPLE_WALLET_PASSPHRASE)


def create_qr_code_image(user):
    import StringIO
    import base64
    output = StringIO.StringIO()
    image = qrcode.make(user.email)
    image.save(output)
    return base64.b64encode(output.getvalue())
