from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  ,Student

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    register_number = forms.CharField(max_length=12, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role','register_number')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())
 
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'year', 'degree_department', 'date_of_birth',
                  'sex', 'linkedin_link', 'github_link', 'website_link', 'profile_image',
                  'phone', 'email', 'about']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'degree_department': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sex': forms.Select(attrs={'class': 'form-control'}),
            'linkedin_link': forms.URLInput(attrs={'class': 'form-control'}),
            'github_link': forms.URLInput(attrs={'class': 'form-control'}),
            'website_link': forms.URLInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

        