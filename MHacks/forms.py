from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe

from MHacks.widgets import ArrayFieldSelectMultiple, MHacksAdminFileWidget
from models import MHacksUser, Application, MentorApplication, Registration
from utils import validate_url


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
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super(ApplicationForm, self).__init__(*args, **kwargs)

        self.fields['school'].cols = 12
        self.fields['is_high_school'].cols = 12
        self.fields['is_high_school'].end_row = 12
        self.fields['is_international'].cols = 12
        self.fields['is_international'].end_row = 12
        self.fields['is_high_school'].general = True

        self.fields['is_high_school'].end_row = True
        self.fields['birthday'].end_row = True

        self.fields['major'].end_row = True
        self.fields['grad_date'].end_row = True

        self.fields['race'].cols = 6
        self.fields['gender'].cols = 6
        self.fields['birthday'].demographic = True
        self.fields['race'].previous = True

        self.fields['github'].cols = 6
        self.fields['devpost'].cols = 6
        self.fields['devpost'].end_row = True

        self.fields['personal_website'].cols = 6
        self.fields['resume'].cols = 6
        self.fields['resume'].end_row = True

        self.fields['num_hackathons'].cols = 12
        self.fields['num_hackathons'].end_row = True
        self.fields['mentoring'].interests = True

        self.fields['cortex'].short = True

        self.fields['github'].required = False
        self.fields['devpost'].required = False
        self.fields['personal_website'].required = False
        self.fields['other_info'].required = False
        self.fields['gender'].required = False
        self.fields['race'].required = False

        self.fields['other_info'].travel = True

        # if the user is from UMich, exclude the short answer and reimbursement/travel fields
        if self.user and 'umich.edu' in self.user.email:
            for key in ['passionate', 'coolest_thing', 'other_info', 'needs_reimbursement', 'can_pay', 'from_city',
                        'from_state']:
                del self.fields[key]
                self.fields['cortex'].short = False

    class Meta:
        from application_lists import TECH_OPTIONS
        model = Application

        # use all fields except for these
        exclude = ['user', 'deleted', 'score', 'reimbursement', 'submitted', 'decision']

        labels = {
            'school': 'School or University',
            "grad_date": 'Expected graduation date',
            'birthday': 'Date of birth',
            'is_high_school': 'I am a high school student.',
            'is_international': 'I am an international student.',
            'github': '',
            'devpost': '',
            'personal_website': '',
            'cortex': 'CTRL/CMD + click to multi-select!',
            'passionate': 'Tell us about a project that you worked on and why you\'re proud of it. This doesn\'t have to be a hack! (150 words max)',
            'coolest_thing': 'What do you hope to take away from MHacks 8? (150 words max)',
            'other_info': 'Anything else you want to tell us?',
            'num_hackathons': 'How many hackathons have you attended? (Put 0 if this is your first!)',
            'can_pay': 'How much of the travel cost can you pay?',
            'mentoring': 'I am interested in mentoring other hackers!',
            'needs_reimbursement': 'I will be needing travel reimbursement to attend MHacks.',
            'from_city': 'Which city will you be traveling from?',
            'from_state': 'Which state or country will you be traveling from? (Type your country if you are traveling internationally)',
            'gender': 'Preferred gender pronouns',
            'resume': 'Resume (If you don\'t have a formal resume, you can upload a skills sheet, a bullet-pointed list, etc!)'
        }

        widgets = {
            "grad_date": forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY', 'id': 'graduation_date'}),
            'cortex': ArrayFieldSelectMultiple(attrs={'class': 'checkbox-inline checkbox-style textfield check-width'}, choices=TECH_OPTIONS),
            'birthday': forms.TextInput(attrs={'placeholder': 'MM/DD/YYYY'}),
            'school': forms.TextInput(attrs={'placeholder': 'Hackathon College', 'class': 'form-control input-md',
                                             'id': 'school-autocomplete'}),
            'major': forms.TextInput(attrs={'placeholder': 'Hackathon Science', 'class': 'form-control input-md',
                                            'id': 'major-autocomplete'}),
            'gender': forms.TextInput(attrs={'placeholder': 'They/Them/Theirs', 'id': 'gender-autocomplete'}),
            'race': forms.TextInput(attrs={'placeholder': 'Hacker', 'id': 'race-autocomplete'}),
            'github': forms.TextInput(attrs={'placeholder': 'GitHub', 'class': 'form-control input-md'}),
            'devpost': forms.TextInput(attrs={'placeholder': 'Devpost', 'class': 'form-control input-md'}),
            'personal_website': forms.TextInput(
                attrs={'placeholder': 'Personal Website', 'class': 'form-control input-md'}),
            'other_info': forms.Textarea(attrs={'class': 'textfield form-control'}),
            'coolest_thing': forms.Textarea(attrs={'class': 'textfield form-control'}),
            'passionate': forms.Textarea(attrs={'class': 'textfield form-control'}),
            'resume': MHacksAdminFileWidget(attrs={'class': 'input-md form-control'}),
            'from_state': forms.TextInput(attrs={'placeholder': 'State or country', 'id': 'state-autocomplete'})
        }

    # custom validator for urls
    def clean_github(self):
        data = self.cleaned_data['github']
        validate_url(data, 'github.com')
        return data

    def clean_devpost(self):
        data = self.cleaned_data['devpost']
        validate_url(data, 'devpost.com')
        return data

    def clean_major(self):
        data = self.cleaned_data['major']
        if not self.cleaned_data['is_high_school'] and not data:
            raise forms.ValidationError('Please enter your major.')
        return data

    def clean_grad_date(self):
        data = self.cleaned_data['grad_date']
        if not self.cleaned_data['is_high_school'] and not data:
            raise forms.ValidationError('Please enter your graduation date.')

        return data


