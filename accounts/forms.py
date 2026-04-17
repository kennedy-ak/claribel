from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile, Organization, MentorAssignment, TaskAssignment, Meeting


class RegistrationForm(UserCreationForm):
    """Enhanced registration form with role selection and organization code."""
    ROLE_CHOICES = [
        ('mentee', 'Mentee'),
        ('mentor', 'Mentor')
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='I want to join as:'
    )

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        label='Phone Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0201234567 or +233201234567'
        }),
        help_text='Optional: Enter your Ghanaian phone number to receive SMS notifications (format: 02XXXXXXXXX or +233XXXXXXXXX)'
    )

    sms_notifications_enabled = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Enable SMS Notifications'
    )

    join_code = forms.CharField(
        max_length=8,
        required=False,
        label='Organization Join Code (for Mentees)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 8-character code (e.g., ABC12345)',
            'style': 'text-transform: uppercase;'
        }),
        help_text='Ask your organization administrator for the join code. Leave empty if you don\'t have one yet.'
    )

    # Organization fields for mentors
    org_name = forms.CharField(
        max_length=200,
        required=False,
        label='Organization Name (for Mentors)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter organization name'
        }),
        help_text='Create a new organization if you\'re a mentor. Leave empty if you don\'t want to create one.'
    )

    org_description = forms.CharField(
        max_length=500,
        required=False,
        label='Organization Description (for Mentors)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Brief description of your organization'
        }),
        help_text='Optional: Provide a description for your organization.'
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

        if not getattr(settings, 'ALLOW_MENTOR_REGISTRATION', True):
            del self.fields['role']
            del self.fields['org_name']
            del self.fields['org_description']


class OrganizationForm(forms.ModelForm):
    """Form for creating a new organization."""

    class Meta:
        model = Organization
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter organization name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of your organization'
            })
        }


class MentorAssignmentForm(forms.Form):
    """Form for assigning a mentee to a mentor."""

    mentor = forms.ModelChoiceField(
        queryset=None,
        empty_label="Select a mentor",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Assign to Mentor'
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Reason for assignment or reassignment (optional)'
        }),
        label='Notes'
    )

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)

        if organization:
            # Only show mentors from this organization
            self.fields['mentor'].queryset = organization.get_mentors()


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information."""

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'sms_notifications_enabled', 'email_notifications_enabled', 'bio']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 0201234567 or +233201234567'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us about yourself'
            })
        }
        labels = {
            'phone_number': 'Phone Number (for SMS notifications)',
            'sms_notifications_enabled': 'Enable SMS Notifications',
            'email_notifications_enabled': 'Enable Email Notifications',
            'bio': 'Bio'
        }
        help_texts = {
            'phone_number': 'Enter your Ghanaian phone number (format: 02XXXXXXXXX or +233XXXXXXXXX)',
            'sms_notifications_enabled': 'Receive SMS notifications for important updates',
            'email_notifications_enabled': 'Receive email notifications for important updates'
        }


class TaskAssignmentForm(forms.ModelForm):
    """Form for mentors to create task assignments for mentees."""

    class Meta:
        model = TaskAssignment
        fields = ['mentee', 'title', 'description', 'priority', 'due_date', 'notes']
        widgets = {
            'mentee': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed task description'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional notes or instructions'
            })
        }
        labels = {
            'mentee': 'Assign to Mentee',
            'title': 'Task Title',
            'description': 'Task Description',
            'priority': 'Priority Level',
            'due_date': 'Due Date',
            'notes': 'Mentor Notes'
        }
        help_texts = {
            'due_date': 'Set a deadline for task completion'
        }

    def __init__(self, *args, **kwargs):
        mentor = kwargs.pop('mentor', None)
        super().__init__(*args, **kwargs)

        if mentor:
            # Only show mentees assigned to this mentor
            mentees = mentor.profile.get_mentees()
            self.fields['mentee'].queryset = User.objects.filter(
                profile__in=mentees
            )


class TaskUpdateForm(forms.ModelForm):
    """Form for mentees to update task status."""

    class Meta:
        model = TaskAssignment
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add progress notes or comments'
            })
        }
        labels = {
            'status': 'Task Status',
            'notes': 'Progress Notes'
        }


class MeetingForm(forms.ModelForm):
    """Form for mentors to schedule Google Meet meetings with mentees."""

    class Meta:
        model = Meeting
        fields = ['mentee', 'title', 'description', 'start_time', 'end_time', 'google_meet_url', 'notes']
        widgets = {
            'mentee': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Meeting title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Meeting agenda and description'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'google_meet_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://meet.google.com/xxx-xxxx-xxx'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional meeting notes'
            })
        }
        labels = {
            'mentee': 'Schedule with Mentee',
            'title': 'Meeting Title',
            'description': 'Meeting Description',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'google_meet_url': 'Google Meet URL',
            'notes': 'Meeting Notes'
        }
        help_texts = {
            'google_meet_url': 'Paste the Google Meet link here for easy joining',
            'start_time': 'Meeting start date and time',
            'end_time': 'Meeting end date and time'
        }

    def __init__(self, *args, **kwargs):
        mentor = kwargs.pop('mentor', None)
        super().__init__(*args, **kwargs)

        if mentor:
            # Only show mentees assigned to this mentor
            mentees = mentor.profile.get_mentees()
            self.fields['mentee'].queryset = User.objects.filter(
                profile__in=mentees
            )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError('End time must be after start time')

            # Check if start time is in the past
            from django.utils import timezone
            if start_time < timezone.now():
                raise forms.ValidationError('Cannot schedule meetings in the past')

        return cleaned_data
