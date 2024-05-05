from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from backend.models import Message
from django.http import request


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message_text']
        widgets = {
            'message_text': forms.Textarea(
                attrs={
                    'class': 'w-full h-full base-100 text-base-content textarea textarea-bordered',
                    'placeholder': 'Send a message...',
                    'id': 'msgTextArea',
                }
            ),
        }


class QuoteForm(forms.Form):
    date_from = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
    )
    time_from = forms.TimeField(
        widget=forms.widgets.TimeInput(attrs={'type': 'time'})
    )
    date_to = forms.DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
    )
    time_to = forms.TimeField(
        widget=forms.widgets.TimeInput(attrs={'type': 'time'})
    )

    def clear_quote_form(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('dateFrom')
        time_from = cleaned_data.get('timeFrom')
        date_to = cleaned_data.get('dateTo')
        time_to = cleaned_data.get('timeTo')

        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError(
                    'A departure date must be after the arrival date'
                )
            elif date_to == date_from and time_to <= time_from:
                raise ValidationError(
                    'A departure time must be after the arrival time on the same date'
                )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Your new firstname'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Your new lastname'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your new email'})
        }


# class Password