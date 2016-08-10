from django import forms
from django.forms import widgets
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


from models import MHacksUser, Application


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254)
    password = forms.CharField(label='Password', max_length=128, strip=False, widget=forms.PasswordInput)
    password.longest = True

    def confirm_login_allowed(self, user):
        if not user.email_verified:
            error = forms.ValidationError('Email not verified.', code='unverified')
            error.user_pk = urlsafe_base64_encode(force_bytes(user.pk))
            raise error
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password2'].label = "Confirm Password"
        self.fields['password2'].longest = True

    class Meta:
        model = MHacksUser
        fields = ('first_name', 'last_name', "email",)


class ApplicationForm(forms.ModelForm):
    def save(self, commit=True):
        # override the save to db if necessary
        pass

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['school'].cols = 10
        self.fields['is_high_school'].cols = 2
        self.fields['is_high_school'].end_row = True
        self.fields['birthday'].end_row = True

        self.fields['major'].end_row = True
        self.fields['grad_year'].end_row = True

        self.fields['race'].cols = 6
        self.fields['gender'].cols = 6
        self.fields['birthday'].demographic = True
        self.fields['race'].previous = True


        self.fields['github'].cols = 6
        self.fields['devpost'].cols = 6
        self.fields['devpost'].end_row = True

        self.fields['personal_page'].cols = 6
        self.fields['resume'].cols = 6
        self.fields['resume'].end_row = True

        self.fields['num_hackathons'].cols = 6
        self.fields['hack_link'].cols = 6
        self.fields['hack_link'].end_row = True
        self.fields['hack_explanation'].interests = True

        self.fields['cortex'].short = True



    class Meta:
        model = Application
        exclude = ['user', 'deleted', 'score', 'reimbursement', 'submitted']  # use all fields except for these
        labels = {
            'school': 'School or University',
            'grad_year': 'Expected graduation year',
            'dob': 'Date of birth',
            'is_high_school': 'Are you in high school?',
            'github':'',
            'devpost':'',
            'personal_page':'',
            'needs_reimbursement': 'Will you be needing travel reimbursement to attend MHacks?',
            'cortex': '',
            'passionate': 'What\'s something that you made that you\'re proud of (it doesn\'t have to be a hack)? (150 words max)',
            'coolest_thing': 'What would you build if you had access to all the resources you needed? (150 words max)',
            'other_info': 'Anything else you want to tell us?',
            'num_hackathons': 'How many hackathons have you attended? (Put 0 if this is your first!)',
            'can_pay': 'How much of the travel costs can you pay?',
            'city': 'Which city will you be traveling from?',
            'state': 'Which state will you be traveling from?',
            'mentoring': 'Are you interested in mentoring other hackers?'

        }

        widgets = {
            'dob': forms.TextInput(attrs={'placeholder': 'DD/MM/YYYY', 'class': 'form-control input-md'}),
            'grad_year': forms.TextInput(attrs={'placeholder': 'YYYY', 'class': 'form-control input-md'}),
            'birthday': forms.TextInput(attrs={'placeholder': 'DD/MM/YYYY', 'class': 'form-control input-md'}),
            'cortex': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline checkbox-style'}),
            'school': forms.Select(attrs={'class': 'select_style'}),
            'major': forms.Select(attrs={'class': 'select_style'}),
            'gender': forms.Select(attrs={'class': 'select_style'}),
            'race': forms.Select(attrs={'class': 'select_style'}),
            'github': forms.TextInput(attrs={'placeholder': 'Github', 'class': 'form-control input-md'}),
            'devpost': forms.TextInput(attrs={'placeholder': 'Devpost', 'class': 'form-control input-md'}),
            'personal_page': forms.TextInput(attrs={'placeholder': 'Personal Website', 'class': 'form-control input-md'}),
            'other_info': forms.Textarea(attrs={'class': 'textfield form-control'}),
            'coolest_thing': forms.Textarea(attrs={'class': 'textfield form-control'}),
            'passionate': forms.Textarea(attrs={'class': 'textfield form-control'}),
            'hack_explanation': forms.Textarea(attrs={'class': 'textfield form-control'}),
            'resume': forms.FileInput(attrs={'class': 'input-md form-control'})

        }
