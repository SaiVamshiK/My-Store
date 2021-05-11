from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email=forms.EmailField()
    class Meta:
        model = User
        fields=['username','email','password1','password2']



class ReviewForm(forms.Form):
    review=forms.CharField()
    rating=forms.FloatField()
    class Meta:
        fields = ['review','rating']


class CustomReviewForm(forms.Form):
    sound=forms.CharField()
    rating=forms.FloatField()
    class Meta:
        fields=['sound','rating']