class ApplicationSearchForm(forms.Form):
    # User related
    first_name = forms.CharField(label='First name', max_length=255)
    last_name = forms.CharField(label='Last name', max_length=255)
    email = forms.CharField(label='Email', max_length=255)

    # Application
    school = forms.CharField(label='School/College', max_length=255)
    major = forms.CharField(label='Major', max_length=255)
    gender = forms.CharField(label='Gender pronouns', max_length=255)
    city = forms.CharField(label='From City', max_length=255)
    state = forms.CharField(label='From State', max_length=255)
    score_min = forms.IntegerField(label='Score Starts at')
    score_max = forms.IntegerField(label='Score Ends at')
    is_minor = forms.BooleanField(label='Minors')
    is_veteran = forms.BooleanField(label='Veteran hackers')
    is_beginner = forms.BooleanField(label='Beginner hackers')
    is_non_UM = forms.BooleanField(label='Non-UMich hackers')
    limit = forms.CharField(label='Number of results', max_length=255)


class MentorApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MentorApplicationForm, self).__init__(*args, **kwargs)
        self.fields['agree_tc'].required = True

        self.fields['first_time_mentor'].short = True
        self.fields['mentorship_ideas'].skills = True
        self.fields['github'].commit = True

    class Meta:
        from application_lists import SKILLS
        model = MentorApplication

        # use all fields except for these
        exclude = ['user', 'submitted', 'deleted', 'score', 'reimbursement', 'decision']

        labels = {
            'first_time_mentor': 'I am a first time mentor!',
            'what_importance': 'What do you think is important about being a mentor?',
            'why_mentor': 'Why do you want to be a mentor?',
            'mentorship_ideas': 'Do you have any ideas for mentorship at MHacks?',
            'skills': 'What skills are you comfortable mentoring in? (CTRL/CMD + click to select multiple options!)',
            'other_skills': '',
            'github': '',
            'agree_tc': 'I understand that by committing to mentor at MHacks 8 during the weekend of October 7-9, 2016, I will not work on my own project and will help participants to the best of my ability.'
        }

        widgets = {
            'skills': ArrayFieldSelectMultiple(attrs={'class': 'full checkbox-style textfield check-width'}, choices=zip(SKILLS, SKILLS)),
            'other_skills': forms.TextInput(attrs={'class': 'check-width', 'placeholder': 'Other skills'}),
            'github': forms.TextInput(attrs={'class': 'check-width', 'placeholder': 'GitHub (optional)'}),
            'why_mentor': forms.Textarea(attrs={'class': 'textfield form-control'}),
            'mentorship_ideas': forms.Textarea(attrs={'class': 'textfield form-control'}),
            'what_importance': forms.Textarea(attrs={'class': 'textfield form-control'})
        }

    # custom validator for urls
    def clean_github(self):
        data = self.cleaned_data['github']
        validate_url(data, 'github.com')
        return data

    def clean_agree_tc(self):
        data = self.cleaned_data['agree_tc']
        if not data:
            raise forms.ValidationError('You must agree to the terms & conditions to continue.')
        return data


