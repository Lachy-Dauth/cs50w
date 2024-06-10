from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.utils import timezone
from datetime import timedelta

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class BetForm(forms.ModelForm):
    hours_from_now = forms.IntegerField(label="End Time (Hours from now)", min_value=1, initial=24)

    class Meta:
        model = Bet
        fields = ['name', 'description', 'reserve']

    def save(self, commit=True):
        bet = super().save(commit=False)
        hours = self.cleaned_data['hours_from_now']
        bet.end_time = timezone.now() + timedelta(hours=hours)
        if commit:
            bet.save()
        return bet

class BetOptionForm(forms.ModelForm):
    class Meta:
        model = BetOption
        fields = ['name']