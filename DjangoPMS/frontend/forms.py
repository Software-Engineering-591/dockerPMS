from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import datetime

from backend.models import Message, ParkingLot
from leaflet.forms.widgets import LeafletWidget


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

    def check(self):
        date_from = self.cleaned_data.get('date_from')
        time_from = self.cleaned_data.get('time_from')
        date_to = self.cleaned_data.get('date_to')
        time_to = self.cleaned_data.get('time_to')
        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError(
                    'A departure date must be after the arrival date'
                )
            elif date_to == date_from and time_to <= time_from:
                raise ValidationError(
                    'A departure time must be after the arrival time on the same date'
                )
            elif (date_to - date_from) > datetime.timedelta(days=10):
                raise ValidationError(
                    'A departure cannot be more than 10 days in length'
                )


class TopUpForm(forms.Form):
    amount = forms.IntegerField(
        max_value=10000,
        widget=forms.NumberInput(
            attrs={'id': 'credits', 'class': 'input input-bordered w-full'}
        ),
    )
    card_number = forms.IntegerField(
        max_value=9999999999999999,
        min_value=0,
        widget=forms.NumberInput(
            attrs={'class': 'input input-bordered w-full'}
        ),
    )
    card_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )
    expiry = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'MM/YY',
                'type': 'month',
            }
        ),
        input_formats=['%Y-%m'],
    )
    cvc = forms.IntegerField(
        max_value=999,
        widget=forms.NumberInput(
            attrs={'class': 'input input-bordered w-full'}
        ),
    )

    def clean_expiry(self):
        expiry = self.cleaned_data.get('expiry')
        if expiry and expiry < datetime.date.today():
            raise ValidationError('The expiry date has passed.')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)


class ParkingLotForm(forms.ModelForm):
    class Meta:
        model = ParkingLot
        fields = ('name', 'poly')
        widgets = {'poly': LeafletWidget()}
