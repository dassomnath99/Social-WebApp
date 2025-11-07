from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment, Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username','email','password1','password2')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content','image']
        widgets = {
            'content':forms.Textarea(attrs={'rows':3,'placeholder':"what's on your mind?"}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content':forms.TextInput(attrs={'placeholder':'Add a Comment...'})
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio','avatar']
    