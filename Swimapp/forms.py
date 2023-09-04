from django import forms
from django.contrib.auth import authenticate
from multiupload.fields import MultiFileField

from .models import *


class SwimmingSpotForm(forms.ModelForm):
    images = MultiFileField(min_num=1, max_num=10,
                            max_file_size=1024 * 1024 * 5)  # Adjust max_num and max_file_size as needed

    class Meta:
        model = SwimmingSpot
        fields = ['title', 'description', 'longitude', 'latitude', 'category', 'average_temperature']


class CommentForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Comment
        fields = ['text', 'image']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Leave a comment...',
                'rows': 4,  # Adjust the number of rows
                'cols': 60,
            }),
        }
        labels = {
            'text': '',  # Set the label to an empty string
        }


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']

        labels = {
            'image': '',
        }


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label=False,
        widget=forms.TextInput(attrs={'placeholder': 'Username / Email'})
    )
    password = forms.CharField(
        label=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get("username_or_email")
        password = cleaned_data.get("password")

        if username_or_email and password:
            # Try authenticating the user using both username and email
            user = authenticate(
                self.request,
                username=username_or_email,
                password=password
            )

            if user is None:
                # Authentication failed, raise a validation error
                raise forms.ValidationError("username or password incorrect")

            # Authentication succeeded, attach the authenticated user to the form
            self.user = user

        return cleaned_data


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label=False  # Remove the label
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        label=False  # Remove the label
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''

        placeholders = {
            'username': 'Username',
            'email': 'Email',
            'first_name': 'First Name',
        }

        for field_name, placeholder in placeholders.items():
            self.fields[field_name].widget.attrs['placeholder'] = placeholder
            self.fields[field_name].label = False

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already exists')
        return data

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).exists():
            raise forms.ValidationError('Username already exists')
        return data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False

    def clean_email(self):
        data = self.cleaned_data['email']

        if data:
            qs = User.objects.exclude(id=self.instance.id).filter(email=data)
            if qs.exists():
                raise forms.ValidationError('Email already exists')

        return data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ('email',)
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email address',
            }),
        }


class PaymentForm(forms.Form):
    stripe_token = forms.CharField(widget=forms.HiddenInput(), required=False)
    card_number = forms.CharField(
        label='Card Number',
        widget=forms.TextInput(attrs={'placeholder': 'Card number'}),
        required=True
    )

    expiration_date = forms.CharField(
        label='Expiration Date',
        widget=forms.TextInput(attrs={'placeholder': 'MM / YY'}),
        required=True
    )

    cvc = forms.CharField(
        label='CVC',
        widget=forms.TextInput(attrs={'placeholder': 'CVC'}),
        required=True
    )
