from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import datetime
from backend.models import Message, User
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


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)


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

        
class TopUpForm(forms.Form):

    amount = forms.IntegerField(
        max_value = 10000,
        required = True,
        widget = forms.NumberInput(attrs={'id' : 'credits', 'class': 'input input-bordered w-full'})
    )
    card_number = forms.IntegerField(
        max_value=9999999999999999,  # Typical length for credit card numbers
        min_value=0000000000000,  # Minimum length to cover most card types
        required=True,
        widget=forms.NumberInput(attrs={'class': 'input input-bordered w-full'})
    )
    card_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'})
    )
    expiry = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'MM/YY', 'type' : 'month'}),
        input_formats=['%Y-%m']
    )
    cvc = forms.IntegerField(
        max_value= 999,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'input input-bordered w-full'})
    )

    def clean_expiry(self):
        expiry = self.cleaned_data.get('expiry')
        if expiry and expiry < datetime.date.today():
            raise ValidationError("The expiry date has passed.")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

