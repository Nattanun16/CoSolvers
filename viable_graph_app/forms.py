# forms.py
from django import forms


class LoginForm(forms.Form):
    student_id = forms.CharField(label="Student ID")
    password = forms.CharField(widget=forms.PasswordInput)
