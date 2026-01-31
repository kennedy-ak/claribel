from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Organization, MentorAssignment


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
