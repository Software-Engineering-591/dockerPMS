from django import forms
from backend.models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message_text']
        widgets = {
            'message_text': forms.Textarea(attrs={'class' : 'w-full h-1/2 rounded bg-gray-400 text-black mt-20 ' }),
        }

