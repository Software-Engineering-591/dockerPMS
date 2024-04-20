from django import forms
from django.core.exceptions import ValidationError


class QuoteForm(forms.Form):
    # dateFrom = forms.DateField(required=True, label='Arrival date')
    # timeFrom = forms.TimeField(required=True, label='Arrival time')
    # dateTo = forms.DateField(required=True, label='Departure date')
    # timeTo = forms.TimeField(required=True, label='Departure time')
    dateFrom = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    timeFrom = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'type': 'time'}))
    dateTo = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    timeTo = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'type': 'time'}))

    def cleanQuoteFrom(self):

        cleaned_data = super().clean()
        dateFrom = cleaned_data.get("dateFrom")
        timeFrom = cleaned_data.get("timeFrom")
        dateTo = cleaned_data.get("dateTo")
        timeTo = cleaned_data.get("timeTo")

        if dateFrom and dateTo:
            if dateTo < dateFrom:
                raise ValidationError("A departure date must be after the arrival date")
            elif dateTo == dateFrom and timeTo <= timeFrom:
                raise ValidationError("A departure time must be after the arrival time on the same date")