class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(RegistrationForm, self).__init__(*args, **kwargs)

    class Meta:
        from application_lists import TECH_OPTIONS, EMPLOYMENT_SKILLS
        model = Registration

        # use all fields except for these
        exclude = ['user', 'submitted', 'deleted']

        labels = {
            'acceptance': 'Do you accept your invitation to attend MHacks 8 this fall?',
            'transportation': 'How do you plan on getting to MHacks 8?',
            'want_help': 'What areas would you like to have help in? (CTRL/CMD + click to select multiple options!)',
            'other_want_help': '',
            'can_help': 'What areas can you mentor another hacker in? (CTRL/CMD + click to select multiple options!)',
            'other_can_help': '',
            't_shirt_size': 'Please select your T-shirt size:',
            'dietary_restrictions': 'Please select any dietary restrictions:',
            'accommodations': 'Would you need any accommodations?',
            'medical_concerns': 'Do you have any medical concerns that we should be aware of?',
            'phone_number': 'Please enter your phone number below:',
            'degree': 'What degree are you currently pursuing?',
            'employment': 'What types of employment are you interested in?',
            'technical_skills': 'Please select any technical skills you are competent in:',
            'code_of_conduct': mark_safe('I have read and agree to the terms of the <a href="https://drive.google.com/a/umich.edu/file/d/0B5_voCkrKbNTVllEckF5UHpYZk0/view">MHacks Code of Conduct</a>'),
            'waiver_signature': mark_safe('By signing below, I indicate my acceptance of the terms stated in the <a href="https://drive.google.com/a/umich.edu/file/d/0B5_voCkrKbNTX0c3NjUzV1F2WTQ/view">Accident Waiver and Release of Liability Form</a>'),
            'mlh_code_of_conduct': mark_safe('We participate in Major League Hacking (MLH) as a MLH Member Event. You authorize us to share certain application/registration information for event administration, ranking, MLH administration, pre and post-event informational e-mails, and occasional messages about hackathons in line with the MLH Privacy Policy. <br><br> I have read and agree to the terms of the <a href="https://static.mlh.io/docs/mlh-code-of-conduct.pdf">MLH Code of Conduct</a>')
        }

        widgets = {
            'want_help': ArrayFieldSelectMultiple(attrs={'class': 'full checkbox-style textfield check-width'},
                                                  choices=TECH_OPTIONS),
            'other_want_help': forms.TextInput(attrs={'class': 'check-width', 'placeholder': 'Other areas'}),
            'can_help': ArrayFieldSelectMultiple(attrs={'class': 'full checkbox-style textfield check-width'},
                                                 choices=TECH_OPTIONS),
            'other_can_help': forms.TextInput(attrs={'class': 'check-width', 'placeholder': 'Other areas'}),
            'technical_skills': ArrayFieldSelectMultiple(attrs={'class': 'full checkbox-style textfield check-width'},
                                                         choices=zip(EMPLOYMENT_SKILLS, EMPLOYMENT_SKILLS)),
            'accommodations': forms.Textarea(attrs={'class': 'textfield form-control', 'placeholder': '(e.g. wheelchair accessible transportation, closed captioning, etc.)'}),
            'medical_concerns': forms.Textarea(attrs={'class': 'textfield form-control', 'placeholder': '(e.g. asthma, diabetes, epilepsy, etc.)'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+##########'}),
            'waiver_signature': forms.TextInput(attrs={'class': 'check-width', 'placeholder': 'First Last'})
        }

    def clean_waiver_signature(self):
        data = self.cleaned_data['waiver_signature']
        print(data)
        user = self.user
        if not data:
            raise forms.ValidationError('You must sign the Accident Waiver and Release of Liability Form')
        if user.get_full_name() != data.strip().lower():
            raise forms.ValidationError('Please sign your name as it appears in your user account: {}'.format(user.get_full_name()))
        return data

    def clean_code_of_conduct(self):
        data = self.cleaned_data['code_of_conduct']
        if not data:
            raise forms.ValidationError('You must agree to the MHacks Code of Conduct.')
        return data

    def clean_mlh_code_of_conduct(self):
        data = self.cleaned_data['mlh_code_of_conduct']
        if not data:
            raise forms.ValidationError('You must agree to the MLH Code of Conduct.')
        return data
