from django import forms
from django.core.exceptions import ValidationError
import datetime
from backend.models import Message

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


class TopUpForm(forms.Form):
    email = forms.EmailField(
        label='Confirmation will be sent to',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'input input-bordered w-full'})
    )
    card_number = forms.CharField(
        label='Card number',
        max_length=16,  # Typical length for credit card numbers
        min_length=13,  # Minimum length to cover most card types
        required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    name_on_card = forms.CharField(
        label='Name on card',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    expiry = forms.DateField(
        label='Expiry date',
        required=True,
        widget=forms.DateInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'MM/YY'}),
        input_formats=['%m/%y']  # Accepting MM/YY format
    )
    cvc = forms.CharField(
        label='Security code',
        max_length=4,  # CVC codes are usually 3 or 4 digits
        min_length=3,
        required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )

    def clean_expiry(self):
        expiry = self.cleaned_data.get('expiry')
        if expiry and expiry < datetime.date.today():
            raise ValidationError("The expiry date has passed.")
        return expiry

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # You can add more validation to check if email is associated with a user etc.
        return email



